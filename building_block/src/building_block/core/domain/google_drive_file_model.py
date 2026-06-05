"""Google Drive file model."""

from bson import ObjectId
from building_block.shared.enum import FileSource
from building_block.core.domain.file_model import FileModel as BaseFileModel
from pydantic import Field
from typing import Optional


class GoogleDriveFile(BaseFileModel):
    """FileModel for Google Drive sources."""

    original: FileSource = Field(
        default=FileSource.GOOGLE_DRIVE, description="File source"
    )
    drive_file_id: str = Field(..., description="Google Drive internal file ID")
    mime_type: str = Field(..., description="File MIME type")
    size_bytes: Optional[int] = Field(default=None, description="File size in bytes")

    @classmethod
    def _to_model(cls, doc: dict) -> "GoogleDriveFile":
        """Build model from canonical GoogleDriveFile fields."""
        doc["file_id"] = str(_id) if (_id := doc.pop("_id", None)) is not None else None
        return cls(**doc)

    def _to_doc(self) -> dict:
        document: dict = self.model_dump()
        file_id = document.pop("file_id", None)
        if file_id is not None:
            document["_id"] = ObjectId(file_id)
        return document
