"""Google Drive downloader implementation."""

import os
from datetime import datetime

from building_block.core.domain.file_model import FileDownloadStatus
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.shared.services.filer_service.adapters.google_drive_file_service import (
    GoogleDriveFileService,
)
from building_block.shared.services.filer_service.ports.IFIleService import (
    IFileService,
)
from building_block.shared.services.google_drive_service import GoogleDriveServiceProxy
from building_block.utils.file_utils import resolve_file_dest_path
from building_block.utils.logging import debug, info, log_error, log_success
from building_block.utils.mappers import GoogleDriveFileMapper

from data_loader.applications.models import DownloadResponse


class GoogleDriveDownloader:
    """Downloader implementation for Google Drive."""

    def __init__(self) -> None:
        self.db_file_service: IFileService[GoogleDriveFile] = GoogleDriveFileService()
        self.service = GoogleDriveServiceProxy()

    def download(
        self,
        file: GoogleDriveFile,
        dest_path: str,
        **kwargs,
    ) -> list[DownloadResponse]:
        local_path = resolve_file_dest_path(file.name, dest_path)
        responses: list[DownloadResponse] = []
        self._download_handler(file, local_path, responses)
        return responses

    def _download_handler(
        self,
        file_model: GoogleDriveFile,
        dest_path: str,
        responses: list[DownloadResponse],
    ) -> str | None:
        if file_model.mime_type == "application/vnd.google-apps.folder":
            os.makedirs(dest_path, exist_ok=True)
            files_metadata = self.service.list_files(file_id=file_model.drive_file_id)

            for child_metadata in files_metadata:
                child_file = GoogleDriveFileMapper.to_model(child_metadata)
                child_dest_path = os.path.join(dest_path, child_file.name)
                self._download_handler(child_file, child_dest_path, responses)

            log_success(f"Downloaded folder {file_model.name} to {dest_path}")
            return dest_path

        if not file_model.name.lower().endswith(".csv"):
            info(f"Skip non-xlsx file: {file_model.name}")
            return None

        try:
            local_path = dest_path
            if not os.path.exists(local_path):
                local_path = self.service.download_file(
                    file_model.drive_file_id,
                    local_path,
                )
                info("Convert Data to Model")
                file_response: GoogleDriveFile = file_model.model_copy(
                    update={
                        "dest_path": local_path,
                        "date_download": datetime.now(),
                        "download_status": FileDownloadStatus.SUCCESS,
                    }
                )
                info(f"Finish download file {file_model.name}")
                self.db_file_service.save(file_response)

            responses.append(
                DownloadResponse(
                    id=file_model.drive_file_id or "",
                    file_path=local_path,
                    file_download_status=FileDownloadStatus.SUCCESS,
                    file_name=file_model.name,
                    mime_type=file_model.mime_type,
                    size=file_model.size_bytes,
                )
            )
            log_success(
                f"Downloaded file {file_model.name} from Google Drive to {local_path}"
            )
            return local_path
        except Exception as e:
            file_response = file_model.model_copy(
                update={
                    "date_download": datetime.now(),
                    "download_status": FileDownloadStatus.FAILED,
                }
            )
            debug(f"Failed to download file {file_model.name}: {str(e)}")
            self.db_file_service.save(file_response)

            responses.append(
                DownloadResponse(
                    id=file_model.drive_file_id or "",
                    file_path="",
                    file_download_status=FileDownloadStatus.FAILED,
                    file_name=file_model.name,
                    mime_type=file_model.mime_type,
                    size=file_model.size_bytes,
                )
            )
            log_error(f"Failed to download file {file_model.name}: {str(e)}")
            return None

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
