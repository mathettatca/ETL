from abc import ABC
from enum import Enum

from building_block.core.base.base_model import CustomBaseModel
from pydantic import Field



class BaseResponse(ABC,CustomBaseModel):
    status: str = Field(description="Response status")
    message: str = Field(description="Response message")
    status_code: int = Field(default=200, description="Response status code")