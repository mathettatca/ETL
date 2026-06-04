"""Google Drive file model."""

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
        return cls(**doc)

    def _to_doc(self) -> dict:
        """Return canonical GoogleDriveFile fields."""
        return self.model_dump()
