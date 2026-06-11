"""
Simple DAG to test SMTP email notifications.
"""

from datetime import datetime, timedelta
import logging
import os
from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import conf
from airflow.utils.email import send_email

try:
    from common.notifications import build_gmail_failure_callback, _parse_recipients
except ImportError:
    from .common.notifications import build_gmail_failure_callback, _parse_recipients
logger = logging.getLogger(__name__)


def task_that_fails():
    """Task that intentionally fails to trigger failure email."""
    raise ValueError("🧪 TEST FAILURE - This should trigger an email notification!")


def task_success():
    """Successful task that sends a success email."""
    print("✅ Task completed successfully!")


def mask_secret(value: str | None) -> str:
    if not value:
        return "<EMPTY>"
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def send_test_email(**context):
    """Directly send a test email."""

    logger.info("========== SMTP TEST EMAIL START ==========")

    # 1. Read recipients from Airflow Variable
    failure_email = Variable.get(
        "failure_email",
        default_var="khoinm0603@gmail.com",
    )
    recipients = [failure_email]

    logger.info("[SMTP_TEST] failure_email Variable: %s", failure_email)
    logger.info("[SMTP_TEST] recipients: %s", recipients)

    # 2. Read Airflow SMTP config
    smtp_host = conf.get("smtp", "smtp_host", fallback=None)
    smtp_port = conf.get("smtp", "smtp_port", fallback=None)
    smtp_user = conf.get("smtp", "smtp_user", fallback=None)
    smtp_password = conf.get("smtp", "smtp_password", fallback=None)
    smtp_mail_from = conf.get("smtp", "smtp_mail_from", fallback=None)
    smtp_starttls = conf.get("smtp", "smtp_starttls", fallback=None)
    smtp_ssl = conf.get("smtp", "smtp_ssl", fallback=None)

    logger.info("[SMTP_CONFIG] smtp_host: %s", smtp_host)
    logger.info("[SMTP_CONFIG] smtp_port: %s", smtp_port)
    logger.info("[SMTP_CONFIG] smtp_user: %s", smtp_user)
    logger.info("[SMTP_CONFIG] smtp_password exists: %s", bool(smtp_password))
    logger.info(
        "[SMTP_CONFIG] smtp_password length: %s",
        len(smtp_password) if smtp_password else 0,
    )
    logger.info(
        "[SMTP_CONFIG] smtp_password masked: %s",
        mask_secret(smtp_password),
    )
    logger.info("[SMTP_CONFIG] smtp_mail_from: %s", smtp_mail_from)
    logger.info("[SMTP_CONFIG] smtp_starttls: %s", smtp_starttls)
    logger.info("[SMTP_CONFIG] smtp_ssl: %s", smtp_ssl)

    # 3. Read raw Docker env to verify container env
    smtp_env_keys = [
        "AIRFLOW__SMTP__SMTP_HOST",
        "AIRFLOW__SMTP__SMTP_PORT",
        "AIRFLOW__SMTP__SMTP_USER",
        "AIRFLOW__SMTP__SMTP_PASSWORD",
        "AIRFLOW__SMTP__SMTP_MAIL_FROM",
        "AIRFLOW__SMTP__SMTP_STARTTLS",
        "AIRFLOW__SMTP__SMTP_SSL",
        "AIRFLOW__EMAIL__EMAIL_BACKEND",
        "AIRFLOW__EMAIL__FROM_EMAIL",
    ]

    for key in smtp_env_keys:
        value = os.getenv(key)

        if "PASSWORD" in key:
            logger.info("[ENV] %s exists: %s", key, bool(value))
            logger.info("[ENV] %s length: %s", key, len(value) if value else 0)
            logger.info("[ENV] %s masked: %s", key, mask_secret(value))
        else:
            logger.info("[ENV] %s: %s", key, value)

    # 4. Log Airflow context
    logger.info("[CONTEXT] dag_id: %s", context.get("dag").dag_id if context.get("dag") else None)
    logger.info("[CONTEXT] task_id: %s", context.get("task").task_id if context.get("task") else None)
    logger.info("[CONTEXT] run_id: %s", context.get("run_id"))
    logger.info("[CONTEXT] logical_date: %s", context.get("logical_date"))

    subject = "[Airflow Test] 🧪 SMTP Email Test - SUCCESS"

    html_content = """
    <div style="font-family:Arial,Helvetica,sans-serif;line-height:1.45;color:#0f172a;background:#f8fafc;padding:24px;">
        <div style="max-width:860px;margin:0 auto;">
            <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;padding:22px 24px;margin-bottom:16px;">
                <h1 style="font-size:24px;line-height:1.25;margin:0;color:#0f172a;">
                    ✅ SMTP Email Test Successful!
                </h1>
                <p style="margin:12px 0;color:#475569;">
                    Your Airflow SMTP configuration is working correctly.
                </p>
            </div>
            <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:18px 20px;">
                <p style="color:#166534;margin:0;">
                    <strong>Test Details:</strong><br>
                    • DAG: test_smtp_email<br>
                    • Task: send_test_email<br>
                    • Status: ✅ SUCCESS<br>
                    • Timestamp: {timestamp}
                </p>
            </div>
        </div>
    </div>
    """.format(timestamp=datetime.now().isoformat())

    logger.info("[SMTP_TEST] About to send email")
    logger.info("[SMTP_TEST] subject: %s", subject)
    logger.info("[SMTP_TEST] to: %s", recipients)
    
    try:
        send_email(
            to=recipients,
            subject=subject,
            html_content=html_content,
        )
        print(f"✅ Test email sent successfully to: {recipients}")
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        raise


default_args = {
    "owner": "airflow",
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    dag_id="test_smtp_email",
    default_args=default_args,
    description="🧪 Simple DAG to test SMTP email notifications",
    schedule=None,  # Manual trigger only
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["testing", "email"],
    on_failure_callback=build_gmail_failure_callback(),
) as dag:
    
    # Task 1: Send success email
    task_send_success = PythonOperator(
        task_id="send_test_email",
        python_callable=send_test_email,
        doc="Sends a test success email to verify SMTP configuration",
    )
    
    # Task 2: Intentional failure task (to test failure email)
    task_fail = PythonOperator(
        task_id="trigger_failure_email",
        python_callable=task_that_fails,
        doc="Intentionally fails to trigger failure notification email",
    )
    
    # Task 3: Normal success task
    task_ok = PythonOperator(
        task_id="successful_task",
        python_callable=task_success,
        doc="A task that completes successfully",
    )
    
    # DAG flow
    task_send_success >> task_ok
