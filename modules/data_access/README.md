# Data Access Mediator + CQRS Plan

## Summary

`modules/data_access` will use a sync in-process Mediator with CQRS separation.
This is just application pacakge , centralize data access layer which is not API

Request flow:

```text
caller(modules depend on data_access, not another service) -> mediator -> handler -> repository -> response
```

Mediator responsibilities:

- Dispatch command/query call to registered handlers.
- Resolve handler by request type.
- Return handler response.
- Re-raise handler exceptions directly.

## CQRS Structure

Commands mutate state.

Existing command handlers:

- `AuditGDriveFileCommand -> AuditGDriveFileCommandHandler`
- `AuditAPIFileCommand -> AuditAPIFileCommandHandler`
- `AuditS3FileCommand -> AuditS3FileCommandHandler`

Queries read state.

Base types:

- `Command(BaseRequest)`
- `Query(BaseRequest)`
- `BaseRequestHandler[TRequest, TResponse]`

Fix typing in `BaseRequestHandler` so:

```python
TRequest = TypeVar("TRequest", bound=BaseRequest)
TResponse = TypeVar("TResponse", bound=BaseResponse)
```

## Mediator Design

Add `Mediator`:

```python
response = mediator.send(request)
```

Behavior:

- Resolve handler by request class.
- Raise `ValueError` if no handler is registered.
- Execute handler directly.
- Return handler response.

Add `MediatorRegistry`:

```python
registry.register(AuditGDriveFileCommand, AuditGDriveFileCommandHandler)
handler = registry.resolve(AuditGDriveFileCommand)
```

Handler factory may be either:

- handler class
- lambda/factory returning a handler instance

## Pipeline Behaviors

Mediator pipeline behaviors were removed by design. The mediator now dispatches
directly to the resolved handler. Logging, audit, and error handling should be
implemented inside the relevant handler/service if a use case needs them.

## Usage Example

```python
from modules.data_access.mediator import build_data_access_mediator
from modules.data_access.application.request.commands import AuditGDriveFileCommand

mediator = build_data_access_mediator()

request = AuditGDriveFileCommand(
    file_name="data.csv",
    file_local_path="tmp/data.csv",
    drive_file_id="1A2B3C4D5E",
    mime_type="text/csv",
    size_bytes=2048,
)

response = mediator.send(request)
```

## Implementation Notes

- `main.py` should create mediator registry/factory usage examples only
- Commands and queries should not know about mediator.
- Handlers keep business orchestration.
- Repositories keep persistence logic.
- Mediator should not contain cross-cutting pipeline logic.

## Test Plan

Add unit tests for:

- registry register/resolve
- unknown request raises `ValueError`
- mediator dispatches command to correct handler
- mediator re-raises handler exception directly
- current command tests still pass

Run:

```bash
uv run pytest -q test/unit_test
```

## Assumptions

- Mediator v1 is synchronous.
- Handler errors are re-raised directly.
- No validation pipeline in v1 beyond Pydantic model validation.
