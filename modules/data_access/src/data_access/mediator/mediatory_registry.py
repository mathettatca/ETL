from collections.abc import Callable
from typing import Any, TypeVar

from data_access.application.base.base_handler import BaseRequestHandler
from data_access.application.base.base_request import BaseRequest
from data_access.application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
    AuditFileDownloadCommandHandler,
)
from data_access.application.request.commands.save_hs_raw_data.save_hs_raw_data_command import (
    SaveHsRawDataCommand,
    SaveHsRawDataCommandHandler,
)
from data_access.mediator.mediator import Mediator


TRequest = TypeVar("TRequest", bound=BaseRequest)
HandlerFactory = type[BaseRequestHandler[Any, Any]] | Callable[[], BaseRequestHandler[Any, Any]]


class MediatorRegistry:
    def __init__(self):
        self._handlers: dict[type[BaseRequest], HandlerFactory] = {}

    def register(
        self,
        request_type: type[TRequest],
        handler_factory: HandlerFactory,
    ) -> None:
        self._handlers[request_type] = handler_factory

    def resolve(self, request_type: type[TRequest]) -> BaseRequestHandler[Any, Any]:
        handler_factory = self._handlers.get(request_type)
        if handler_factory is None:
            raise ValueError(f"No handler registered for request type: {request_type.__name__}")
        return handler_factory()


def build_data_access_registry() -> MediatorRegistry:
    registry = MediatorRegistry()
    registry.register(AuditFileDownloadCommand, AuditFileDownloadCommandHandler)
    registry.register(SaveHsRawDataCommand, SaveHsRawDataCommandHandler)
    return registry


def build_data_access_mediator() -> Mediator:
    registry = build_data_access_registry()
    return Mediator(registry=registry)
