from data_access.application.base.base_response import BaseResponse
from pydantic import Field


class AuditFileDownloadCommandResponse(BaseResponse):
    inserted_id: str | None = Field(default=None, description="Inserted Id")

    @classmethod
    def _to_model(cls, _dict: dict) -> "AuditFileDownloadCommandResponse":
        return cls(
            status=_dict["status"],
            message=_dict["message"],
            status_code=_dict["status_code"],
            inserted_id=_dict.get("inserted_id"),
        )

    def _to_doc(self) -> dict:
        doc = {
            "status": self.status,
            "message": self.message,
            "status_code": self.status_code,
        }
        if self.inserted_id is not None:
            doc["inserted_id"] = self.inserted_id
        return doc
