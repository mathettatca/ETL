from types import SimpleNamespace

from google.auth.exceptions import RefreshError

from building_block.shared.scripts import bootstrap_google_drive as bootstrap
from building_block.shared.scripts import initialize_google_drive_service


class FakeCredentials:
    def __init__(
        self,
        valid: bool = False,
        expired: bool = False,
        refresh_token: str | None = None,
        refresh_error: bool = False,
    ):
        self.valid = valid
        self.expired = expired
        self.refresh_token = refresh_token
        self.refresh_error = refresh_error
        self.refreshed = False

    def refresh(self, request):
        if self.refresh_error:
            raise RefreshError("invalid_grant")
        self.refreshed = True
        self.valid = True
        self.expired = False

    def to_json(self) -> str:
        return '{"token": "fake"}'


def test_scripts_package_exports_initialize_entrypoint():
    assert initialize_google_drive_service is bootstrap.initialize_google_drive_service


def test_load_google_drive_credentials_returns_valid_token(monkeypatch, tmp_path):
    token_path = tmp_path / "client_secret.token.json"
    token_path.write_text("{}")
    client_secret_path = tmp_path / "client_secret.json"
    valid_creds = FakeCredentials(valid=True)

    monkeypatch.setattr(
        bootstrap.Credentials,
        "from_authorized_user_file",
        lambda path, scopes: valid_creds,
    )

    creds = bootstrap.load_google_drive_credentials(
        client_secret_path=client_secret_path,
        token_path=token_path,
    )

    assert creds is valid_creds


def test_load_google_drive_credentials_refreshes_expired_token(monkeypatch, tmp_path):
    token_path = tmp_path / "client_secret.token.json"
    token_path.write_text("{}")
    client_secret_path = tmp_path / "client_secret.json"
    expired_creds = FakeCredentials(expired=True, refresh_token="refresh-token")

    monkeypatch.setattr(
        bootstrap.Credentials,
        "from_authorized_user_file",
        lambda path, scopes: expired_creds,
    )

    creds = bootstrap.load_google_drive_credentials(
        client_secret_path=client_secret_path,
        token_path=token_path,
    )

    assert creds is expired_creds
    assert creds.refreshed is True
    assert token_path.read_text() == '{"token": "fake"}'


def test_load_google_drive_credentials_runs_consent_when_refresh_fails(
    monkeypatch,
    tmp_path,
):
    token_path = tmp_path / "client_secret.token.json"
    token_path.write_text("{}")
    client_secret_path = tmp_path / "client_secret.json"
    expired_creds = FakeCredentials(
        expired=True,
        refresh_token="refresh-token",
        refresh_error=True,
    )
    fallback_creds = FakeCredentials(valid=True)

    monkeypatch.setattr(
        bootstrap.Credentials,
        "from_authorized_user_file",
        lambda path, scopes: expired_creds,
    )

    def fake_consent_flow(client_secret_path, token_path):
        assert not token_path.exists()
        return fallback_creds

    monkeypatch.setattr(bootstrap, "run_oauth_consent_flow", fake_consent_flow)

    creds = bootstrap.load_google_drive_credentials(
        client_secret_path=client_secret_path,
        token_path=token_path,
    )

    assert creds is fallback_creds


def test_initialize_google_drive_service_uses_bootstrapped_credentials(monkeypatch):
    creds = FakeCredentials(valid=True)
    built_client = SimpleNamespace(name="drive-client")
    build_calls = []

    def fake_build(service_name, version, credentials):
        build_calls.append((service_name, version, credentials))
        return built_client

    monkeypatch.setattr(bootstrap, "load_google_drive_credentials", lambda: creds)
    monkeypatch.setattr(bootstrap, "build", fake_build)

    service = bootstrap.initialize_google_drive_service()

    assert service is built_client
    assert build_calls == [("drive", "v3", creds)]
