from building_block.core.domain.processing_step import ProcessingStep
from data_access.mediator import Mediator
from data_access.application.request.commands.audit_processing_result.audit_processing_result_command import (
    AuditProccessingResultCommand,
)


class AuditProcessingResultAdapter:
    def __init__(self) -> None:
        self.mediator = Mediator()

    def save(
        self,
        file_id: str,
        processing_step: list[dict[str, ProcessingStep]],
    ) -> dict:
        response = self.mediator.send(
            AuditProccessingResultCommand(
                file_id=file_id,
                proccessing_step=processing_step,
            )
        )
        return response
