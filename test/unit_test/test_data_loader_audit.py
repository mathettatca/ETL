from datetime import datetime
from types import SimpleNamespace

import pytest

from data_access.application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
)
from building_block.core.domain.file_model import FileDownloadStatus, FileModel, FileSource
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from data_loader import entrypoints


class FakeDispatcher:
    responses: list[FileModel] = []

    def get_file_info(self, source: FileSource, **kwargs):
        return SimpleNamespace(original=source)

    def download(self, file, dest_path: str, **kwargs) -> list[FileModel]:
        return self.responses


class FakeMediator:
    def __init__(self, fail_all: bool = False, fail_first: bool = False):
        self.fail_all = fail_all
        self.fail_first = fail_first
        self.sent: list[AuditFileDownloadCommand] = []

    def send(self, command: AuditFileDownloadCommand):
        self.sent.append(command)
        if self.fail_all or (self.fail_first and len(self.sent) == 1):
            raise RuntimeError("audit failed")
        return None


def build_response(
    file_id: str = "drive-file-id",
    file_name: str = "audit.csv",
    mime_type: str = "text/csv",
    dest_path: str | None = "/tmp/audit.csv",
) -> GoogleDriveFile:
    return GoogleDriveFile(
        name=file_name,
        date_create=datetime(2026, 6, 7, 0, 0, 0),
        date_download=datetime(2026, 6, 7, 1, 0, 0),
        dest_path=dest_path,
        download_status=FileDownloadStatus.SUCCESS,
        drive_file_id=file_id,
        mime_type=mime_type,
        size_bytes=2048,
    )


def patch_loader(monkeypatch, responses: list[FileModel], mediator: FakeMediator):
    FakeDispatcher.responses = responses
    mediator_calls = []

    def fake_mediator():
        mediator_calls.append(True)
        return mediator

    monkeypatch.setattr(entrypoints, "DownloaderDispatcher", FakeDispatcher)
    monkeypatch.setattr(entrypoints, "Mediator", fake_mediator)
    return mediator_calls


def test_run_data_loader_sends_audit_command_for_each_response(monkeypatch):
    responses = [
        build_response(file_id="drive-file-1", file_name="a.csv"),
        build_response(file_id="drive-file-2", file_name="b.csv"),
    ]
    mediator = FakeMediator()
    mediator_calls = patch_loader(monkeypatch, responses, mediator)

    result = entrypoints.run_data_loader(
        file_source="google_drive",
        dest_path="/tmp",
        file_id="folder-id",
    )

    assert len(mediator_calls) == 1
    assert len(mediator.sent) == 2
    assert result == responses

    first = mediator.sent[0]
    assert isinstance(first, AuditFileDownloadCommand)
    assert first.file_name == "a.csv"
    assert first.file_local_path == "/tmp/audit.csv"
    assert first.file_source == FileSource.GOOGLE_DRIVE
    assert first.download_status == FileDownloadStatus.SUCCESS
    assert first.size == 2048
    assert first.model_extra["drive_file_id"] == "drive-file-1"
    assert first.model_extra["mime_type"] == "text/csv"


def test_run_data_loader_returns_when_audit_partially_fails(monkeypatch):
    responses = [
        build_response(file_id="drive-file-1", file_name="a.csv"),
        build_response(file_id="drive-file-2", file_name="b.csv"),
    ]
    mediator = FakeMediator(fail_first=True)
    patch_loader(monkeypatch, responses, mediator)

    result = entrypoints.run_data_loader(
        file_source="google_drive",
        dest_path="/tmp",
        file_id="folder-id",
    )

    assert len(mediator.sent) == 2
    assert result == responses


def test_run_data_loader_raises_when_all_audits_fail(monkeypatch):
    responses = [
        build_response(file_id="drive-file-1", file_name="a.csv"),
        build_response(file_id="drive-file-2", file_name="b.csv"),
    ]
    mediator = FakeMediator(fail_all=True)
    patch_loader(monkeypatch, responses, mediator)

    with pytest.raises(RuntimeError, match="All file download audit commands failed"):
        entrypoints.run_data_loader(
            file_source="google_drive",
            dest_path="/tmp",
            file_id="folder-id",
        )

    assert len(mediator.sent) == 2


def test_run_data_loader_rejects_missing_audit_metadata(monkeypatch):
    mediator = FakeMediator()
    patch_loader(monkeypatch, [build_response(dest_path=None)], mediator)

    with pytest.raises(ValueError, match="dest_path is required"):
        entrypoints.run_data_loader(
            file_source="google_drive",
            dest_path="/tmp",
            file_id="folder-id",
        )
