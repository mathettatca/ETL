"""Shared project path constants."""

from pathlib import Path


def _find_project_root(start: Path) -> Path:
    for path in (start, *start.parents):
        if (path / "pyproject.toml").is_file() and (path / "docker-compose.yml").is_file():
            return path
    raise RuntimeError(f"Could not find project root from {start}")


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())
SRC_ROOT = PROJECT_ROOT / "src"
BUILDING_BLOCK_ROOT = SRC_ROOT / "building_block"
ENV_PATH = BUILDING_BLOCK_ROOT / "env" / ".env"
GOOGLE_DRIVE_TOKEN_PATH = BUILDING_BLOCK_ROOT / "google_tokens"
