from typing import Any

from pydantic import ConfigDict

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.file_model import FileModel
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.infrastructure.mongo.base_mongo_repository import BaseMongoRepository
from building_block.shared.enum import FileDownloadStatus, FileSource

from .audit_file_download_command_response import AuditFileDownloadCommandResponse
from .handler.api_download_handler import AuditAPIFileDownloadHandler
from .handler.google_drive_download_handler import AuditGoogleDriveFileDownloadHandler
from .handler.s3_download_handler import AuditS3FileDownloadHandler
from ....base.base_handler import BaseRequestHandler
from ..base_command import Command


class AuditFileDownloadCommand(Command):
    file_name: str
    file_local_path: str
    size: int | None = None
    file_source: FileSource
    download_status: FileDownloadStatus = FileDownloadStatus.PENDING

    model_config = ConfigDict(extra="allow")

    def to_handler_kwargs(self) -> dict[str, Any]:
        return {
            "file_name": self.file_name,
            "file_local_path": self.file_local_path,
            "size": self.size,
            "download_status": self.download_status,
            **(self.model_extra or {}),
        }

    def _to_doc(self) -> dict:
        return {
            "file_name": self.file_name,
            "file_local_path": self.file_local_path,
            "size": self.size,
            "file_source": self.file_source.value,
            "download_status": self.download_status.value,
        }

class AuditFileDownloadCommandHandler(
    BaseRequestHandler[AuditFileDownloadCommand, AuditFileDownloadCommandResponse]
):
    download_handlers = {
        status: {
            FileSource.GOOGLE_DRIVE: AuditGoogleDriveFileDownloadHandler,
            FileSource.API: AuditAPIFileDownloadHandler,
            FileSource.S3: AuditS3FileDownloadHandler,
        }
        for status in FileDownloadStatus
    }

    def __init__(self):
        self.mongo_repository: BaseNoSqlRepository[FileModel] = BaseMongoRepository(
            model=GoogleDriveFile,
            collection_name="file_collection",
        )

    def handle(
        self,
        request: AuditFileDownloadCommand,
    ) -> AuditFileDownloadCommandResponse:
        source_handlers = self.download_handlers.get(request.download_status)
        if source_handlers is None:
            raise ValueError(f"Unsupported download_status: {request.download_status}")

        handler_type = source_handlers.get(request.file_source)
        if handler_type is None:
            raise ValueError(f"Unsupported file_source: {request.file_source}")

        source_handler = handler_type(
            mongo_repository=self.mongo_repository,
            **request.to_handler_kwargs(),
        )
        return source_handler.handle()
