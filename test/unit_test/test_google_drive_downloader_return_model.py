from datetime import datetime
from pathlib import Path

from building_block.core.domain.file_model import FileDownloadStatus
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from data_loader.applications.services.downloaders.adapters import google_drive_downloader
from data_loader.applications.services.downloaders.adapters.google_drive_downloader import (
    GoogleDriveDownloader,
)


class FakeGoogleDriveService:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def download_file(self, drive_file_id: str, local_path: str) -> str:
        if self.fail:
            raise RuntimeError("download failed")
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        Path(local_path).touch()
        return local_path


def build_google_drive_file() -> GoogleDriveFile:
    return GoogleDriveFile(
        name="audit.csv",
        date_create=datetime(2026, 6, 7, 0, 0, 0),
        drive_file_id="drive-file-id",
        mime_type="text/csv",
        size_bytes=2048,
    )


def build_downloader(service: FakeGoogleDriveService) -> GoogleDriveDownloader:
    downloader = GoogleDriveDownloader.__new__(GoogleDriveDownloader)
    downloader.service = service
    return downloader


def test_downloader_initializes_service_from_bootstrap(monkeypatch):
    drive_client = object()
    wrapper_calls = []

    class FakeServiceWrapper:
        def __init__(self, service):
            wrapper_calls.append(service)
            self.service = service

    monkeypatch.setattr(
        google_drive_downloader,
        "initialize_google_drive_service",
        lambda: drive_client,
    )
    monkeypatch.setattr(
        google_drive_downloader,
        "GoogleDriveService",
        FakeServiceWrapper,
    )

    downloader = GoogleDriveDownloader()

    assert wrapper_calls == [drive_client]
    assert downloader.service.service is drive_client


def test_download_handler_returns_success_model_when_file_is_new(tmp_path):
    downloader = build_downloader(FakeGoogleDriveService())
    responses: list[GoogleDriveFile] = []

    result = downloader._download_handler(
        build_google_drive_file(),
        str(tmp_path / "audit.csv"),
        responses,
    )

    assert result is not None
    assert responses == [result]
    assert result.dest_path == str(tmp_path / "audit.csv")
    assert result.download_status == FileDownloadStatus.SUCCESS
    assert result.date_download is not None
    assert result.date_update is None


def test_download_handler_returns_update_model_when_file_exists(tmp_path):
    local_path = tmp_path / "audit.csv"
    local_path.touch()
    downloader = build_downloader(FakeGoogleDriveService())
    responses: list[GoogleDriveFile] = []

    result = downloader._download_handler(
        build_google_drive_file(),
        str(local_path),
        responses,
    )

    assert result is not None
    assert responses == [result]
    assert result.dest_path == str(local_path)
    assert result.download_status == FileDownloadStatus.UPDATE
    assert result.date_download is None
    assert result.date_update is not None


def test_download_handler_returns_failed_model_when_download_raises(tmp_path):
    downloader = build_downloader(FakeGoogleDriveService(fail=True))
    responses: list[GoogleDriveFile] = []

    result = downloader._download_handler(
        build_google_drive_file(),
        str(tmp_path / "audit.csv"),
        responses,
    )

    assert result is not None
    assert responses == [result]
    assert result.dest_path == str(tmp_path / "audit.csv")
    assert result.download_status == FileDownloadStatus.FAILED
    assert result.date_download is not None
    assert result.date_update is None
