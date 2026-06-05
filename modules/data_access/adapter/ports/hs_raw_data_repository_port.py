from typing import Protocol

import pandas as pd


class HsRawDataRepositoryPort(Protocol):
    def save_dataframe(self, dataframe: pd.DataFrame) -> int:
        pass
