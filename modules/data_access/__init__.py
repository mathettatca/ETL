"""Public boundary for the internal data access package."""

_PUBLIC_EXPORTS = {
    "AuditAPIFileCommand": "modules.data_access.application.request",
    "AuditFileDownloadCommand": "modules.data_access.application.request",
    "AuditFileDownloadCommandResponse": "modules.data_access.application.request",
    "AuditGDriveFileCommand": "modules.data_access.application.request",
    "AuditS3FileCommand": "modules.data_access.application.request",
    "Command": "modules.data_access.application.request",
    "Mediator": "modules.data_access.mediator",
    "Query": "modules.data_access.application.request",
    "build_data_access_mediator": "modules.data_access.mediator",
    "build_data_access_registry": "modules.data_access.mediator",
}

__all__ = sorted(_PUBLIC_EXPORTS)


def __getattr__(name: str):
    module_name = _PUBLIC_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'modules.data_access' has no attribute {name!r}")

    module = __import__(module_name, fromlist=[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
