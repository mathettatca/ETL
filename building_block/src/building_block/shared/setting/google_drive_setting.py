from pathlib import Path
from pydantic import field_validator

from building_block.shared.setting.base_setting import AppBaseSetting

class GoogleDriveSetting(AppBaseSetting):
    google_credentials_path: str

    @field_validator("google_credentials_path", mode="before")
    @classmethod
    def resolve_path(cls, v) ->str:
        if v is None:
            return v

        path = Path(v)

        # nếu đã là absolute thì giữ nguyên
        if path.is_absolute():
            return path

        # tránh tạo instance mới mỗi lần
        base_path = cls.PROJECT_ROOT

        return str(base_path / path)
