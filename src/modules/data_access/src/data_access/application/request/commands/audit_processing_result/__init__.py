from data_access.mediator.mediator import Mediator

from .adit_proccessing_result_handler import AuditProccessingResultHanlder
from .audit_processing_result_command import AuditProccessingResultCommand
from .audit_proccessing_result_response import AuditProccessingResultResponse

Mediator._registry.register(
    AuditProccessingResultCommand,
    AuditProccessingResultHanlder,
)

__all__ = [
    "AuditProccessingResultCommand",
    "AuditProccessingResultHanlder",
    "AuditProccessingResultResponse",
]
