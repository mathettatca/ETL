from airflow import DAG
from airflow.providers.smtp.operators.smtp import EmailOperator
from datetime import datetime

with DAG(
    dag_id="send_email_dag",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    send_email = EmailOperator(
        task_id="send_email",
        to=["khoinm0603@gmail.com"],
        subject="Airflow Report - {{ ds }}",          # ds = execution date
        html_content="""
            <h3>Báo cáo ngày {{ ds }}</h3>
            <p>DAG <b>{{ dag.dag_id }}</b> chạy thành công!</p>
        """,
    )


if __name__ == "__main__":
    dag.test()