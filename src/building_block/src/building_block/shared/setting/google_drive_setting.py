from typing import ClassVar

from building_block.utils.project_paths import GOOGLE_DRIVE_TOKEN_PATH
from building_block.shared.setting.base_setting import AppBaseSetting


class GoogleDriveSetting(AppBaseSetting):
    google_credentials_path: ClassVar[str] = str(
        GOOGLE_DRIVE_TOKEN_PATH / "client_secret.json"
    )
