#!/usr/bin/env bash
set -euo pipefail

# Run this script from the repository root.
# data_loader now uses the same flat internal-package layout as data_access.
# This script intentionally avoids `uv init --package`, because that command
# recreates the src-layout that this project no longer uses.

MODULE_DIR="modules/data_loader"

if [[ ! -d "${MODULE_DIR}" ]]; then
  echo "Missing ${MODULE_DIR}. Run this script from the repository root." >&2
  exit 1
fi

if [[ ! -f "${MODULE_DIR}/pyproject.toml" ]]; then
  echo "Missing ${MODULE_DIR}/pyproject.toml. Create it from the flat package template first." >&2
  exit 1
fi

echo "${MODULE_DIR} already uses flat layout. No uv init step is required."
