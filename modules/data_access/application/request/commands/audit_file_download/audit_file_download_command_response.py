from application.base.base_response import BaseResponse


class AuditFileDownloadCommandResponse(BaseResponse):
    def __init__(self, status: str, message: str,status_code:int):
        super().__init__(status, message,status_code)

    @classmethod
    def _to_model(cls, _dict: dict) -> "AuditFileDownloadCommandResponse":
        return cls(status=_dict["status"], message=_dict["message"],status_code = _dict["status_code"])

    def _to_doc(self) -> dict:
        return {
            "status": self._status,
            "message": self._message,
            "status_code":self._status_code
        }
