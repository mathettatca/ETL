#!/usr/bin/env bash
# Move building_block and modules under ./src without changing Python imports.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

AIRFLOW_SRC="/opt/airflow/src"
RUNTIME_PYTHONPATH="${AIRFLOW_SRC}:${AIRFLOW_SRC}/building_block/src:${AIRFLOW_SRC}/modules/data_access/src:${AIRFLOW_SRC}/modules/data_loader/src:${AIRFLOW_SRC}/modules/data_processing/src:${AIRFLOW_SRC}/modules/etl_pipeline/src"
LOCAL_PYTHONPATH="src:src/building_block/src:src/modules/data_access/src:src/modules/data_loader/src:src/modules/data_processing/src:src/modules/etl_pipeline/src"

log() {
  printf '\n--> %s\n' "$1"
}

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

replace_file_text() {
  local file="$1"
  local from="$2"
  local to="$3"

  [[ -f "${file}" ]] || fail "Missing file: ${file}"
  perl -0pi -e "s#\Q${from}\E#${to}#g" "${file}"
}

move_dir_once() {
  local source="$1"
  local target="$2"

  if [[ -d "${source}" && ! -e "${target}" ]]; then
    mkdir -p "$(dirname "${target}")"
    mv "${source}" "${target}"
    printf '    moved %s -> %s\n' "${source}" "${target}"
    return
  fi

  if [[ ! -e "${source}" && -d "${target}" ]]; then
    printf '    already moved: %s\n' "${target}"
    return
  fi

  if [[ -e "${source}" && -e "${target}" ]]; then
    fail "Both ${source} and ${target} exist. Resolve this partial migration first."
  fi

  fail "Missing source ${source} and target ${target}"
}

log "Validate current layout"
[[ -f pyproject.toml ]] || fail "Run this script from the project root"
[[ -f Dockerfile ]] || fail "Missing Dockerfile"
[[ -f docker-compose.yml ]] || fail "Missing docker-compose.yml"

log "Move directories under src"
mkdir -p src
move_dir_once "building_block" "src/building_block"
move_dir_once "modules" "src/modules"

log "Update uv workspace paths"
replace_file_text "pyproject.toml" '"building_block",' '"src/building_block",'
replace_file_text "pyproject.toml" '"modules/data_access",' '"src/modules/data_access",'
replace_file_text "pyproject.toml" '"modules/data_loader",' '"src/modules/data_loader",'
replace_file_text "pyproject.toml" '"modules/data_processing",' '"src/modules/data_processing",'
replace_file_text "pyproject.toml" '"modules/etl_pipeline",' '"src/modules/etl_pipeline",'
perl -0pi -e 's#\n    "etl_pipeline",##g' pyproject.toml

if [[ -f uv.lock ]]; then
  log "Update uv lock editable paths"
  replace_file_text "uv.lock" 'editable = "building_block"' 'editable = "src/building_block"'
  replace_file_text "uv.lock" 'editable = "modules/data_access"' 'editable = "src/modules/data_access"'
  replace_file_text "uv.lock" 'editable = "modules/data_loader"' 'editable = "src/modules/data_loader"'
  replace_file_text "uv.lock" 'editable = "modules/data_processing"' 'editable = "src/modules/data_processing"'
  replace_file_text "uv.lock" 'editable = "modules/etl_pipeline"' 'editable = "src/modules/etl_pipeline"'
fi

log "Update Airflow PYTHONPATH"
perl -0pi -e "s#PYTHONPATH: .*#PYTHONPATH: ${RUNTIME_PYTHONPATH}#g" docker-compose.yml

log "Update Dockerfile workspace metadata copy"
if ! grep -q 'COPY src/building_block/pyproject.toml ./src/building_block/pyproject.toml' Dockerfile; then
  perl -0pi -e 's#COPY pyproject\.toml uv\.lock\* \./#COPY pyproject.toml uv.lock* ./\nCOPY src/building_block/pyproject.toml ./src/building_block/pyproject.toml\nCOPY src/modules/data_access/pyproject.toml ./src/modules/data_access/pyproject.toml\nCOPY src/modules/data_loader/pyproject.toml ./src/modules/data_loader/pyproject.toml\nCOPY src/modules/data_processing/pyproject.toml ./src/modules/data_processing/pyproject.toml\nCOPY src/modules/etl_pipeline/pyproject.toml ./src/modules/etl_pipeline/pyproject.toml#g' Dockerfile
fi

log "Update first-run Google token paths"
replace_file_text "scripts/first-run.sh" "building_block/google_tokens/client_secret.json" "src/building_block/google_tokens/client_secret.json"

log "Update shared project path constants"
PROJECT_PATHS="src/building_block/src/building_block/utils/project_paths.py"
[[ -f "${PROJECT_PATHS}" ]] || fail "Missing ${PROJECT_PATHS}"
cat > "${PROJECT_PATHS}" <<'PY'
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
PY

log "Create pytest path bootstrap"
mkdir -p test
cat > test/conftest.py <<'PY'
"""Test path bootstrap for the src-hosted monorepo layout."""

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
PATHS = [
    ROOT_DIR / "src",
    ROOT_DIR / "src" / "building_block" / "src",
    ROOT_DIR / "src" / "modules" / "data_access" / "src",
    ROOT_DIR / "src" / "modules" / "data_loader" / "src",
    ROOT_DIR / "src" / "modules" / "data_processing" / "src",
    ROOT_DIR / "src" / "modules" / "etl_pipeline" / "src",
    ROOT_DIR / "src" / "modules" / "data_access" / "src" / "data_access",
]

for path in reversed(PATHS):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)
PY

log "Migration complete"
printf 'Local test PYTHONPATH:\n  %s\n' "${LOCAL_PYTHONPATH}"
printf '\nSuggested verification:\n'
printf '  PYTHONPATH=%s uv run pytest -q test/unit_test\n' "${LOCAL_PYTHONPATH}"
printf '  PYTHONPATH=%s:dags uv run python -c '\''import dags.data_ingest_dag as d; print(d.dag_id if hasattr(d, "dag_id") else d.dag.dag_id)'\''\n' "${LOCAL_PYTHONPATH}"
