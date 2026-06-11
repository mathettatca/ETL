"""Column mapping for HS-code datasets."""

from __future__ import annotations

import pandas as pd

from building_block.core.domain.processing_step import ProcessingStep, ProcessingStepStatus
from data_processing.domain.models.schema import COLUMN_IMP_MAPPING, mapped_columns
from data_processing.domain.models.base_handler import BaseProcessingHandler
from data_processing.domain.models.processed_data import ProcessedData


class HsCodeColumnMapper:
    """Map source columns to canonical HS-code columns."""

    def __init__(self, column_mapping: dict[str, str] | None = None) -> None:
        self.column_mapping = column_mapping or COLUMN_IMP_MAPPING

    def map(self, df: pd.DataFrame) -> pd.DataFrame:
        mapped_df = df.rename(columns=self.column_mapping)
        existing_columns = [
            column for column in mapped_columns() if column in mapped_df.columns
        ]
        return mapped_df[existing_columns]


class HsCodeColumnMappingHandler(BaseProcessingHandler):
    """Chain step that maps source columns to canonical HS-code columns."""

    step_name = "map_columns"

    def __init__(self, column_mapper: HsCodeColumnMapper | None = None) -> None:
        super().__init__()
        self.column_mapper = column_mapper or HsCodeColumnMapper()

    def _process(self, data: ProcessedData) -> ProcessedData:

        df = data.dataframe
        try:
            if not isinstance(df, pd.DataFrame):
                raise Exception("dataframe not found in structured_data")

            mapped_df = self.column_mapper.map(df)
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.SUCCESS,
                message="Column mapping successfully",
                status_code=200,
                result={
                    "columns": list(mapped_df.columns),
                },
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]
            data.dataframe = mapped_df

            return data
        except Exception as exc:
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.FAILED,
                message="Column mapping failed",
                status_code=500,
                error=str(exc),
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]
            return data
