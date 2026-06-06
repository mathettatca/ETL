from typing import Any

from data_access.application.base.base_request import BaseRequest


class Mediator:
    def __init__(self, registry: Any):
        self.registry = registry

    def send(self, request: BaseRequest) -> Any:
        handler = self.registry.resolve(type(request))
        return handler.handle(request)
