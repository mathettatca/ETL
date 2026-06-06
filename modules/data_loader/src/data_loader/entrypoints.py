"""Public entrypoints for data_loader."""

from typing import Any

from data_access.application.request.commands.audit_file_download.audit_file_download_command import (
    AuditFileDownloadCommand,
)
from building_block.core.domain.file_model import FileSource
from building_block.utils.logging import info
from data_access.mediator import build_data_access_mediator

from data_loader.applications.models import DownloadResponse
from data_loader.applications.services.downloaders.adapters.file_dispatcher import (
    DownloaderDispatcher,
)


def _require_audit_value(value: Any, field_name: str) -> Any:
    if value is None:
        raise ValueError(f"{field_name} is required for audit file download")
    return value


def _build_audit_file_download_command(
    source: FileSource,
    response: DownloadResponse,
) -> AuditFileDownloadCommand:
    return AuditFileDownloadCommand(
        file_name=_require_audit_value(response.file_name, "file_name"),
        file_local_path=response.file_path,
        file_source=source,
        download_status=response.file_download_status,
        size=response.size,
        drive_file_id=response.id,
        mime_type=_require_audit_value(response.mime_type, "mime_type"),
    )


def _send_audit_file_downloads(
    source: FileSource,
    responses: list[DownloadResponse],
) -> None:
    mediator = build_data_access_mediator()
    audit_failures: list[Exception] = []

    for response in responses:
        command = _build_audit_file_download_command(source, response)
        try:
            mediator.send(command)
        except Exception as exc:
            audit_failures.append(exc)

    if responses and len(audit_failures) == len(responses):
        raise RuntimeError("All file download audit commands failed") from audit_failures[-1]


def run_data_loader(
    file_source: str,
    dest_path: str,
    **kwargs: Any,
) -> list[dict]:
    """
    Load files by dispatching directly to the downloader for file_source.

    Args:
        file_source: Source identifier, for example "google_drive".
        dest_path: Local destination directory.
        **kwargs: Source-specific parameters. Google Drive requires file_id.

    Returns:
        JSON-safe list of download result dictionaries.
    """
    source = FileSource(file_source)
    info(f"Starting data load from {source.value}")

    dispatcher = DownloaderDispatcher()
    file = dispatcher.get_file_info(source, **kwargs)
    responses = dispatcher.download(file=file, dest_path=dest_path, **kwargs)
    _send_audit_file_downloads(source, responses)

    return [response._to_doc() for response in responses]

if __name__ == "__main__":
    # print(f"Run data loader response: "run_data_loader())
    print("Success")
