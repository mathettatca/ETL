"""Google Drive downloader implementation."""

import os
from datetime import datetime

from building_block.core.domain.file_model import FileDownloadStatus
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.shared.scripts.bootstrap_google_drive import (
    initialize_google_drive_service,
)
from building_block.shared.services.google_drive_service import GoogleDriveService
from building_block.utils.file_utils import _is_supported_file_type, resolve_file_dest_path
from building_block.utils.logging import debug, info, log_error, log_success
from building_block.utils.mappers import GoogleDriveFileMapper


class GoogleDriveDownloader:
    """Downloader implementation for Google Drive."""

    def __init__(self) -> None:
        drive_client = initialize_google_drive_service()
        self.service = GoogleDriveService(service=drive_client)

    def download(
        self,
        file: GoogleDriveFile,
        dest_path: str,
        file_type:str,
        **kwargs,
    ) -> list[GoogleDriveFile]:
        local_path = resolve_file_dest_path(file.name, dest_path)
        info(f"[Google Drive Downloader] Download Folder localPath: {local_path}")
        downloaded_files: list[GoogleDriveFile] = []
        self._download_handler(file, local_path,file_type, downloaded_files)
        return downloaded_files

    def _download_handler(
        self,
        gdrive_file: GoogleDriveFile,
        dest_path: str,
        file_type:str,
        downloaded_files: list[GoogleDriveFile],
    ) -> GoogleDriveFile | None:
        if gdrive_file.mime_type == "application/vnd.google-apps.folder":
            os.makedirs(dest_path, exist_ok=True)
            files_metadata = self.service.list_files(file_id=gdrive_file.drive_file_id)

            for child_metadata in files_metadata:
                child_file = GoogleDriveFileMapper.to_model(child_metadata)
                child_dest_path = os.path.join(dest_path, child_file.name)
                self._download_handler(child_file, child_dest_path, file_type, downloaded_files)

            log_success(f"Downloaded folder {gdrive_file.name} to {dest_path}")
            return None

        if not _is_supported_file_type(file_name=gdrive_file.name, file_type=file_type):
            return None
        local_file = gdrive_file.model_dump()
        file_existed_before_download = os.path.exists(dest_path)
        info(f"[Google Drive Downloader]: local_path :{dest_path}")
        try:
            local_path = self.service.download_file(
                gdrive_file.drive_file_id,
                dest_path,
            )
            local_file["dest_path"] = local_path
            if file_existed_before_download:
                local_file["download_status"] = FileDownloadStatus.UPDATE
                local_file["date_update"] = datetime.now()
            else:
                local_file["download_status"] = FileDownloadStatus.SUCCESS
                local_file["date_download"] = datetime.now()

            file_response = GoogleDriveFile(**local_file)
            log_success(
                f"Downloaded file {gdrive_file.name} from Google Drive to {local_path}"
            )
            return file_response
        except Exception as e:
            local_file["dest_path"] = dest_path
            local_file["date_download"] = datetime.now()
            local_file["download_status"] = FileDownloadStatus.FAILED
            file_response = GoogleDriveFile(**local_file)
            debug(f"Failed to download file {gdrive_file.name}: {str(e)}")
            log_error(f"Failed to download file {gdrive_file.name}: {str(e)}")
            return file_response
        finally:
            downloaded_files.append(file_response)

    def get_file_info(self, **kwargs) -> GoogleDriveFile:
        file_id = kwargs.get("file_id", None)
        if file_id is None:
            raise Exception(f"{file_id} is None")

        files_metadata: dict = self.service.get_file_metadata(file_id)
        if not files_metadata:
            raise FileNotFoundError("Google Drive file not found with query")

        return GoogleDriveFileMapper.to_model(files_metadata)

    def list_files(self, **kwargs) -> GoogleDriveFile:
        file_id = kwargs.get("file_id", None)
        if file_id is None:
            raise Exception(f"{file_id} is None")
        fields = kwargs.get(
            "fields",
            "files(id, name, mimeType, size, createdTime)",
        )

        if file_id is not None:
            query = f"'{file_id}' in parents and trashed = false"

        files_metadata = self.service.execute_query(query=query, fields=fields)
        if not files_metadata:
            raise FileNotFoundError(f"Google Drive file not found with query: {query}")

        file_metadata = files_metadata[0]
        return GoogleDriveFileMapper.to_model(file_metadata)
