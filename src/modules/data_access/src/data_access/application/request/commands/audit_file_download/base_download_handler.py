from typing import Any

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.file_model import FileModel
from building_block.shared.enum import FileDownloadStatus


class BaseAuditFileDownloadSourceHandler:
    def __init__(
        self,
        mongo_repository: BaseNoSqlRepository[FileModel],
        **kwargs: Any,
    ):
        self.mongo_repository = mongo_repository
        self.file_name = self._require(kwargs, "file_name")
        self.file_local_path = self._require(kwargs, "file_local_path")
        self.size = kwargs.get("size")
        self.download_status = FileDownloadStatus(
            kwargs.get("download_status", FileDownloadStatus.PENDING)
        )
        self.specs = kwargs.get("specs", {})

    def _require(self, kwargs: dict[str, Any], key: str) -> Any:
        value = kwargs.get(key)
        if value is None:
            raise ValueError(f"{key} is required")
        return value

    def handle(self) -> Any:
        raise NotImplementedError
