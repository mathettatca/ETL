"""Public request exports for data access commands and queries."""

_PUBLIC_EXPORTS = {
    "AuditAPIFileCommand": "modules.data_access.application.request.commands",
    "AuditAPIFileCommandHandler": "modules.data_access.application.request.commands",
    "AuditAPIFileCommandResponse": "modules.data_access.application.request.commands",
    "AuditAPIFileDownloadHandler": "modules.data_access.application.request.commands",
    "AuditFileDownloadCommand": "modules.data_access.application.request.commands",
    "AuditFileDownloadCommandHandler": "modules.data_access.application.request.commands",
    "AuditFileDownloadCommandResponse": "modules.data_access.application.request.commands",
    "AuditGDriveFileCommand": "modules.data_access.application.request.commands",
    "AuditGDriveFileCommandHandler": "modules.data_access.application.request.commands",
    "AuditGDriveFileCommandResponse": "modules.data_access.application.request.commands",
    "AuditGoogleDriveFileDownloadHandler": "modules.data_access.application.request.commands",
    "AuditS3FileCommand": "modules.data_access.application.request.commands",
    "AuditS3FileCommandHandler": "modules.data_access.application.request.commands",
    "AuditS3FileCommandResponse": "modules.data_access.application.request.commands",
    "AuditS3FileDownloadHandler": "modules.data_access.application.request.commands",
    "Command": "modules.data_access.application.request.commands",
    "CreateFileCommandHandler": "modules.data_access.application.request.commands",
    "CreateFileCommandRequest": "modules.data_access.application.request.commands",
    "CreateFileCommandResponse": "modules.data_access.application.request.commands",
    "Query": "modules.data_access.application.request.queries",
    "QueryHandler": "modules.data_access.application.request.queries",
}

__all__ = sorted(_PUBLIC_EXPORTS)


def __getattr__(name: str):
    module_name = _PUBLIC_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(
            f"module 'modules.data_access.application.request' has no attribute {name!r}"
        )

    module = __import__(module_name, fromlist=[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
