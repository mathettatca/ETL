"""Public entrypoints for data_loader."""

from typing import Any

from building_block.utils.file_utils import _is_supported_file_type
from data_access.application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
)
from building_block.core.domain.file_model import FileModel, FileSource
from building_block.core.domain.google_drive_file_model import GoogleDriveFile
from building_block.utils.logging import info, log_error
from data_access.mediator import Mediator

from data_loader.applications.services.downloaders.adapters.file_dispatcher import (
    DownloaderDispatcher,
)


def _require_audit_value(value: Any, field_name: str) -> Any:
    if value is None:
        raise ValueError(f"{field_name} is required for audit file download")
    return value


def _build_audit_file_download_command(
    model: FileModel,
) -> AuditFileDownloadCommand:
    extra_fields: dict[str, Any] = {}
    size: int | None = None

    if isinstance(model, GoogleDriveFile):
        size = model.size_bytes
        extra_fields = {
            "drive_file_id": _require_audit_value(
                model.drive_file_id,
                "drive_file_id",
            ),
            "mime_type": _require_audit_value(model.mime_type, "mime_type"),
        }

    return AuditFileDownloadCommand(
        file_name=_require_audit_value(model.name, "file_name"),
        file_local_path=_require_audit_value(model.dest_path, "dest_path"),
        file_source=model.original,
        download_status=model.download_status,
        size=size,
        **extra_fields,
    )


def _send_audit_file_downloads(
    responses: list[FileModel],
) -> None:
    mediator = Mediator()
    results: list[FileModel] = []

    for response in responses:
        command = _build_audit_file_download_command(response)
        result:dict = mediator.send(command)

        # start with the file model doc and attach inserted_id when available
        response.file_id = result.get("inserted_id")
        results.append(response)

    return results
        
def run_data_loader(
    file_source: str,
    dest_path: str,
    file_type:str,
    **kwargs: Any,
) -> list[FileModel]:
    """
    Load files by dispatching directly to the downloader for file_source.

    Args:
        file_source: Source identifier, for example "google_drive".
        dest_path: Local destination directory.
        **kwargs: Source-specific parameters. Google Drive requires file_id.

    Returns:
        List of downloaded file models.
    """
    source = FileSource(file_source)
    info(f"Starting data load from {source.value}")
    dispatcher = DownloaderDispatcher()
    file = dispatcher.get_file_info(source, **kwargs)
    responses = dispatcher.download(file=file, dest_path=dest_path, file_type=file_type, **kwargs)
    responses_with_audit = _send_audit_file_downloads(responses)

    return responses_with_audit

if __name__ == "__main__":
    response: list[FileModel] = run_data_loader(
        file_source=FileSource.GOOGLE_DRIVE.value,
        dest_path="test/data/2026_06_10/",  # xài đường dẫn tương đối thì ko thêm "/" phía trc
        file_id="1ily-9QVNs6LqPFRqJXH79ktvkZTA1Y4m",
    )
    print(f"Run data loader response: {response}")
