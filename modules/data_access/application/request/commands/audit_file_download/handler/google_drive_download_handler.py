from datetime import datetime
from typing import Any

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.file_model import FileModel
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.utils.logging import info
from ..audit_file_download_command_response import AuditFileDownloadCommandResponse
from ..base_download_handler import BaseAuditFileDownloadSourceHandler


class AuditGoogleDriveFileDownloadHandler(BaseAuditFileDownloadSourceHandler):
    def __init__(
        self,
        mongo_repository: BaseNoSqlRepository[FileModel],
        **kwargs: Any,
    ):
        super().__init__(mongo_repository=mongo_repository, **kwargs)
        self.drive_file_id = self._require(kwargs, "drive_file_id")
        self.mime_type = self._require(kwargs, "mime_type")

    def handle(self) -> AuditFileDownloadCommandResponse:
        try:
            file:FileModel = self.mongo_repository.get(drive_file_id=self.drive_file_id)
            info(f"[AuditGoogleDriveFileDownloadHandler] get file sucess")
            if file is not None:
                info(f"[AuditGoogleDriveFileDownloadHandler] file :{file._to_doc()} ")
                update_data = {
                    "name": self.file_name,
                    "dest_path": self.file_local_path,
                    "drive_file_id": self.drive_file_id,
                    "mime_type": self.mime_type,
                    "size_bytes": self.size,
                    "download_status": self.download_status,
                }
                update_data = {
                    key: value for key, value in update_data.items() if value is not None
                }
                file = file.model_copy(update=update_data)
                self.mongo_repository.update_one(file)
                return AuditFileDownloadCommandResponse(
                    status="success",
                    message="Update File Audit successfully",
                    status_code= 201 
                )
            file_model = GoogleDriveFile(
                name=self.file_name,
                date_create=datetime.now(),
                dest_path=self.file_local_path,
                drive_file_id=self.drive_file_id,
                mime_type=self.mime_type,
                size_bytes=self.size,
                download_status=self.download_status,
            )

            self.mongo_repository.insert_one(file_model)
            return AuditFileDownloadCommandResponse(
                status="success",
                message="Import File Audit successfully",
                status_code=200
            )
        except Exception as e:
            error_name = type(e).__name__
            raise Exception(
                f"[AuditGoogleDriveFileDownloadHandler] Audit Google drive handler exception: {error_name}: {e}"
            ) from e
