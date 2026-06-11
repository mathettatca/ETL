"""Public request exports for data access commands and queries."""

_PUBLIC_EXPORTS = {
    "AuditAPIFileCommand": "data_access.application.request.commands",
    "AuditAPIFileCommandHandler": "data_access.application.request.commands",
    "AuditAPIFileCommandResponse": "data_access.application.request.commands",
    "AuditAPIFileDownloadHandler": "data_access.application.request.commands",
    "AuditFileDownloadCommand": "data_access.application.request.commands",
    "AuditFileDownloadCommandHandler": "data_access.application.request.commands",
    "AuditFileDownloadCommandResponse": "data_access.application.request.commands",
    "AuditGDriveFileCommand": "data_access.application.request.commands",
    "AuditGDriveFileCommandHandler": "data_access.application.request.commands",
    "AuditGDriveFileCommandResponse": "data_access.application.request.commands",
    "AuditGoogleDriveFileDownloadHandler": "data_access.application.request.commands",
    "AuditS3FileCommand": "data_access.application.request.commands",
    "AuditS3FileCommandHandler": "data_access.application.request.commands",
    "AuditS3FileCommandResponse": "data_access.application.request.commands",
    "AuditS3FileDownloadHandler": "data_access.application.request.commands",
    "Command": "data_access.application.request.commands",
    "CreateFileCommandHandler": "data_access.application.request.commands",
    "CreateFileCommandRequest": "data_access.application.request.commands",
    "CreateFileCommandResponse": "data_access.application.request.commands",
    "Query": "data_access.application.request.queries",
    "QueryHandler": "data_access.application.request.queries",
}

__all__ = sorted(_PUBLIC_EXPORTS)


def __getattr__(name: str):
    module_name = _PUBLIC_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(
            f"module 'data_access.application.request' has no attribute {name!r}"
        )

    module = __import__(module_name, fromlist=[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
