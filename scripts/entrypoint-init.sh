#!/bin/bash
set -e

echo "======================================================"
echo " Airflow Init — STSDataIngestion"
echo "======================================================"

echo ""
echo "--> Validate required environment variables..."

required_vars=(
  "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
  "AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE"
  "AIRFLOW_ADMIN_USERNAME"
  "AIRFLOW_ADMIN_PASSWORD"
  "AIRFLOW__SMTP__SMTP_HOST"
  "AIRFLOW__SMTP__SMTP_PORT"
  "AIRFLOW__SMTP__SMTP_USER"
  "AIRFLOW__SMTP__SMTP_PASSWORD"
  "AIRFLOW__SMTP__SMTP_MAIL_FROM"
  "FAILURE_EMAIL"
  "PIPELINE_SUMMARY_EMAIL"
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "Missing required env: ${var_name}" >&2
    echo "Define it in docker-compose.yml or .env" >&2
    exit 1
  fi
done

echo ""
echo "--> Configure SimpleAuthManager password file..."

python - <<'PY'
import json
import os
from pathlib import Path

passwords_file = Path(os.environ["AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE"])
username = os.environ["AIRFLOW_ADMIN_USERNAME"]
password = os.environ["AIRFLOW_ADMIN_PASSWORD"]

passwords_file.parent.mkdir(parents=True, exist_ok=True)
passwords_file.write_text(
    json.dumps({username: password}),
    encoding="utf-8",
)

print(f"SimpleAuthManager password file created: {passwords_file}")
print(f"SimpleAuthManager user: {username}")
PY

echo ""
echo "--> Migrate Airflow metadata DB..."

airflow db migrate

echo ""
echo "--> Create smtp_default connection from docker-compose environment..."

SMTP_PASSWORD_CLEAN="$(echo "${AIRFLOW__SMTP__SMTP_PASSWORD}" | tr -d ' ')"

airflow connections delete smtp_default 2>/dev/null || true

airflow connections add smtp_default \
  --conn-type smtp \
  --conn-host "${AIRFLOW__SMTP__SMTP_HOST}" \
  --conn-login "${AIRFLOW__SMTP__SMTP_USER}" \
  --conn-password "${SMTP_PASSWORD_CLEAN}" \
  --conn-port "${AIRFLOW__SMTP__SMTP_PORT}" \
  --conn-extra "{\"smtp_starttls\": ${AIRFLOW__SMTP__SMTP_STARTTLS}, \"smtp_ssl\": ${AIRFLOW__SMTP__SMTP_SSL}}"

echo ""
echo "--> Sync docker-compose email env to Airflow Variables..."

airflow variables set failure_email "${FAILURE_EMAIL}"
airflow variables set pipeline_summary_email "${PIPELINE_SUMMARY_EMAIL}"

echo ""
echo "======================================================"
echo " Init DONE. Airflow is ready."
echo " UI: http://localhost:8080"
echo " Login: ${AIRFLOW_ADMIN_USERNAME} / ${AIRFLOW_ADMIN_PASSWORD}"
echo "======================================================"