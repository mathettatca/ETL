from __future__ import annotations

import importlib.util
import logging
import os
from pathlib import Path
from typing import Any

from airflow.sdk.bases.sensor import BaseSensorOperator

logger = logging.getLogger(__name__)


def _load_google_drive_service() -> Any:
    bootstrap_script_path = Path(
        os.environ.get(
            "GOOGLE_DRIVE_BOOTSTRAP_SCRIPT",
            str(
                Path(__file__).resolve().parents[2]
                / "scripts"
                / "bootstrap_google_drive.py"
            ),
        )
    )
    spec = importlib.util.spec_from_file_location(
        "google_drive_bootstrap",
        bootstrap_script_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Cannot load Google Drive bootstrap script: {bootstrap_script_path}"
        )

    bootstrap_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap_module)
    return bootstrap_module.initialize_google_drive_service()


class GoogleDriveSensor(BaseSensorOperator):
    template_fields = ("folder_id", "execution_date")

    def __init__(
        self,
        *,
        folder_id: str,
        execution_date: str,
        max_results: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.folder_id = folder_id
        self.execution_date = execution_date
        self.max_results = max_results

    def poke(self, context: dict[str, Any]) -> bool:
        try:
            service = _load_google_drive_service()
            response = (
                service.files()
                .list(
                    q=f"'{self.folder_id}' in parents and trashed=false",
                    spaces="drive",
                    fields="files(id, name, mimeType, createdTime, modifiedTime, size)",
                    pageSize=self.max_results,
                )
                .execute()
            )
            files = response.get("files", [])
        except Exception as exc:
            if self._is_not_found_error(exc):
                raise Exception(
                    "[google_drive_sensor] Google Drive folder/file not found "
                    f"for folder_id={self.folder_id}. Return False."
                ) from exc
            raise

        file_ids = []
        logger.info("execute date: %s", self.execution_date)
        for file in files:
            modifiedDate: str = file["modifiedTime"].split("T")[0]
            logger.info("modifiledDated: %s", modifiedDate)
            if modifiedDate.strip() == self.execution_date.strip():
                logger.info("Append file %s", file["name"])
                file_ids.append(file["id"])

        if len(file_ids) == 0:
            logger.info(
                "[google_drive_sensor] No new files found "
                "for execution_date=%s",
                self.execution_date,
            )
            return False

        context["ti"].xcom_push(key="file_ids", value=file_ids)
        logger.info("[google_drive_sensor] Found %s new file(s).", len(file_ids))
        return True

    @staticmethod
    def _is_not_found_error(exc: Exception) -> bool:
        if isinstance(exc, FileNotFoundError):
            return True

        message = str(exc).lower()
        return "not found" in message or "404" in message
