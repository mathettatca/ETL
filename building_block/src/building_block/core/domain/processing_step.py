from datetime import datetime
from enum import Enum
from typing import Any

from building_block.core.base.base_model import CustomBaseModel
from pydantic import Field


class ProcessingStepStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingStep(CustomBaseModel):
    status: ProcessingStepStatus
    message: str | None = None
    status_code: int | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    processed_at: datetime = Field(default_factory=datetime.now)