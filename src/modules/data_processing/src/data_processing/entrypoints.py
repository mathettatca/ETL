"""Data Processing application entry-points."""

from datetime import datetime
from pathlib import Path

from building_block.shared.enum.file_source import FileSource
import pandas as pd

from data_processing.domain.models import ProcessedData
from data_processing.application.pipelines.pipeline_factory import (
    build_hscode_pipeline,
    )

def run_data_processing(
    file_path: str,
    file_id:str,
    data_source:FileSource
) -> bool:


    hs_code_pipeline = build_hscode_pipeline()

    dataframe = pd.read_csv(file_path)

    hs_code_pipeline.handle(
        ProcessedData(
            file_id=file_id,
            dataframe=dataframe,
            processed_at=datetime.now(),
            data_source=data_source
        )
    )

    return True


if __name__ == "__main__":
    run_data_processing(
        file_path="/Users/apple/Main/project/DataPipeline/ETL/test/data/2026_06_06/hs511111/detail_Vietnam_import_hs511111_2025-12-01_to_2026-03-31.csv",
        file_id="6a24f4fa9fc8a12469fa5004",
        data_souce=FileSource.GOOGLE_DRIVE
    )