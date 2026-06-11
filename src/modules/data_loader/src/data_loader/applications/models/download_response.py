"""Download response DTO."""

from pydantic import Field

from building_block.core.base.base_model import CustomBaseModel
from building_block.core.domain.file_model import FileDownloadStatus


class DownloadResponse(CustomBaseModel):
    """Response returned after a file download attempt."""

    id: str = Field(..., description="File ID from database/source")
    file_path: str = Field(..., description="Local file path after download")
    file_download_status: FileDownloadStatus = Field(
        ..., description="Download status"
    )
    file_name: str | None = Field(default=None, description="Downloaded file name")
    mime_type: str | None = Field(default=None, description="Downloaded file MIME type")
    size: int | None = Field(default=None, description="Downloaded file size in bytes")

    @classmethod
    def _to_model(cls, doc: dict) -> "DownloadResponse":
        return cls(
            id=doc.get("id", doc.get("file_id", "")),
            file_path=doc.get("file_path", doc.get("local_path", "")),
            file_download_status=doc.get(
                "file_download_status",
                FileDownloadStatus.PENDING,
            ),
            file_name=doc.get("file_name"),
            mime_type=doc.get("mime_type"),
            size=doc.get("size", doc.get("size_bytes")),
        )

    def _to_doc(self) -> dict:
        return {
            "id": self.id,
            "file_id": self.id,
            "local_path": self.file_path,
            "file_download_status": self.file_download_status.value,
        }
