"""Bootstrap Google Drive service account credentials and API client."""

import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_PATH = Path("google_tokens/client_secret.json")


def initialize_google_drive_service(
) -> Any:
    """Load service account credentials and return a Google Drive API client."""
    try:
        # Resolve service account credential path from argument, env, or default file.
        credentials_path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH"))

        # Validate service account credential file before building credentials.
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Missing Google service account file: {credentials_path}"
            )

        # Load Google Drive readonly credentials from the service account JSON.
        creds = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=GOOGLE_DRIVE_SCOPES,
        )

        # Build and return the Google Drive API client.
        service = build(
            "drive",
            "v3",
            credentials=creds,
        )

        print(
            "Initialized Google Drive API client "
            f"with service account: {creds.service_account_email}"
        )
        return service

    except Exception:
        print("Failed to initialize Google Drive service with service account")
        raise