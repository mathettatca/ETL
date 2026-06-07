"""Shared project path constants."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = PROJECT_ROOT / "src"
ENV_PATH = PROJECT_ROOT /"building_block" /"env" /".env"
GOOGLE_DRIVE_TOKEN_PATH = PROJECT_ROOT /"building_block"/ "google_tokens"