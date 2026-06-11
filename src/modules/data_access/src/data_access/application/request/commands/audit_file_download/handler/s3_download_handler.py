from datetime import datetime
from typing import Any

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.file_model import FileModel
from building_block.shared.enum import FileSource

from ..audit_file_download_command_response import AuditFileDownloadCommandResponse
from ..base_download_handler import BaseAuditFileDownloadSourceHandler


class AuditS3FileDownloadHandler(BaseAuditFileDownloadSourceHandler):
    def __init__(
        self,
        mongo_repository: BaseNoSqlRepository[FileModel],
        **kwargs: Any,
    ):
        super().__init__(mongo_repository=mongo_repository, **kwargs)
        self.bucket_name = self._require(kwargs, "bucket_name")
        self.object_key = self._require(kwargs, "object_key")
        self.region_name = kwargs.get("region_name")
        self.e_tag = kwargs.get("e_tag")

    def handle(self) -> AuditFileDownloadCommandResponse:
        file_model = FileModel(
            name=self.file_name,
            date_create=datetime.now(),
            dest_path=self.file_local_path,
            original=FileSource.S3,
            spec={
                **self.specs,
                "bucket_name": self.bucket_name,
                "object_key": self.object_key,
                "region_name": self.region_name,
                "size": self.size,
                "e_tag": self.e_tag,
            },
        )

        inserted_id = self.mongo_repository.insert_one(file_model)
        return AuditFileDownloadCommandResponse(
            status="success",
            message="Import File Audit successfully",
            status_code=200,
            inserted_id=str(inserted_id) if inserted_id is not None else None,
        )
