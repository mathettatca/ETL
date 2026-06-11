from data_access.application.base.base_response import BaseResponse
from pydantic import Field


class AuditProccessingResultResponse(BaseResponse):
    inserted_id: str | str = Field(default= None)

    @classmethod
    def _to_model(cls, _dict: dict) -> "AuditProccessingResultResponse":
        return cls(
            status=_dict["status"],
            message=_dict["message"],
            status_code=_dict["status_code"],
            inserted_id=_dict.get("inserted_id"),
        )

    def _to_doc(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "status_code": self.status_code,
            "inserted_id": self.inserted_id,
        }
