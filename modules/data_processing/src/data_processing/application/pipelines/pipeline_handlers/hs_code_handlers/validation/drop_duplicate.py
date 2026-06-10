from data_processing.domain.models.base_handler import BaseProcessingHandler
from data_processing.domain.models.processed_data import ProcessedData
from building_block.core.domain.processing_step import ProcessingStep, ProcessingStepStatus
import pandas as pd


class DropDuplicationHandler(BaseProcessingHandler):
    step_name = "drop_duplication"
    def _process(self, data: ProcessedData) -> ProcessedData:
        df = data.dataframe
        try:
            # add count of duplicates per key
            df["count"] = (
                df.groupby(["stt", "segment", "page"])["stt"].transform("size")
            )

            duplicates_exist = (df["count"] > 1).any()
            if duplicates_exist:
                csv_file = getattr(data, "csv_file", None)
                if csv_file is not None and hasattr(csv_file, "name"):
                    print(f"Duplicate found in file: {csv_file.name}")
                else:
                    print(f"Duplicate found in file: {getattr(data, 'file_id', 'unknown')}")

                before = len(df)
                df = df.drop_duplicates(subset=["stt", "segment", "page"], keep="first")
                after = len(df)
                dropped = before - after
            else:
                dropped = 0

            if "count" in df.columns:
                df = df.drop(columns=["count"])

            data.dataframe = df

            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.SUCCESS,
                message="Drop duplication successfully",
                status_code=200,
                result={"dropped_count": int(dropped)},
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]

            return data
        except Exception as exc:
            proccessing_step: ProcessingStep = ProcessingStep(
                status=ProcessingStepStatus.FAILED,
                message="Drop duplication failed",
                status_code=500,
                error=str(exc),
            )
            data.processing_steps = data.processing_steps + [
                {self.step_name: proccessing_step}
            ]
            return data