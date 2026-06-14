import logging
from pathlib import Path
from datetime import datetime, timedelta
from html import escape
import pendulum

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import task
from airflow.utils.email import send_email

try:
    from .common import GoogleDriveSensor
    from .common.notifications import build_gmail_failure_callback, _parse_recipients
except ImportError:
    from common import GoogleDriveSensor
    from common.notifications import build_gmail_failure_callback, _parse_recipients

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIPELINE_PYTHONPATH = ":".join(
    str(PROJECT_ROOT / path)
    for path in (
        "src/modules/etl_pipeline/src",
        "src/modules/data_loader/src",
        "src/modules/data_processing/src",
        "src/modules/data_access/src",
        "src/building_block/src",
    )
)
PIPELINE_SCRIPT = PROJECT_ROOT / "src/modules/etl_pipeline/src/hs_code_daily.py"


def _html_cell(value: object) -> str:
    if value is None:
        return "N/A"

    return escape(str(value)).replace("\n", "<br>")


def _html_table(headers: list[str], rows: list[list[object]]) -> str:
    header_cells = "".join(
        '<th style="padding:10px 12px;text-align:left;border-bottom:1px solid #cbd5e1;'
        'background:#f1f5f9;color:#0f172a;font-size:13px;font-weight:700;">'
        f"{_html_cell(header)}</th>"
        for header in headers
    )
    body_rows = "".join(
        "<tr>"
        + "".join(
            '<td style="padding:10px 12px;border-bottom:1px solid #e2e8f0;'
            'vertical-align:top;color:#334155;font-size:13px;">'
            f"{_html_cell(cell)}</td>"
            for cell in row
        )
        + "</tr>"
        for row in rows
    )
    return (
        '<table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;'
        'border-radius:8px;overflow:hidden;background:#ffffff;">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{body_rows}</tbody>"
        "</table>"
    )


def _html_metric_card(label: str, value: object, color: str = "#334155") -> str:
    return (
        '<td style="padding:0 8px 12px 0;width:25%;">'
        '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px;'
        'background:#ffffff;">'
        f'<div style="font-size:12px;color:#64748b;margin-bottom:6px;">{_html_cell(label)}</div>'
        f'<div style="font-size:24px;line-height:1.2;font-weight:700;color:{color};">'
        f"{_html_cell(value)}</div>"
        "</div>"
        "</td>"
    )

def _html_error_list(errors: list[object]) -> str:
    items = "".join(
        '<li style="margin-bottom:8px;color:#7f1d1d;">'
        f"{_html_cell(error)}</li>"
        for error in errors
    )
    return (
        '<div style="border:1px solid #fecaca;border-radius:8px;background:#fef2f2;'
        'padding:12px 16px;">'
        f'<ul style="margin:0;padding-left:18px;">{items}</ul>'
        "</div>"
    )


def _file_display_name(file_info: dict) -> str:
    """Extract display name from file_info dict."""
    return file_info.get("name") or file_info.get("file_name") or "Unknown"


@task(task_id="send_pipeline_summary_email")
def task_send_pipeline_summary_email(**context) -> str | None:
    ti = context["ti"]
    dag = context.get("dag")
    dag_run = context.get("dag_run")
    params = context.get("params", {})

    recipients_value = Variable.get("pipeline_summary_email", default_var=None)
    if not recipients_value:
        recipients_value = Variable.get(
            "failure_email",
            default_var="khoinm0603@gmail.com",
        )
    recipients = _parse_recipients(recipients_value)
    if not recipients:
        logger.info("[summary_email] No recipients configured - skipping.")
        return None

    load_summary = ti.xcom_pull(task_ids="data_loader_task", key="load_summary") or {}
    successful_files = (
        ti.xcom_pull(task_ids="data_loader_task", key="successful_files") or []
    )
    failed_files = ti.xcom_pull(task_ids="data_loader_task", key="failed_files") or []
    processing_result = (
        ti.xcom_pull(task_ids="data_processing_task", key="processing_result") or {}
    )
    postgres_result = (
        ti.xcom_pull(
            task_ids="import_processing_result_to_postgres",
            key="postgres_import_result",
        )
        or {}
    )
    failure_errors = [
        error
        for error in [
            ti.xcom_pull(task_ids="google_drive_sensor", key="failure_error"),
            ti.xcom_pull(task_ids="data_loader_task", key="failure_error"),
            ti.xcom_pull(task_ids="data_processing_task", key="failure_error"),
            ti.xcom_pull(
                task_ids="import_processing_result_to_postgres",
                key="failure_error",
            ),
        ]
        if error
    ]

    processing_errors = processing_result.get("errors") or []
    postgres_errors = postgres_result.get("errors") or []
    status = "FAILED" if failure_errors or processing_errors or postgres_errors else "SUCCESS"

    dag_id = getattr(dag, "dag_id", "unknown")
    run_id = getattr(dag_run, "run_id", "unknown")
    logical_date = context.get("logical_date") or context.get("execution_date")

    processing_files = processing_result.get("files") or []
    import_files = postgres_result.get("files") or []
    processing_rows = [
        [
            _file_display_name(file_info),
            file_info.get("status", ""),
            file_info.get("is_valid", ""),
            file_info.get("csv_path") or "N/A",
            "; ".join(file_info.get("errors") or []),
        ]
        for file_info in processing_files
    ]
    import_rows = [
        [
            _file_display_name(file_info),
            file_info.get("inserted_count", 0),
            file_info.get("status", "success"),
        ]
        for file_info in import_files
    ]

    all_errors = [*failure_errors, *processing_errors, *postgres_errors]
    status_color = "#b91c1c" if status == "FAILED" else "#047857"
    status_background = "#fef2f2" if status == "FAILED" else "#ecfdf5"
    status_border = "#fecaca" if status == "FAILED" else "#a7f3d0"

    html_sections = [
        (
            '<div style="font-family:Arial,Helvetica,sans-serif;line-height:1.45;'
            'color:#0f172a;background:#f8fafc;padding:24px;">'
            '<div style="max-width:980px;margin:0 auto;">'
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:22px 24px;margin-bottom:16px;">'
            '<div style="font-size:13px;color:#64748b;margin-bottom:4px;">Airflow Summary</div>'
            '<h1 style="font-size:24px;line-height:1.25;margin:0;color:#0f172a;">'
            "Data Ingest Pipeline Report"
            "</h1>"
            f'<div style="display:inline-block;margin-top:12px;padding:5px 10px;'
            f'border-radius:999px;border:1px solid {status_border};'
            f'background:{status_background};color:{status_color};'
            'font-size:12px;font-weight:700;letter-spacing:0.3px;">'
            f"{_html_cell(status)}</div>"
            "</div>"
        ),
        (
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:18px 20px;margin-bottom:16px;">'
            '<h2 style="font-size:16px;margin:0 0 12px;color:#0f172a;">Run Info</h2>'
            + _html_table(
                ["Field", "Value"],
                [
                    ["DAG", dag_id],
                    ["Run ID", run_id],
                    ["Logical Date", logical_date],
                    ["Google Drive Folder", params.get("google_drive_folder_id")],
                    ["Execution Date Param", params.get("date")],
                ],
            )
            + "</div>"
        ),
        (
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:18px 20px;margin-bottom:16px;">'
            '<h2 style="font-size:16px;margin:0 0 12px;color:#0f172a;">Pipeline Summary</h2>'
            '<table style="width:100%;border-collapse:collapse;"><tr>'
            + _html_metric_card("Loaded Total", load_summary.get("total", 0))
            + _html_metric_card(
                "Loaded Success",
                load_summary.get("success", len(successful_files)),
                "#047857",
            )
            + _html_metric_card(
                "Loaded Failed",
                load_summary.get("failed", len(failed_files)),
                "#b91c1c",
            )
            + _html_metric_card(
                "Inserted Rows",
                postgres_result.get("inserted_count", 0),
                "#1d4ed8",
            )
            + "</tr></table>"
            + _html_table(
                ["Stage", "Status", "Total/Input", "Success", "Failed/Rows"],
                [
                    [
                        "Data Loader",
                        "success" if not failed_files else "partial",
                        load_summary.get("total", 0),
                        load_summary.get("success", len(successful_files)),
                        load_summary.get("failed", len(failed_files)),
                    ],
                    [
                        "Data Processing",
                        processing_result.get("status", "N/A"),
                        processing_result.get("total", 0),
                        processing_result.get("success", 0),
                        processing_result.get("failed", 0),
                    ],
                    [
                        "PostgreSQL Import",
                        postgres_result.get("status", "N/A"),
                        postgres_result.get("total_input_files", 0),
                        "N/A",
                        postgres_result.get("inserted_count", 0),
                    ],
                ],
            )
            + "</div>"
        ),
    ]

    if all_errors:
        html_sections.append(
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:18px 20px;margin-bottom:16px;">'
            '<h2 style="font-size:16px;margin:0 0 12px;color:#991b1b;">Errors</h2>'
            + _html_error_list(all_errors)
            + "</div>"
        )

    if processing_rows:
        html_sections.append(
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:18px 20px;margin-bottom:16px;">'
            '<h2 style="font-size:16px;margin:0 0 12px;color:#0f172a;">Processed Files</h2>'
            + _html_table(
                ["File Name", "Status", "Valid", "CSV Path", "Errors"],
                processing_rows,
            )
            + "</div>"
        )

    if import_rows:
        html_sections.append(
            '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:10px;'
            'padding:18px 20px;margin-bottom:16px;">'
            '<h2 style="font-size:16px;margin:0 0 12px;color:#0f172a;">Imported Files</h2>'
            + _html_table(["File Name", "Inserted Rows", "Status"], import_rows)
            + "</div>"
        )

    html_sections.extend(
        [
            '<div style="font-size:12px;color:#64748b;margin-top:12px;">'
            "Generated by Airflow data_ingest_pipeline."
            "</div>",
            "</div></div>",
        ]
    )

    html_content = "".join(html_sections)
    ti.xcom_push(key="summary_email_html", value=html_content)

    send_email(
        to=recipients,
        subject=f"[Airflow][SUMMARY][{status}] {dag_id}",
        html_content=html_content,
    )
    logger.info("[summary_email] Sent pipeline summary email to %s.", recipients)
    return html_content


gmail_failure_callback = build_gmail_failure_callback()

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(seconds=5),
    "execution_timeout": timedelta(hours=2),
    "on_failure_callback": gmail_failure_callback,
}

with DAG(
    dag_id="data_ingest_pipeline",
    default_args=default_args,
    schedule="00 08 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    params={
        "source": "google_drive",
        "dest_path": str(PROJECT_ROOT),
        "google_drive_folder_id": '1sbRDJhwTcUX02_YkiF5gmdjjf64uJ8L3',
        "date":None
    },
    tags=["ingest", "hscode"],
) as dag:
    google_drive_sensor = GoogleDriveSensor(
        task_id="google_drive_sensor",
        folder_id="{{ params.google_drive_folder_id }}",
        execution_date="{{params.date or ds}}",
        poke_interval=10,
        timeout=7200,
        mode="reschedule"
    )

    summary_email_task = task_send_pipeline_summary_email()

    data_pipeline_task = BashOperator(
        task_id="data_pipeline_task",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            f"PYTHONUNBUFFERED=1 "
            f"PYTHONPATH={PIPELINE_PYTHONPATH} "
            f"python {PIPELINE_SCRIPT} "
            "--file-source '{{ params.source }}' "
            "--dest-path '{{ params.dest_path }}' "
            "--file_id '{{ params.google_drive_folder_id }}'"
        ),
    )
    google_drive_sensor >> data_pipeline_task >> summary_email_task


if __name__ == "__main__":
    dag.test(
        run_conf={
            "source": "google_drive",
            "dest_path": str(PROJECT_ROOT),
            "google_drive_folder_id": "1sbRDJhwTcUX02_YkiF5gmdjjf64uJ8L3",
        },
    )
