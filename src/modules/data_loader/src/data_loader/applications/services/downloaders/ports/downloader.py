"""Downloader port for the file loading feature."""

from typing import Protocol

from building_block.core.domain.file_model import FileModel


class Downloader(Protocol):
    def download(
        self,
        file: FileModel,
        dest_path: str,
        file_type:str,
        **kwargs,
    ) -> list[FileModel]:
        ...

    def get_file_info(self, **kwargs) -> FileModel:
        ...
