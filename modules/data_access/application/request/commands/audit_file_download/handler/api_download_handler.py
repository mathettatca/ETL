from datetime import datetime
from typing import Any

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.api_file import ApiFile
from building_block.core.domain.file_model import FileModel

from ..audit_file_download_command_response import AuditFileDownloadCommandResponse
from ..base_download_handler import BaseAuditFileDownloadSourceHandler


class AuditAPIFileDownloadHandler(BaseAuditFileDownloadSourceHandler):
    def __init__(
        self,
        mongo_repository: BaseNoSqlRepository[FileModel],
        **kwargs: Any,
    ):
        super().__init__(mongo_repository=mongo_repository, **kwargs)
        self.endpoint_url = self._require(kwargs, "endpoint_url")
        self.response_code = kwargs.get("response_code")
        self.content_type = kwargs.get("content_type")
        self.request_params = kwargs.get("request_params", {})

    def handle(self) -> AuditFileDownloadCommandResponse:
        file_model = ApiFile(
            name=self.file_name,
            date_create=datetime.now(),
            dest_path=self.file_local_path,
            endpoint_url=self.endpoint_url,
            response_code=self.response_code,
            content_type=self.content_type,
            request_params=self.request_params,
            spec=self.specs,
        )

        self.mongo_repository.insert_one(file_model)
        return AuditFileDownloadCommandResponse(
            status="success",
            message="Import File Audit successfully",
            status_code=200
        )
