"""Bootstrap Google Drive service account credentials and API client."""

import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from building_block.utils.logging import log_success


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SCOPES = GOOGLE_DRIVE_SCOPES
SERVICE_ACCOUNT_PATH = Path("google_tokens/client_secret.json")


def initialize_google_drive_service(
    service_account_path: Path | str | None = None,
) -> Any:
    """Load service account credentials and return a Google Drive API client."""
    # Resolve service account credential path from argument, env, or default file.
    credentials_path = Path(
        service_account_path
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        or os.getenv("GOOGLE_CREDENTIALS_PATH")
        or SERVICE_ACCOUNT_PATH
    )

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

    # Build the Google Drive API client with service account credentials.
    service = build(
        "drive",
        "v3",
        credentials=creds,
    )

    # Log successful initialization without exposing private key contents.
    log_success(
        "Initialized Google Drive API client with service account: "
        f"{creds.service_account_email}"
    )
    return service
