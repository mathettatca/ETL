"""Processed data model."""

from building_block.core.domain.processing_step import ProcessingStep
from building_block.shared.enum.file_source import FileSource
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ProcessedData(BaseModel):
    """Model representing data after processing pipeline."""

    file_id: str = Field(..., description="Unique file identifier")
    dataframe: pd.DataFrame = Field(
        default_factory=dict,
        description="Structured processing payload and metadata",
    )
    processing_steps: list[dict[str, ProcessingStep]] = Field(
        default_factory=list, description="Audit trail of processing steps"
    )
    processed_at: datetime = Field(..., description="Processing completion time")
    data_source:FileSource = Field(
        default=None,description="Source of datafile"
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
