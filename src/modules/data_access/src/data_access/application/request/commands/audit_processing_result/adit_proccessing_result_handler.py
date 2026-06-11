from datetime import datetime
from typing import ClassVar

from building_block.core.base.base_nosql_repository import BaseNoSqlRepository
from building_block.core.base.base_model import CustomBaseModel
from building_block.core.domain.processing_step import ProcessingStep
from building_block.infrastructure.mongo.base_mongo_repository import BaseMongoRepository
from data_access.application.base.base_handler import BaseRequestHandler
from .audit_proccessing_result_response import AuditProccessingResultResponse
from .audit_processing_result_command import AuditProccessingResultCommand


class AuditProcessingResultModel(CustomBaseModel):
    collection_name: ClassVar[str] = "processing_result_collection"
    file_id: str
    proccessing_step: list[dict[str, dict]]
    audited_at: datetime

    def _to_doc(self) -> dict:
        return {
            "file_id": self.file_id,
            "proccessing_step": self.proccessing_step,
            "audited_at": self.audited_at,
        }


class AuditProccessingResultHanlder(
    BaseRequestHandler[AuditProccessingResultCommand, AuditProccessingResultResponse]
):
    def __init__(self, repository: BaseNoSqlRepository | None = None):
        self.repository: BaseNoSqlRepository = repository or BaseMongoRepository(
            AuditProcessingResultModel
        )

    def handle(self, request: AuditProccessingResultCommand) -> AuditProccessingResultResponse:
        audit_model = AuditProcessingResultModel(
            file_id=request.file_id,
            proccessing_step=self._normalize_processing_steps(request.proccessing_step),
            audited_at=datetime.now(),
        )
        inserted_id = self.repository.insert_one(audit_model)
        if inserted_id is None:
            return AuditProccessingResultResponse(
                status="failed",
                message="Audit processing result failed",
                status_code=500,
            )

        return AuditProccessingResultResponse(
            status="success",
            message="Audit processing result successfully",
            status_code=200,
            inserted_id=str(inserted_id),
        )

    def _normalize_processing_steps(
        self,
        processing_steps: list[dict[str, ProcessingStep]],
    ) -> list[dict[str, dict]]:
        return [
            {
                step_name: processing_step._to_doc()
                for step_name, processing_step in processing_step_item.items()
            }
            for processing_step_item in processing_steps
        ]
