from datetime import datetime
from typing import Self

from building_block.core.base.base_model import CustomBaseModel


class BaseRequest(CustomBaseModel):
    _created_at:str = str(datetime.now())

    @classmethod
    def _to_model(cls, doc: dict) -> Self:
        return cls.model_validate(doc)

    def _to_doc(self) -> dict:
        return self.model_dump(mode="json")
