"""Google Drive service stage wrapper."""

import os
from typing import Any

from building_block.shared.scripts.bootstrap_google_drive import initialize_google_drive_service
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

from building_block.utils.logging import info, log_success


class GoogleDriveService:
    """
    Singleton Google Drive API stage wrapper.

    OAuth/token lifecycle is handled by
    building_block.shared.scripts.bootstrap_google_drive.
    """

    _instance: "GoogleDriveService | None" = None
    _service: Any = None

    def __new__(cls, *args, **kwargs) -> "GoogleDriveService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, service: Any | None = None) -> None:
        """Initialize the wrapper with an already-authenticated Drive client."""
        if getattr(self, "_initialized", False):
            if service is not None:
                self._service = service
                log_success("Updated Google Drive API stage client")
            return

        if service is None:
            initialize_google_drive_service()

        self._service = service
        self._initialized = True
        log_success("Initialized Google Drive API stage client")

    @property
    def service(self) -> Any:
        """Get the Google Drive service client."""
        if self._service is None:
            raise RuntimeError("Google Drive API stage client is not initialized")
        return self._service

    def download_file(
        self, file_id: str, dest_path: str, chunk_size: int = 1024 * 1024
    ) -> str:
        """
        Download a file from Google Drive with streaming to disk.
        Writes data in chunks to avoid memory overflow for large files.
        Shows progress using tqdm progress bar.
        """
        try:
            file_metadata = self.get_file_metadata(file_id)
            total_size = int(file_metadata.get("size", 0))
            file_name = file_metadata.get("name", "Unknown")

            request = self.service.files().get_media(fileId=file_id)
            os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)

            with open(dest_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request, chunksize=chunk_size)

                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=file_name,
                ) as pbar:
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            bytes_downloaded = int(status.resumable_progress)
                            pbar.update(bytes_downloaded - pbar.n)

            return dest_path
        except Exception as e:
            raise RuntimeError(f"Failed to download file from Google Drive: {e}")

    def list_files(
        self,
        file_id: str | None = None,
        max_results: int = 100,
    ) -> list[dict]:
        """
        List files in a Google Drive folder.

        Args:
            file_id: Google Drive folder/file ID used as parent container.
            max_results: Maximum number of results to return.
        """
        try:
            info(f"Google Drive file_id: {file_id}")
            query = f"'{file_id}' in parents and trashed=false"
            request = self.service.files().list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, createdTime, modifiedTime, size)",
                pageSize=max_results,
            )
            results = request.execute()
            return results.get("files", [])
        except Exception as e:
            raise RuntimeError(f"Failed to list files from Google Drive: {e}")

    def get_file_metadata(self, file_id: str) -> dict:
        """Get metadata for a specific file."""
        try:
            request = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, createdTime, modifiedTime, size, parents",
            )
            return request.execute()
        except Exception as e:
            raise RuntimeError(f"Failed to get file metadata from Google Drive: {e}")

    def get_file_by_name(self, name: str) -> str:
        """Get the first non-trashed Google Drive folder ID by name."""
        query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"name='{name}' "
            "and trashed=false"
        )
        results = (
            self.service.files()
            .list(
                q=query,
                fields="files(id, name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora="allDrives",
            )
            .execute()
        )
        folders = results.get("files", [])
        if not folders:
            raise Exception(f"Khong tim thay folder name '{name}'")

        return folders[0]["id"]

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton stage wrapper."""
        cls._instance = None
        cls._service = None
