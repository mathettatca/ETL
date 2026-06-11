from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import Any

from airflow.sdk.bases.sensor import BaseSensorOperator
from building_block.utils.logging import info




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
        from building_block.shared.services.google_drive_service import GoogleDriveService
        self.google_drive_service = GoogleDriveService()



    def poke(self, context: dict[str, Any]) -> bool:
        try:
            files = self.google_drive_service.list_files(self.folder_id)
        except Exception as exc:
            if self._is_not_found_error(exc):
                raise Exception("[google_drive_sensor] Google Drive folder/file not found "
                    f"for folder_id={self.folder_id}. Return False."
                )

        file_ids = []
        info(f"execute date: {str(self.execution_date)}")
        for file in files:
            modifiedDate:str = file['modifiedTime'].split("T")[0]
            info(f"modifiledDated: {modifiedDate}")
            if modifiedDate.strip() == self.execution_date.strip():
                info(f"Append file {file['name']}")
                file_ids.append(file['id'])

        if len(file_ids) == 0:
            info(
                "[google_drive_sensor] No new files found "
                f"for execution_date={self.execution_date}"
            )
            return False

        context["ti"].xcom_push(key="file_ids", value=file_ids)
        info(f"[google_drive_sensor] Found {len(file_ids)} new file(s).")
        return True


    @staticmethod
    def _is_not_found_error(exc: Exception) -> bool:
        if isinstance(exc, FileNotFoundError):
            return True

        message = str(exc).lower()
        return "not found" in message or "404" in message
