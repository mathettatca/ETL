from typing import Any, ClassVar

from data_access.application.base.base_request import BaseRequest
from data_access.mediator.mediatory_registry import MediatorRegistry


class Mediator:
    _instance: ClassVar["Mediator | None"] = None
    _registry: ClassVar[MediatorRegistry ] = MediatorRegistry()


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    
    def send(self, request: BaseRequest) -> dict:
        handler = self._registry.resolve(type(request))
        return handler.handle(request)._to_doc()
    

