from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .base_response import BaseResponse
from .base_request import BaseRequest



TRequest = TypeVar("TRequest", bound=BaseRequest)
TResponse = TypeVar("TResponse", bound=BaseResponse)

class BaseRequestHandler(ABC, Generic[TRequest, TResponse]):
    @abstractmethod
    def handle(self,request:TRequest) -> TResponse:
        pass

    
