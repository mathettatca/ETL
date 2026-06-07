from building_block.utils.project_paths import GOOGLE_DRIVE_TOKEN_PATH

from building_block.shared.setting.base_setting import AppBaseSetting


class GoogleDriveSetting(AppBaseSetting):
    @property
    def google_credentials_path(self) -> str:
        return str(GOOGLE_DRIVE_TOKEN_PATH / "client_secret.json")
