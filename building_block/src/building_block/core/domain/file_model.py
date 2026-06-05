"""Base file model for all file types in the system."""

from pydantic import ConfigDict, Field
from datetime import datetime

from building_block.core.base.base_model import CustomBaseModel
from building_block.shared.enum import FileDownloadStatus, FileSource


class FileModel(CustomBaseModel):
    """
    Base model for all file types in the system.
    Only uses Pydantic — does not import any infrastructure libraries.
    This is a Value Object with immutable behavior.
    """

    file_id: str | None = Field(default=None, description="Unique file identifier")
    name: str = Field(..., description="File name")
    date_create: datetime = Field(..., description="Creation date from source")
    date_download: datetime | None = Field(
        default=None, description="Download timestamp"
    )
    dest_path:str | None = Field(
        default= None, description="Local path"
    )
    original: FileSource = Field(..., description="Source of the file")
    download_status:FileDownloadStatus = FileDownloadStatus.PENDING

    model_config = ConfigDict(
        frozen=True,  # Immutable — Value Object behavior
        json_schema_extra={
            "example": {
                "file_id": "file_123",
                "name": "document.pdf",
                "date_create": "2024-01-01T00:00:00",
                "date_download": "2024-01-02T12:30:00",
                "original": "google_drive",
            }
        },
    )
