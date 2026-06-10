from typing import Protocol

import pandas as pd


class HsRawDataSaverPort(Protocol):
    def save(self, dataframe: pd.DataFrame) -> dict:
        ...
