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

echo ""
echo "--> Start PostgreSQL and MongoDB"
${COMPOSE} up -d "${AIRFLOW_POSTGRES_SERVICE}" "${APP_POSTGRES_SERVICE}" mongo

echo ""
echo "--> Wait for app PostgreSQL healthcheck"
for _ in {1..60}; do
  if ${COMPOSE} exec -T "${APP_POSTGRES_SERVICE}" pg_isready -U "${APP_POSTGRES_USER}" -d "${APP_POSTGRES_DB}" >/dev/null 2>&1; then
    echo "    App PostgreSQL is ready."
    break
  fi
  sleep 2
done

if ! ${COMPOSE} exec -T "${APP_POSTGRES_SERVICE}" pg_isready -U "${APP_POSTGRES_USER}" -d "${APP_POSTGRES_DB}" >/dev/null 2>&1; then
  echo "App PostgreSQL did not become ready in time." >&2
  exit 1
fi

echo ""
echo "--> Wait for MongoDB healthcheck"
for _ in {1..60}; do
  if ${COMPOSE} exec -T mongo mongosh --quiet --eval "db.adminCommand('ping').ok" >/dev/null 2>&1; then
    echo "    MongoDB is ready."
    break
  fi
  sleep 2
done

if ! ${COMPOSE} exec -T mongo mongosh --quiet --eval "db.adminCommand('ping').ok" >/dev/null 2>&1; then
  echo "MongoDB did not become ready in time." >&2
  exit 1
fi

echo ""
echo "--> Start Airflow runtime services"
${COMPOSE} up -d "${AIRFLOW_API_SERVICE}" airflow-scheduler airflow-dag-processor airflow-triggerer

echo ""
echo "--> Wait for Airflow API healthcheck"
for _ in {1..60}; do
  if ${COMPOSE} exec -T "${AIRFLOW_API_SERVICE}" curl --fail http://localhost:8080/api/v2/monitor/health >/dev/null 2>&1; then
    echo "    Airflow API is ready."
    break
  fi
  sleep 2
done

if ! ${COMPOSE} exec -T "${AIRFLOW_API_SERVICE}" curl --fail http://localhost:8080/api/v2/monitor/health >/dev/null 2>&1; then
  echo "Airflow API did not become ready in time." >&2
  exit 1
fi

echo ""
echo "--> Current containers"
${COMPOSE} ps

echo ""
echo "======================================================"
echo " Start DONE"
echo " Airflow UI: http://localhost:8080"
echo " Login: admin / admin"
echo " App PostgreSQL: localhost:5434"
echo "======================================================"
