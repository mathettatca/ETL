from datetime import datetime
from pathlib import Path
import sys

from bson import ObjectId


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "building_block" / "src"))

from building_block.shared.enum import FileSource
from building_block.core.domain.file_model import FileModel
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.infrastructure.mongo.base_mongo_repository import BaseMongoRepository


class FakeInsertOneResult:
    inserted_id = "file-id-1"


class FakeUpdateOneResult:
    modified_count = 1


class FakeCollection:
    def __init__(self):
        self.inserted_document: dict | None = None
        self.updated_filter: dict | None = None
        self.updated_payload: dict | None = None

    def insert_one(self, document: dict) -> FakeInsertOneResult:
        self.inserted_document = document
        return FakeInsertOneResult()

    def update_one(self, filter_options: dict, payload: dict) -> FakeUpdateOneResult:
        self.updated_filter = filter_options
        self.updated_payload = payload
        return FakeUpdateOneResult()


def insert_data() -> FileModel:
    return FileModel(
        name="audit.csv",
        date_create=datetime(2026, 6, 2, 10, 30, 0),
        dest_path="/tmp/audit.csv",
        original=FileSource.GOOGLE_DRIVE,
        spec={"drive_file_id": "drive-file-id"},
    )


def test_insert_one_repository():
    collection = FakeCollection()
    repository = BaseMongoRepository.__new__(BaseMongoRepository)
    repository.model = FileModel
    repository._get_collection = lambda: collection

    inserted_id = repository.insert_one(insert_data())

    assert inserted_id == "file-id-1"
    assert collection.inserted_document == {
        "file_id": None,
        "name": "audit.csv",
        "date_create": "2026-06-02T10:30:00",
        "date_download": None,
        "dest_path": "/tmp/audit.csv",
        "original": "google_drive",
        "download_status": "pending",
        "spec": {"drive_file_id": "drive-file-id"},
    }


def test_insert_one_google_drive_file_excludes_file_id():
    collection = FakeCollection()
    repository = BaseMongoRepository.__new__(BaseMongoRepository)
    repository.model = GoogleDriveFile
    repository._get_collection = lambda: collection

    repository.insert_one(
        GoogleDriveFile(
            name="audit.csv",
            date_create=datetime(2026, 6, 2, 10, 30, 0),
            dest_path="/tmp/audit.csv",
            original=FileSource.GOOGLE_DRIVE,
            drive_file_id="drive-file-id",
            mime_type="text/csv",
            size_bytes=2048,
        )
    )

    assert collection.inserted_document is not None
    assert "file_id" not in collection.inserted_document
    assert "_id" not in collection.inserted_document


def test_insert_one_google_drive_file_maps_file_id_to_object_id():
    collection = FakeCollection()
    repository = BaseMongoRepository.__new__(BaseMongoRepository)
    repository.model = GoogleDriveFile
    repository._get_collection = lambda: collection

    repository.insert_one(
        GoogleDriveFile(
            file_id="656f1f77bcf86cd799439011",
            name="audit.csv",
            date_create=datetime(2026, 6, 2, 10, 30, 0),
            dest_path="/tmp/audit.csv",
            original=FileSource.GOOGLE_DRIVE,
            drive_file_id="drive-file-id",
            mime_type="text/csv",
            size_bytes=2048,
        )
    )

    assert collection.inserted_document is not None
    assert "file_id" not in collection.inserted_document
    assert collection.inserted_document["_id"] == ObjectId("656f1f77bcf86cd799439011")


def test_google_drive_file_to_model_maps_object_id_to_file_id_string():
    model = GoogleDriveFile._to_model(
        {
            "_id": ObjectId("656f1f77bcf86cd799439011"),
            "name": "audit.csv",
            "date_create": datetime(2026, 6, 2, 10, 30, 0),
            "dest_path": "/tmp/audit.csv",
            "original": FileSource.GOOGLE_DRIVE,
            "drive_file_id": "drive-file-id",
            "mime_type": "text/csv",
            "size_bytes": 2048,
        }
    )

    assert model.file_id == "656f1f77bcf86cd799439011"


def test_update_one_google_drive_file_uses_model_file_id_without_setting_it():
    collection = FakeCollection()
    repository = BaseMongoRepository.__new__(BaseMongoRepository)
    repository.model = GoogleDriveFile
    repository._get_collection = lambda: collection

    result = repository.update_one(
        GoogleDriveFile(
            file_id="656f1f77bcf86cd799439011",
            name="audit.csv",
            date_create=datetime(2026, 6, 2, 10, 30, 0),
            dest_path="/tmp/audit.csv",
            original=FileSource.GOOGLE_DRIVE,
            drive_file_id="drive-file-id",
            mime_type="text/csv",
            size_bytes=2048,
        )
    )

    assert result is True
    assert collection.updated_filter is not None
    assert set(collection.updated_filter) == {"_id"}
    assert str(collection.updated_filter["_id"]) == "656f1f77bcf86cd799439011"
    assert collection.updated_payload is not None
    assert "file_id" not in collection.updated_payload["$set"]
