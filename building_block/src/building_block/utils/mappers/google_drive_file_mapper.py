from typing import Any

from bson import ObjectId

from building_block.core.domain.file_model import FileDownloadStatus
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.utils.logging import log_error


class GoogleDriveFileMapper:
    @staticmethod
    def to_model(doc: dict) -> GoogleDriveFile:
        drive_file_id = doc.get("id", doc.get("drive_file_id", None))
        if drive_file_id is None:
            log_error(f"drive_file_id is missing in doc: {doc}")

        created_time = doc.get("createdTime", doc.get("date_create", None))
        date_create = (
            created_time.replace("+00:00", "Z")
            if isinstance(created_time, str)
            else created_time
        )

        temp_id = doc.get("_id", doc.get("file_id", None))
        file_id = str(temp_id) if temp_id is not None else None

        size = doc.get("size", doc.get("size_bytes"))
        try:
            size_bytes = int(size) if size is not None else None
        except Exception:
            log_error(f"Invalid size value: {size}")
            size_bytes = None

        try:
            return GoogleDriveFile(
                file_id=file_id,
                name=doc["name"],
                date_create=date_create,
                date_download=doc.get("date_download"),
                dest_path=doc.get("dest_path", None),
                original=doc.get("original", "google_drive"),
                drive_file_id=drive_file_id,
                mime_type=doc.get("mimeType", doc.get("mime_type", "")),
                size_bytes=size_bytes,
                download_status=doc.get(
                    "download_status",
                    FileDownloadStatus.PENDING,
                ),
            )
        except Exception as e:
            log_error(f"Failed to build GoogleDriveFile: {e} | doc={doc}")
            raise

    @classmethod
    def to_doc(cls, file: GoogleDriveFile) -> dict:
        doc = {
            "name": file.name,
            "date_create": file.date_create,
            "date_download": file.date_download,
            "dest_path": file.dest_path,
            "original": file.original.value,
            "drive_file_id": file.drive_file_id,
            "mime_type": file.mime_type,
            "size_bytes": file.size_bytes,
            "download_status": file.download_status,
        }

        if file.file_id is not None:
            doc["_id"] = cls.to_object_id(file.file_id)

        return doc

    @staticmethod
    def to_object_id(value: Any) -> Any:
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        return value
