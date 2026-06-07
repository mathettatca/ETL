"""Google Drive service integration."""

import json
import os
from pathlib import Path
from typing import Any
from building_block.shared.setting import GoogleDriveSetting
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm

from building_block.utils.logging import info, log_success


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class GoogleDriveService:
    """
    Singleton Google Drive API client.
    Manages authentication and provides methods for interacting with Google Drive.
    """

    _instance: "GoogleDriveService | None" = None
    _service: Any = None

    def __new__(cls) -> "GoogleDriveService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Google Drive API client."""
        if getattr(self, "_initialized", False):
            return

        try:
            setting = GoogleDriveSetting()
            cred_path = setting.google_credentials_path
            creds = self._load_credentials(cred_path)
            self._service = build("drive", "v3", credentials=creds)
            self._initialized = True
            log_success("Connected to Google Drive API successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Drive service: {e}")

    def _load_credentials(self, credentials_path: str) -> Any:
        """Load either service-account credentials or OAuth client credentials."""
        credentials_file = Path(credentials_path)
        credentials_info = json.loads(credentials_file.read_text())

        if credentials_info.get("type") == "service_account":
            return ServiceAccountCredentials.from_service_account_file(
                str(credentials_file),
                scopes=GOOGLE_DRIVE_SCOPES,
            )

        if "installed" in credentials_info or "web" in credentials_info:
            return self._load_oauth_credentials(credentials_file)

        raise ValueError(
            "Unsupported Google credentials format. Expected service account JSON "
            "or OAuth client JSON with 'installed'/'web' key."
        )

    def _load_oauth_credentials(self, credentials_file: Path) -> OAuthCredentials:
        """Load cached OAuth token, refresh it, or create a new token from client secrets."""
        token_path = Path(
            os.getenv(
                "GOOGLE_TOKEN_PATH",
                str(credentials_file.with_name(f"{credentials_file.stem}.token.json")),
            )
        )

        creds = None
        if token_path.exists():
            creds = OAuthCredentials.from_authorized_user_file(
                str(token_path),
                GOOGLE_DRIVE_SCOPES,
            )

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file),
                GOOGLE_DRIVE_SCOPES,
            )
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        return creds

    @property
    def service(self) -> Any:
        """Get the Google Drive service instance."""
        if self._service is None:
            raise RuntimeError("Google Drive service not initialized")
        return self._service

    def download_file(
        self, file_id: str, dest_path: str, chunk_size: int = 1024 * 1024
    ) -> str:
        """
        Download a file from Google Drive with streaming to disk.
        Writes data in chunks to avoid memory overflow for large files.
        Shows progress using tqdm progress bar.

        Args:
            file_id: Google Drive file ID
            dest_path: Local destination path
            chunk_size: Size of each chunk to write (default 1MB = 1024*1024 bytes)

        Returns:
            Local file path
        """
        try:
            # Get file metadata to get total size
            file_metadata = self.get_file_metadata(file_id)
            total_size = int(file_metadata.get("size", 0))
            file_name = file_metadata.get("name", "Unknown")

            request = self.service.files().get_media(fileId=file_id)
             
            os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)

            # Stream download directly to disk with progress bar
            with open(dest_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request, chunksize=chunk_size)

                with tqdm(total=total_size, unit="B", unit_scale=True, desc=file_name) as pbar:
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            # Update progress bar with bytes downloaded in this chunk
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
        UPDATE , request query_string
        List files in a Google Drive folder.

        Args:
            file_id: Google Drive folder/file ID used as parent container.
            max_results: Maximum number of results to return

        Returns:
            List of file metadata dictionaries
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
        
    def get_file_by_name(self, name: str) -> dict:
        """
        step1: build_query

        step2: execute_query
            step2.1: call drive api list with query
            step2.2: extract files from response

        step3: validate_result
            step3.1: ensure at least one folder exists
            step3.2: ensure only one folder matches

        step4: return_result
            step4.1: return first folder
        """

        # step1.1 + step1.2 + step1.3: build query
        query = (
            "mimeType='application/vnd.google-apps.folder' "
            f"name='{name}' "
            "and trashed=false"
        )

        # step2.1: call drive api list with query
        results = self.service.files().list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives",
        ).execute()

        # step2.2: extract files from response
        folders = results.get("files", [])

        # step3.1: ensure at least one folder exists
        if not folders:
            raise Exception(f"Khong tim thay folder name '{name}'")


        # step4.1: return first folder
        return folders[0]["id"]

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None
        cls._service = None


# Convenient global reference