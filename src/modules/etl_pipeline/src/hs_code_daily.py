import argparse
from typing import Any

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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily HS code pipeline.")
    parser.add_argument("--file-source", required=True)
    parser.add_argument("--dest-path", required=True)
    parser.add_argument("--google-drive-folder-id")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(
        file_source=args.file_source,
        dest_path=args.dest_path,
        google_drive_folder_id=args.google_drive_folder_id,
    )
