"""File loading downloaders."""

from data_loader.applications.services.downloaders.adapters.google_drive_downloader import (
    GoogleDriveDownloader,
)
from data_loader.applications.services.downloaders.adapters.file_dispatcher import (
    DownloaderDispatcher,
)

__all__ = ["DownloaderDispatcher", "GoogleDriveDownloader"]
