from pydantic import Field

from data_access.application.base.base_response import BaseResponse


class SaveHsRawDataCommandResponse(BaseResponse):
    inserted_count:int = Field(default=0,description="inserted Column count")

    @classmethod
    def _to_model(cls, _dict: dict) -> "SaveHsRawDataCommandResponse":
        return cls(
            status=_dict["status"],
            message=_dict["message"],
            status_code=_dict["status_code"],
            inserted_count=_dict["inserted_count"],
        )

    def _to_doc(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "status_code": self.status_code,
            "inserted_count": self.inserted_count,
        }