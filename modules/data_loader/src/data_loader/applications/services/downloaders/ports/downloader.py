"""Downloader port for the file loading feature."""

from typing import Protocol

from building_block.core.domain.file_model import FileModel
from data_loader.applications.models import DownloadResponse


class Downloader(Protocol):
    def download(
        self,
        file: FileModel,
        dest_path: str,
        **kwargs,
    ) -> list[DownloadResponse]:
        ...

    def get_file_info(self, **kwargs) -> FileModel:
        ...
