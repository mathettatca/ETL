"""Shared project path constants."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[5]
SRC_ROOT = PROJECT_ROOT / "src"
BUILDING_BLOCK_ROOT = SRC_ROOT / "building_block"
ENV_PATH = BUILDING_BLOCK_ROOT / "env" / ".env"
GOOGLE_DRIVE_TOKEN_PATH = BUILDING_BLOCK_ROOT / "google_tokens"
