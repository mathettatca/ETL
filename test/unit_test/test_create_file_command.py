from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "building_block" / "src"))

from building_block.shared.enum import FileSource
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from modules.data_access.application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
    AuditFileDownloadCommandHandler,
)


class FakeFileRepository:
    def __init__(self):
        self.inserted_models: list[GoogleDriveFile] = []
        self.existing_model: GoogleDriveFile | None = None
        self.updated_models: list[GoogleDriveFile] = []

    def get(self, **filter_options) -> GoogleDriveFile | None:
        return self.existing_model

    def insert_one(self, model: GoogleDriveFile) -> str:
        self.inserted_models.append(model)
        return "file-id-1"

    def update_one(self, model: GoogleDriveFile) -> bool:
        self.updated_models.append(model)
        return True


def insert_data() -> dict:
    return {
        "file_name": "audit.csv",
        "file_local_path": "/tmp/audit.csv",
        "file_source": "google_drive",
        "drive_file_id": "drive-file-id",
        "mime_type": "text/csv",
        "size": 2048,
        "download_status": "pending",
        "specs": {"source_folder_id": "folder-id"},
    }


def test_create_model():
    data = insert_data()
    request = AuditFileDownloadCommand._to_model(data)

    assert request.file_name == "audit.csv"
    assert request.file_local_path == "/tmp/audit.csv"
    assert request.file_source == FileSource.GOOGLE_DRIVE
    assert request.size == 2048
    assert request._to_doc() == {
        "file_name": "audit.csv",
        "file_local_path": "/tmp/audit.csv",
        "file_source": "google_drive",
        "size": 2048,
        "download_status": "pending",
    }


def test_create_gdrive_model_ggdrive_id_None():
    data = insert_data()
    data["drive_file_id"] = None
    repository = FakeFileRepository()
    handler = AuditFileDownloadCommandHandler.__new__(AuditFileDownloadCommandHandler)
    handler.mongo_repository = repository

    with pytest.raises(ValueError, match="drive_file_id is required"):
        handler.handle(AuditFileDownloadCommand(**data))


def test_create_model_from_legacy_gdrive_payload():
    data = insert_data()
    data["size_bytes"] = data.pop("size")

    request = AuditFileDownloadCommand(**data)

    assert request.file_source == FileSource.GOOGLE_DRIVE
    assert request.size is None
    assert request.model_extra["size_bytes"] == 2048


def test_insert_one_repository():
    data = insert_data()
    repository = FakeFileRepository()
    handler = AuditFileDownloadCommandHandler.__new__(AuditFileDownloadCommandHandler)
    handler.mongo_repository = repository

    response = handler.handle(AuditFileDownloadCommand(**data))

    assert response._to_doc() == {
        "status": "success",
        "message": "Import File Audit successfully",
        "status_code": 200,
    }
    assert len(repository.inserted_models) == 1

    inserted_model = repository.inserted_models[0]
    assert inserted_model.name == "audit.csv"
    assert inserted_model.dest_path == "/tmp/audit.csv"
    assert inserted_model.original == FileSource.GOOGLE_DRIVE
    assert inserted_model.drive_file_id == "drive-file-id"
    assert inserted_model.mime_type == "text/csv"
    assert inserted_model.size_bytes == 2048
    assert inserted_model.spec == {}
