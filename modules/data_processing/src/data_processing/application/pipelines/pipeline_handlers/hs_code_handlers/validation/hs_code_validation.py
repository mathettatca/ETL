"""HS-code validation result models."""

from __future__ import annotations

from building_block.core.base.base_model import CustomBaseModel
from pydantic import Field


class HsCodeValidationResult(CustomBaseModel):
    """Result of running HS-code dataframe validation rules."""

    missing_columns: bool = Field(default=True)
    wrong_type_columns: bool = Field(default=True)
    missing_value_warning: dict[str, dict[str, float | int | str]] = Field(
        default_factory=dict
    )

    @property
    def has_schema_error(self) -> bool:
        return not (self.missing_columns and self.wrong_type_columns)
