"""Base settings for the entire application."""

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

from building_block.utils.project_paths import ENV_PATH

class AppBaseSetting(BaseSettings):
    """
    Base class for all settings in the system.
    Pydantic-settings automatically reads from environment variables.
    Subclasses only need to declare fields.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        case_sensitive=False,
        extra="ignore"
    )
