"""API file model."""

from building_block.shared.enum import FileSource
from building_block.core.domain.file_model import FileModel as BaseFileModel
from pydantic import Field
from typing import Optional


class ApiFile(BaseFileModel):
    """FileModel for API/HTTP sources."""

    original: FileSource = Field(default=FileSource.API, description="File source")
    endpoint_url: str = Field(..., description="API endpoint URL")
    response_code: Optional[int] = Field(default=None, description="HTTP response code")
    content_type: Optional[str] = Field(default=None, description="Content-Type header")
    request_params: dict = Field(default_factory=dict, description="Request parameters")
