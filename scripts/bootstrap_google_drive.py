"""Bootstrap Google Drive OAuth credentials and API client."""

import argparse
import logging
import os
from pathlib import Path
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SCOPES = GOOGLE_DRIVE_SCOPES

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _default_client_secret_path() -> Path:
    return Path(
        os.environ.get(
            "GOOGLE_CREDENTIALS_PATH",
            os.environ.get(
                "GOOGLE_APPLICATION_CREDENTIALS",
                "google_tokens/client_secret.json",
            ),
        )
    )


CLIENT_SECRET_PATH = _default_client_secret_path()
TOKEN_PATH = Path(
    os.environ.get(
        "GOOGLE_TOKEN_PATH",
        str(CLIENT_SECRET_PATH.with_suffix(".token.json")),
    )
)


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
        host=os.environ.get("GOOGLE_OAUTH_REDIRECT_HOST", "localhost"),
        bind_addr=os.environ.get("GOOGLE_OAUTH_BIND_ADDR", "0.0.0.0"),
        port=int(os.environ.get("GOOGLE_OAUTH_REDIRECT_PORT", "8090")),
        open_browser=_env_bool("GOOGLE_OAUTH_OPEN_BROWSER", default=False),
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
    logger.info("Initialized Google Drive API client from bootstrap credentials")
    return service


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap Google Drive OAuth token."
    )
    parser.add_argument(
        "--client-secret-path",
        default=str(CLIENT_SECRET_PATH),
        help="Path to Google OAuth client_secret.json.",
    )
    parser.add_argument(
        "--token-path",
        default=str(TOKEN_PATH),
        help="Path where the OAuth token JSON will be stored.",
    )
    args = parser.parse_args()

    token_path = Path(args.token_path)
    load_google_drive_credentials(
        client_secret_path=Path(args.client_secret_path),
        token_path=token_path,
    )
    print(f"Google Drive token ready: {token_path}")


if __name__ == "__main__":
    main()
