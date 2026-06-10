from data_access.mediator.mediator import Mediator

from .save_hs_raw_data_command import HS_RAW_DATA_INSERT_COLUMNS, SaveHsRawDataCommand
from .save_hs_raw_data_handler import SaveHsRawDataCommandHandler
from .save_hs_raw_data_response import SaveHsRawDataCommandResponse

Mediator._registry.register(
    SaveHsRawDataCommand,
    SaveHsRawDataCommandHandler,
)

__all__ = [
    "HS_RAW_DATA_INSERT_COLUMNS",
    "SaveHsRawDataCommand",
    "SaveHsRawDataCommandHandler",
    "SaveHsRawDataCommandResponse",
]
