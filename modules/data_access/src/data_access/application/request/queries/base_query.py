from typing import Generic, TypeVar

from ...base.base_handler import BaseRequestHandler
from ...base.base_request import BaseRequest
from ...base.base_response import BaseResponse


TQuery = TypeVar("TQuery", bound=BaseRequest)
TResponse = TypeVar("TResponse", bound=BaseResponse)


class Query(BaseRequest):
    """Marker base class for read-only requests."""


class QueryHandler(BaseRequestHandler[TQuery, TResponse], Generic[TQuery, TResponse]):
    """Base handler for query requests."""
