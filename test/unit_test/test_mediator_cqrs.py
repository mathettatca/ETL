from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "building_block" / "src"))

import pytest

from modules.data_access.application.base.base_handler import BaseRequestHandler
from modules.data_access.application.base.base_response import BaseResponse
from modules.data_access.mediator import Mediator, MediatorRegistry
from modules.data_access.application.request.commands.base_command import Command


class FakeCommand(Command):
    value: int


class UnknownCommand(Command):
    value: int


class FakeResponse(BaseResponse):
    def __init__(self, status: str, message: str):
        super().__init__(status, message)

    def _to_doc(self) -> dict:
        return {
            "status": self._status,
            "message": self._message,
        }


class FakeHandler(BaseRequestHandler[FakeCommand, FakeResponse]):
    def __init__(self):
        self.handled_requests: list[FakeCommand] = []

    def handle(self, request: FakeCommand) -> FakeResponse:
        self.handled_requests.append(request)
        return FakeResponse(status="success", message="Import File Audit successfully")


class FailingHandler(BaseRequestHandler[FakeCommand, FakeResponse]):
    def handle(self, request: FakeCommand) -> FakeResponse:
        raise RuntimeError("handler failed")


def test_registry_register_and_resolve():
    registry = MediatorRegistry()
    registry.register(FakeCommand, FakeHandler)

    handler = registry.resolve(FakeCommand)

    assert isinstance(handler, FakeHandler)


def test_registry_unknown_request_raises_value_error():
    registry = MediatorRegistry()

    with pytest.raises(ValueError):
        registry.resolve(UnknownCommand)


def test_mediator_dispatches_to_handler():
    handler = FakeHandler()
    registry = MediatorRegistry()
    registry.register(FakeCommand, lambda: handler)
    mediator = Mediator(registry=registry)

    response = mediator.send(FakeCommand(value=1))

    assert response._to_doc() == {
        "status": "success",
        "message": "Import File Audit successfully",
    }
    assert len(handler.handled_requests) == 1
    assert handler.handled_requests[0].value == 1


def test_mediator_re_raises_handler_exception():
    registry = MediatorRegistry()
    registry.register(FakeCommand, FailingHandler)
    mediator = Mediator(registry=registry)

    with pytest.raises(RuntimeError, match="handler failed"):
        mediator.send(FakeCommand(value=1))
