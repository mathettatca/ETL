#!/usr/bin/env bash
# First-time local initialization for STSDataIngestion.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE="${COMPOSE:-docker compose}"
RESET_LOCAL_DATA="${RESET_LOCAL_DATA:-0}"

echo "======================================================"
echo " STSDataIngestion - Docker First Run"
echo "======================================================"

echo ""
echo "--> Prepare Google Drive OAuth token mount"
mkdir -p google_tokens

if [[ -f src/building_block/google_tokens/client_secret.json ]]; then
  cp src/building_block/google_tokens/client_secret.json client_secret.json
  echo "    Copied client_secret.json to docker env"
else
  echo "    Missing client_secret.json. Put it at src/building_block/google_tokens/client_secret.json." >&2
  exit 1
fi

if [[ "${RESET_LOCAL_DATA}" == "1" ]]; then
  echo ""
  echo "--> Reset local Docker data for this compose project"
  ${COMPOSE} down --volumes --remove-orphans
fi

echo ""
echo "--> Build Airflow image"
docker build -t sts-data-ingestion-airflow:local .

echo ""
echo "--> Start Docker Compose stack"
${COMPOSE} up -d --no-build

echo ""
${COMPOSE} ps
