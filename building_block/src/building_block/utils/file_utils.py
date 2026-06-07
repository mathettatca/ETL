import os

from building_block.shared.setting.base_setting import AppBaseSetting
from .project_paths import PROJECT_ROOT
from building_block.utils.logging import info
import os
from pathlib import Path


def resolve_file_dest_path(file_name: str, dest_path: str) -> str:
    dest = Path(dest_path)

    # Nếu dest_path là absolute path thì giữ nguyên
    # Nếu là relative path thì gắn thêm PROJECT_ROOT
    if not dest.is_absolute():
        dest = PROJECT_ROOT / dest

    # Case 1: dest_path là folder
    # Ví dụ: "output/" hoặc "/app/output/"
    if str(dest_path).endswith(os.sep) or dest.is_dir():
        full_path = dest / file_name
        info(f"Full path: {full_path}")

        dest.mkdir(parents=True, exist_ok=True)
        return str(full_path)

    dest_name = dest.name

    # Case 2: dest_path là full file path
    # Ví dụ: "output/data.csv" hoặc file_name trùng với dest_name
    if dest_name == file_name or dest.suffix:
        info(f"Full path: {dest}")

        dest.parent.mkdir(parents=True, exist_ok=True)
        return str(dest)

    # Case 3: dest_path là folder nhưng chưa tồn tại
    # Ví dụ: "output/data"
    full_path = dest / file_name
    info(f"Full path: {full_path}")

    dest.mkdir(parents=True, exist_ok=True)
    return str(full_path)