from typing import Any

from data_access.application.base.base_request import BaseRequest
from data_access.mediator.mediatory_registry import MediatorRegistry, build_data_access_registry


class Mediator:
    _instance: "Mediator" = None
    _registry: MediatorRegistry = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Registry dùng để lưu request_type -> handler
            cls._instance._registry = build_data_access_registry()
        return cls._instance
        
    
    def send(self, request: BaseRequest) -> Any:
        handler = self._registry.resolve(type(request))
        return handler.handle(request)