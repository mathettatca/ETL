"""Base model for all models in the system."""

from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    """
    Base class for models that support conversion to/from document format.
    """

    @classmethod
    def _to_model(cls, doc: dict) -> "CustomBaseModel":
        return cls.model_validate(doc)

    def _to_doc(self) -> dict:
        return self.model_dump(mode="json")
