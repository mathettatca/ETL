import pandas as pd

from building_block.core.domain.hs_raw_data_model import HsRawDataModel
from building_block.infrastructure.postgres.base_postgre_repository import (
    BasePostgresRepository,
)


class PostgresHsRawDataRepositoryAdapter:
    def __init__(
        self,
        repository: BasePostgresRepository[HsRawDataModel] | None = None,
    ):
        self.repository = repository or BasePostgresRepository(
            model=HsRawDataModel,
            schema=HsRawDataModel.schema_name,
            table_name=HsRawDataModel.table_name,
        )

    def save_dataframe(self, dataframe: pd.DataFrame) -> int:
        return self.repository.insert(dataframe)
