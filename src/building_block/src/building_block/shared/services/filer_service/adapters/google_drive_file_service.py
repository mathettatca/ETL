from typing import Any

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.infrastructure.mongo.base_mongo_repository import BaseMongoRepository
from building_block.utils.logging import log_error
from building_block.utils.mappers import GoogleDriveFileMapper
from building_block.shared.services.filer_service.ports.IFIleService import (
    IFileService,
)


class GoogleDriveFileService(IFileService[GoogleDriveFile]):
    COLLECTION_NAME = "file_collection"

    def __init__(
        self,
        repository: BaseNoSqlRepository[GoogleDriveFile] | None = None,
    ) -> None:
        self._repository = repository or BaseMongoRepository(
            model=GoogleDriveFile,
            collection_name=self.COLLECTION_NAME,
        )

    def to_model(self, doc: dict) -> GoogleDriveFile:
        return GoogleDriveFileMapper.to_model(doc)

    def to_doc(self, file: GoogleDriveFile) -> dict:
        return GoogleDriveFileMapper.to_doc(file)

    def normalize_filter_options(self, options: dict[str, Any]) -> dict[str, Any]:
        filter_options = dict(options)
        temp_id = filter_options.pop("_id", filter_options.pop("id", None))

        if temp_id is not None:
            filter_options["_id"] = self.to_object_id(temp_id)

        return filter_options

    @staticmethod
    def to_object_id(value: Any) -> Any:
        return GoogleDriveFileMapper.to_object_id(value)

    def save(self, file: GoogleDriveFile) -> str | None:
        file_document = self.to_doc(file=file)
        result = self._repository._get_collection().insert_one(file_document)
        return str(result.inserted_id)


    def get(self, **filter_options: Any) -> GoogleDriveFile | None:
        options = self.normalize_filter_options(filter_options)
        raw = self._repository._get_collection().get(options)
        return self.to_model(raw) if raw is not None else None


    def find_many(self, **filter_options: Any) -> list[GoogleDriveFile]:
        options = self.normalize_filter_options(filter_options)
        raws = self._repository._get_collection().find(options)
        return [self.to_model(raw) for raw in raws]


    def update_one(self, file: GoogleDriveFile) -> bool:
        document = self.to_doc(file)
        file_id = document.pop("_id", document.pop("file_id", None))
        if file_id is None:
            log_error("[GoogleDriveFile] update_one failed: no ID found")
            return False

        file_id = self.to_object_id(file_id)

        result = self._repository._get_collection().update_one(
            {"_id": file_id},
            {"$set": document},
        )
        return result.modified_count > 0


    def delete_one(self, **filter_options: Any) -> bool:
        return self._repository.delete_one(**filter_options)
