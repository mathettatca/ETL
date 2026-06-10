from data_access.application.base.base_response import BaseResponse


class AuditFileDownloadCommandResponse(BaseResponse):

    @classmethod
    def _to_model(cls, _dict: dict) -> "AuditFileDownloadCommandResponse":
        return cls(status=_dict["status"], message=_dict["message"],status_code = _dict["status_code"])

    def _to_doc(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "status_code":self.status_code
        }
