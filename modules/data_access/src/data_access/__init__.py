"""Public boundary for the internal data access package."""

_PUBLIC_EXPORTS = {
    "AuditAPIFileCommand": "data_access.application.request",
    "AuditFileDownloadCommand": "data_access.application.request",
    "AuditFileDownloadCommandResponse": "data_access.application.request",
    "AuditGDriveFileCommand": "data_access.application.request",
    "AuditS3FileCommand": "data_access.application.request",
    "Command": "data_access.application.request",
    "Mediator": "data_access.mediator",
    "Query": "data_access.application.request",
    "build_data_access_mediator": "data_access.mediator",
    "build_data_access_registry": "data_access.mediator",
}

__all__ = sorted(_PUBLIC_EXPORTS)


def __getattr__(name: str):
    module_name = _PUBLIC_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'data_access' has no attribute {name!r}")

    module = __import__(module_name, fromlist=[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
