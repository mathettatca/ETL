from data_access.application.base.base_response import BaseResponse
import pandas as pd

from data_access.application.request.commands import SaveHsRawDataCommand
from data_access.mediator import Mediator


class HsRawDataMediatorAdapter:
    def __init__(self) -> None:
        self.mediator = Mediator()

    def save(self, dataframe: pd.DataFrame) -> dict:
        response:dict = self.mediator.send(SaveHsRawDataCommand(dataframe=dataframe))
        return response
