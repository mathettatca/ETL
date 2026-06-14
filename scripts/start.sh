#!/usr/bin/env bash
# Start the local Docker stack after the first-time initialization has run.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

COMPOSE="${COMPOSE:-docker compose}"
APP_POSTGRES_SERVICE="${APP_POSTGRES_SERVICE:-app-postgres}"
AIRFLOW_POSTGRES_SERVICE="${AIRFLOW_POSTGRES_SERVICE:-airflow-postgres}"
APP_POSTGRES_USER="${APP_POSTGRES_USER:-sts}"
APP_POSTGRES_DB="${APP_POSTGRES_DB:-sts_beyond}"
AIRFLOW_API_SERVICE="${AIRFLOW_API_SERVICE:-airflow-apiserver}"

echo "======================================================"
echo " STSDataIngestion - Docker Start"
echo "======================================================"
${COMPOSE} up -d

echo ""
echo "--> Current containers"
${COMPOSE} ps

echo ""
echo "======================================================"
echo " Start DONE"
echo " Airflow UI: http://localhost:8080"
echo " Login: admin / 1"
echo " App PostgreSQL: localhost:5434"
echo "======================================================"
