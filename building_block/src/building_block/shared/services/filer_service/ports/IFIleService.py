from abc import abstractmethod
from typing import Any, Protocol, TypeVar

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.domain.file_model import FileModel

TFileModel = TypeVar("TFileModel", bound=FileModel)


class IFileService(Protocol[TFileModel]):
    _repository: BaseNoSqlRepository[TFileModel]

    @abstractmethod
    def to_model(self, doc: dict) -> TFileModel:
        """Map source/persistence data into a file model."""
        ...

    @abstractmethod
    def to_doc(self, file: TFileModel) -> dict:
        """Map a file model into a persistence document."""
        ...

    @abstractmethod
    def save(self, file: TFileModel) -> str | None:
        """Create/save a file model."""
        ...

    @abstractmethod
    def get(self, **filter_options: Any) -> TFileModel | None:
        """Read one file model by filter options."""
        ...

    @abstractmethod
    def find_many(self, **filter_options: Any) -> list[TFileModel]:
        """Read many file models by filter options."""
        ...

    @abstractmethod
    def update_one(self, file: TFileModel) -> bool:
        """Update one file model."""
        ...

    @abstractmethod
    def delete_one(self, **filter_options: Any) -> bool:
        """Delete one file model by filter options."""
        ...
