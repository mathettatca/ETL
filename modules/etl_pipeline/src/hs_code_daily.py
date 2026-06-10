from typing import Any

from building_block.shared.enum.file_source import FileSource
from building_block.shared.enum.supported_file_type import SupportedFileType
from data_loader.entrypoints import run_data_loader
from data_processing.entrypoints import run_data_processing


def run_pipeline(
    file_source: str,
    dest_path: str,
    **kwargs: Any,
) -> bool:
    files = run_data_loader(
        file_source=file_source,
        dest_path=dest_path,
        file_type=SupportedFileType.CSV,
        **kwargs,
    )

    for file in files:
        if not file.dest_path:
            raise ValueError(f"Downloaded file has no dest_path: {file.name}")

        if not file.file_id:
            raise ValueError(f"Downloaded file has no file_id: {file.name}")

        run_data_processing(
            file_path=file.dest_path,
            file_id=file.file_id,
            data_source=file.original,
        )

    return True

if __name__ == "__main__":
    run_pipeline(
        file_source=FileSource.GOOGLE_DRIVE,
        dest_path="test/2026_10_06",
        file_id="1ily-9QVNs6LqPFRqJXH79ktvkZTA1Y4m",
    )