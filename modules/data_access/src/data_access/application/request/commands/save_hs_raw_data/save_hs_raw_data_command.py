from typing import ClassVar

from data_access.application.base.base_request import BaseRequest
import pandas as pd
from pydantic import ConfigDict

from data_access.adapter.ports.hs_raw_data_repository_port import HsRawDataRepositoryPort
from building_block.core.domain.hs_raw_data_model import HsRawDataModel


HS_RAW_DATA_INSERT_COLUMNS: tuple[str, ...] = HsRawDataModel.insert_columns()


class SaveHsRawDataCommand(BaseRequest):
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





