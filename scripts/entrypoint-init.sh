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
  "AIRFLOW__SMTP__SMTP_HOST"
  "AIRFLOW__SMTP__SMTP_PORT"
  "AIRFLOW__SMTP__SMTP_MAIL_FROM"
  "AIRFLOW__SMTP__SMTP_PASSWORD"
  "GOOGLE_APPLICATION_CREDENTIALS"
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

mkdir -p "$(dirname "${AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE}")"
cp /opt/airflow/bootstrap/simple_auth_manager_passwords.json \
  "${AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE}"
chown -R "${AIRFLOW_UID:-50000}:0" /opt/airflow/config

run_airflow() {
  if [[ "$(id -u)" == "0" ]]; then
    local command
    printf -v command "%q " "$@"
    su airflow -c "${command}"
  else
    "$@"
  fi
}

echo "SimpleAuthManager password file copied: ${AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE}"

echo ""
echo "--> Migrate Airflow metadata DB..."

run_airflow airflow db migrate

echo ""
echo "--> Validate smtp_default runtime connection..."

SMTP_PASSWORD_CLEAN="$(echo "${AIRFLOW__SMTP__SMTP_PASSWORD:-}" | tr -d ' ')"
SMTP_MAIL_FROM="${AIRFLOW__SMTP__SMTP_MAIL_FROM:-${AIRFLOW__SMTP__SMTP_USER:-}}"

if [[ -z "${AIRFLOW__SMTP__SMTP_USER:-}" || -z "${SMTP_PASSWORD_CLEAN}" || -z "${SMTP_MAIL_FROM}" || -z "${AIRFLOW_CONN_SMTP_DEFAULT:-}" ]]; then
  echo "Missing SMTP config. Set AIRFLOW__SMTP__SMTP_USER, AIRFLOW__SMTP__SMTP_PASSWORD, AIRFLOW__SMTP__SMTP_MAIL_FROM, and AIRFLOW_CONN_SMTP_DEFAULT." >&2
  exit 1
fi

echo "smtp_default is provided by AIRFLOW_CONN_SMTP_DEFAULT."

echo ""
echo "--> Validate google_cloud_default runtime connection..."

if [[ -z "${AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT:-}" ]]; then
  echo "Missing Google Cloud config. Set AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT." >&2
  exit 1
fi

echo "google_cloud_default is provided by AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT."

echo ""
echo "--> Sync docker-compose email env to Airflow Variables..."

run_airflow airflow variables set failure_email "${FAILURE_EMAIL}"
run_airflow airflow variables set pipeline_summary_email "${PIPELINE_SUMMARY_EMAIL}"

echo ""
echo "======================================================"
echo " Init DONE. Airflow is ready."
echo " UI: http://localhost:8080"
echo " Login: ${AIRFLOW_ADMIN_USERNAME} / ${AIRFLOW_ADMIN_PASSWORD}"
echo "======================================================"
