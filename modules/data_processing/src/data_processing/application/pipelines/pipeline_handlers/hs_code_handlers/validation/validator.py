"""Validation rules for HS-code datasets."""

from __future__ import annotations

from building_block.core.domain.processing_step import ProcessingStep, ProcessingStepStatus
import pandas as pd

from data_processing.application.pipelines.pipeline_handlers.hs_code_handlers.validation.hs_code_validation import (
    HsCodeValidationResult,
)
from data_processing.domain.models.base_handler import BaseProcessingHandler
from data_processing.domain.models.processed_data import ProcessedData
from data_processing.domain.models.schema import COLUMN_TYPES


class HsCodeSchemaValidationHandler(BaseProcessingHandler):
    """Validate HS-code dataframe schema and data quality signals."""

    step_name = "validation_step"

    def __init__(
        self,
        column_types: dict[str, str] | None = None,
        missing_value_threshold: float = 0.8,
    ) -> None:
        super().__init__()
        self.column_types = column_types or COLUMN_TYPES
        self.missing_value_threshold = missing_value_threshold

    def _process(self, data: ProcessedData) -> ProcessedData:
        df = data.dataframe
        try:
            result: HsCodeValidationResult = self.validate(df)
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.SUCCESS,
                message="Validation successfully",
                status_code=200,
                result=result._to_doc(),
            )
            # Append validation result to processing_steps list
            data.processing_steps = data.processing_steps + [
                {"validation_step": proccessing_step}
            ]

            return data
        except Exception as exc:
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.FAILED,
                message="Validation failed",
                status_code=500,
                error=str(exc),
            )
            data.processing_steps = data.processing_steps + [
                {"validation_step": proccessing_step}
            ]
            return data

    def validate(self, df: pd.DataFrame) -> HsCodeValidationResult:
        return HsCodeValidationResult(
            missing_columns=self.get_missing_columns(df),
            wrong_type_columns=self.get_wrong_type_columns(df),
            missing_value_warning=self.get_missing_value_result(df),
        )

    def get_missing_columns(self, df: pd.DataFrame) -> bool:
        missing_cols = [
            column for column in self.column_types.keys() if column not in df.columns
        ]
        if len(missing_cols) > 0:
            missing_col_str = ", ".join(str(missing_col) for missing_col in missing_cols)
            raise Exception(f"Column missed: {missing_col_str}")
        return True

    def get_wrong_type_columns(
        self,
        df: pd.DataFrame,
    ) -> bool:
        wrong_type_columns = {}

        for column, expected_type in self.column_types.items():
            if column not in df.columns:
                continue

            if not self.is_expected_type(df[column], expected_type):
                wrong_type_columns[column] = {
                    "expect": expected_type,
                    "actual": str(df[column].dtype),
                }

        if len(wrong_type_columns) > 0:
            raise Exception(f"Wrong type columns: {wrong_type_columns}")

        return True

    def is_expected_type(self, series: pd.Series, expected_type: str) -> bool:
        dtype = series.dtype
        expected_type = expected_type.strip().lower()

        if expected_type == "int":
            return pd.api.types.is_integer_dtype(dtype)

        if "float" in expected_type:
            return pd.api.types.is_float_dtype(dtype)

        if expected_type == "str":
            if pd.api.types.is_string_dtype(dtype):
                return True
            if pd.api.types.is_object_dtype(dtype):
                non_null_values = series.dropna()
                return non_null_values.map(lambda value: isinstance(value, str)).all()
            return False

        if expected_type == "object":
            return pd.api.types.is_object_dtype(dtype)

        return False

    def get_missing_value_result(
        self,
        df: pd.DataFrame,
    ) -> dict[str, dict[str, float | int | str]]:
        total_rows = len(df)
        if total_rows == 0:
            return {}

        missing_value_result = {}
        for column in df.columns:
            missing_count = int(df[column].isna().sum())
            missing_ratio = missing_count / total_rows
            if missing_ratio > self.missing_value_threshold:
                missing_value_result[column] = {
                    "col_name": column,
                    "missing_value": missing_ratio,
                    "missing_count": missing_count,
                    "total": total_rows,
                }

        return missing_value_result
