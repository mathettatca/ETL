from data_access.mediator.mediator import Mediator
from .audit_file_download_command import (
    AuditFileDownloadCommand,
    AuditFileDownloadCommandHandler
)

Mediator._registry.register(
    AuditFileDownloadCommand,AuditFileDownloadCommandHandler
)