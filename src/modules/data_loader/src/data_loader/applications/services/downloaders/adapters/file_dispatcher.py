"""File dispatcher using Registry pattern."""

from building_block.core.domain.file_model import FileModel as BaseFileModel, FileSource
from building_block.utils.logging import log_success

from data_loader.applications.services.downloaders import GoogleDriveDownloader
from data_loader.applications.services.downloaders.ports.downloader import Downloader


class DownloaderDispatcher:
    """
    Registry-based dispatcher.
    Maps FileSource -> Downloader implementation.
    No if/elif chain: add new source by registering it.
    """

    def __init__(self):
        self._registry: dict[FileSource, Downloader] = {}
        self.regist_all()

    def register(self, source: FileSource, downloader: Downloader) -> None:
        """
        Register a downloader for a source type.

        Args:
            source: FileSource enum value
            downloader: Downloader implementation
        """
        self._registry[source] = downloader
        log_success(f"Registered downloader for {source.value}")

    def download(
        self,
        file: BaseFileModel,
        dest_path: str,
        file_type,
        **kwargs,
    ) -> list[BaseFileModel]:
        """
        Look up registry and call the appropriate downloader.

        Args:
            file: File to download
            dest_path: Local destination path
            **kwargs: Downloader-specific parameters forwarded to
                Downloader.download (and parse_param).

        Returns:
            List of downloaded file domain models with local path and status.

        Raises:
            ValueError: If source is not registered
        """
        handler = self._registry.get(file.original)
        if handler is None:
            registered_sources = [s.value for s in self._registry.keys()]
            raise ValueError(
                f"No downloader registered for source: {file.original.value}. "
                f"Registered sources: {registered_sources}"
            )
        return handler.download(file, dest_path,file_type, **kwargs)

    def get_file_info(self, source: FileSource, **kwargs) -> BaseFileModel:
        """
        Get file info from source.

        Args:
            source: FileSource enum value
            **kwargs: Source-specific lookup parameters.

        Returns:
            File model from the registered downloader.

        Raises:
            ValueError: If source is not registered
        """
        handler = self._registry.get(source)
        if handler is None:
            registered_sources = [s.value for s in self._registry.keys()]
            raise ValueError(
                f"No downloader registered for source: {source.value}. "
                f"Registered sources: {registered_sources}"
            )
        return handler.get_file_info(**kwargs)

    def is_registered(self, source: FileSource) -> bool:
        """Check if a source is registered."""
        return source in self._registry

    def get_registered_sources(self) -> list[str]:
        """Get list of registered source names."""
        return [s.value for s in self._registry.keys()]

    def regist_all(self) -> None:
        """Register all downloader sources from application downloaders."""
        self.register(FileSource.GOOGLE_DRIVE, GoogleDriveDownloader())
