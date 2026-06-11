"""Bootstrap Google Drive OAuth credentials and API client."""

from pathlib import Path
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from building_block.shared.setting import GoogleDriveSetting
from building_block.utils.logging import log_success


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SCOPES = GOOGLE_DRIVE_SCOPES

CLIENT_SECRET_PATH = Path(GoogleDriveSetting.google_credentials_path)
TOKEN_PATH = CLIENT_SECRET_PATH.with_suffix(".token.json")


def save_token(
    creds: Credentials,
    token_path: Path = TOKEN_PATH,
) -> None:
    """Persist OAuth credentials without logging token contents."""
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())


def run_oauth_consent_flow(
    client_secret_path: Path = CLIENT_SECRET_PATH,
    token_path: Path = TOKEN_PATH,
) -> Credentials:
    """Run OAuth consent and save the resulting token."""
    if not client_secret_path.exists():
        raise FileNotFoundError(
            f"Missing OAuth client secret file: {client_secret_path}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        GOOGLE_DRIVE_SCOPES,
    )
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    save_token(creds, token_path=token_path)
    return creds


def load_google_drive_credentials(
    client_secret_path: Path = CLIENT_SECRET_PATH,
    token_path: Path = TOKEN_PATH,
) -> Credentials:
    """Load, refresh, or create Google Drive OAuth credentials."""
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            GOOGLE_DRIVE_SCOPES,
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_token(creds, token_path=token_path)
            return creds
        except RefreshError:
            if token_path.exists():
                token_path.unlink()
            return run_oauth_consent_flow(
                client_secret_path=client_secret_path,
                token_path=token_path,
            )

    return run_oauth_consent_flow(
        client_secret_path=client_secret_path,
        token_path=token_path,
    )


def load_credentials(
    client_secret_path: Path = CLIENT_SECRET_PATH,
    token_path: Path = TOKEN_PATH,
) -> Credentials:
    """Backward-compatible alias for Google Drive credential bootstrap."""
    return load_google_drive_credentials(
        client_secret_path=client_secret_path,
        token_path=token_path,
    )


def initialize_google_drive_service() -> Any:
    """Build a Google Drive API client from bootstrapped OAuth credentials."""
    creds = load_google_drive_credentials()
    service = build(
        "drive",
        "v3",
        credentials=creds,
    )
    log_success("Initialized Google Drive API client from bootstrap credentials")
    return service
