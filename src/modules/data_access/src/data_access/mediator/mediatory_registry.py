from collections.abc import Callable
from typing import Any, TypeVar

from data_access.application.base.base_handler import BaseRequestHandler
from data_access.application.base.base_request import BaseRequest
from data_access.application.base.base_response import BaseResponse

HandlerFactory = type[BaseRequestHandler[Any, Any]] | Callable[[], BaseRequestHandler[Any, Any]]


class MediatorRegistry:
    def __init__(self):
        self._handlers: dict[type[BaseRequest], HandlerFactory] = {}

    def register(
        self,
        request_type: type[BaseRequest],
        handler_factory: HandlerFactory,
    ) -> None:
        if request_type not in self._handlers:
            self._handlers[request_type] = handler_factory

    def resolve(self, request_type: type[BaseRequest]) -> BaseRequestHandler[BaseRequest, BaseResponse]:
        handler_factory = self._handlers.get(request_type)
        if handler_factory is None:
            raise ValueError(f"No handler registered for request type: {request_type.__name__}")
        return handler_factory()



