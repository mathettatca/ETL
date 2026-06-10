"""Persistence chain step for HS-code raw data."""

from __future__ import annotations

import pandas as pd

from building_block.core.domain.processing_step import ProcessingStep, ProcessingStepStatus
from data_access.application.request.commands import (
    HS_RAW_DATA_INSERT_COLUMNS,
)

from data_processing.domain.models.base_handler import BaseProcessingHandler
from data_processing.domain.models.processed_data import ProcessedData
from data_processing.services.adapters.hs_raw_data_mediator_adapter import (
    HsRawDataMediatorAdapter,
)


class SaveHsRawDataMediatorHandler(BaseProcessingHandler):
    """Persist the final HS-code DataFrame through data_access mediator."""

    step_name = "save_hs_raw_data"

    def __init__(self) -> None:
        super().__init__()
        self.saver = HsRawDataMediatorAdapter()

    def _process(self, data: ProcessedData) -> ProcessedData:
        df = data.dataframe
        try:
            if not isinstance(df, pd.DataFrame):
                raise Exception("dataframe not found in structured_data")

            dataframe = df.copy()

            dataframe["mongo_file_id"] = data.file_id
            dataframe["data_source"] = data.data_source

            if "need_check" not in dataframe.columns:
                dataframe["need_check"] = 0

            allowed_columns = [
                column
                for column in HS_RAW_DATA_INSERT_COLUMNS
                if column in dataframe.columns
            ]

            dataframe = dataframe.loc[:, allowed_columns]
            response_doc = self.saver.save(dataframe)
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.SUCCESS,
                message="Save hs raw data successfully",
                status_code=200,
                result=response_doc,
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]
            data.dataframe = dataframe

            return data
        except Exception as exc:
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.FAILED,
                message="Save hs raw data failed",
                status_code=500,
                error=str(exc),
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]
            return data
