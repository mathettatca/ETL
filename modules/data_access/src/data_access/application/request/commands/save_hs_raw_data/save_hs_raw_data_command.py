from typing import ClassVar

import pandas as pd
from pydantic import ConfigDict

from data_access.adapter.ports.hs_raw_data_repository_port import HsRawDataRepositoryPort
from data_access.adapter.postgres_hs_raw_data_repository_adapter import (
    PostgresHsRawDataRepositoryAdapter,
)
from data_access.application.base.base_handler import BaseRequestHandler
from data_access.application.base.base_response import BaseResponse
from building_block.core.domain.hs_raw_data_model import HsRawDataModel
from ..base_command import Command


HS_RAW_DATA_INSERT_COLUMNS: tuple[str, ...] = HsRawDataModel.insert_columns()


class SaveHsRawDataCommand(Command):
    dataframe: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)
    insert_columns: ClassVar[tuple[str, ...]] = HsRawDataModel.insert_columns()

    def normalized_dataframe(self) -> pd.DataFrame:
        if not isinstance(self.dataframe, pd.DataFrame):
            raise ValueError("dataframe must be a pandas DataFrame")

        allowed_columns = set(self.insert_columns)
        input_columns = set(self.dataframe.columns)
        extra_columns = sorted(input_columns - allowed_columns)
        if extra_columns:
            raise ValueError(
                "hs_raw_data dataframe contains unsupported columns: "
                + ", ".join(extra_columns)
            )

        dataframe = self.dataframe.copy()
        for column in self.insert_columns:
            if column not in dataframe.columns:
                dataframe[column] = None

        return dataframe.loc[:, list(self.insert_columns)]

    def _to_doc(self) -> dict:
        return {
            "row_count": len(self.dataframe) if isinstance(self.dataframe, pd.DataFrame) else None,
            "columns": (
                list(self.dataframe.columns)
                if isinstance(self.dataframe, pd.DataFrame)
                else None
            ),
        }


class SaveHsRawDataCommandResponse(BaseResponse):
    def __init__(
        self,
        status: str,
        message: str,
        inserted_count: int,
        status_code: int = 200,
    ):
        super().__init__(status, message, status_code)
        self.inserted_count = inserted_count

    @classmethod
    def _to_model(cls, _dict: dict) -> "SaveHsRawDataCommandResponse":
        return cls(
            status=_dict["status"],
            message=_dict["message"],
            status_code=_dict["status_code"],
            inserted_count=_dict["inserted_count"],
        )

    def _to_doc(self) -> dict:
        return {
            "status": self._status,
            "message": self._message,
            "status_code": self._status_code,
            "inserted_count": self.inserted_count,
        }


class SaveHsRawDataCommandHandler(
    BaseRequestHandler[SaveHsRawDataCommand, SaveHsRawDataCommandResponse]
):
    def __init__(self, repository: HsRawDataRepositoryPort | None = None):
        self.repository = repository or PostgresHsRawDataRepositoryAdapter()

    def handle(
        self,
        request: SaveHsRawDataCommand,
    ) -> SaveHsRawDataCommandResponse:
        dataframe = request.normalized_dataframe()
        inserted_count = 0
        if not dataframe.empty:
            inserted_count = self.repository.save_dataframe(dataframe)

        return SaveHsRawDataCommandResponse(
            status="success",
            message="Save HS raw data successfully",
            status_code=200,
            inserted_count=inserted_count,
        )
