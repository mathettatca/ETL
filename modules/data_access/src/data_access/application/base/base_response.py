from abc import ABC
from enum import Enum



class BaseResponse(ABC):
    _status_code:int = None
    _status: str = None
    _message:str = None
    def __init__(self,status:str,message:str,status_code:int =200):
        self._status_code = status_code
        self._status = status
        self._message= message
