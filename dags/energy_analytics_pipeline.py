from datetime import timedelta

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ROOT = "/opt/airflow/project"


default_args = {
    "owner": "fiza",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="european_energy_analytics_pipeline",
    description="Monthly European energy analytics pipeline",
    start_date=pendulum.datetime(2026, 9, 1, tz="UTC"),
    schedule="@monthly",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["energy", "ember", "duckdb", "dbt", "power-bi"],
) as dag:

    ingest_ember_data = BashOperator(
        task_id="ingest_ember_data",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -u src/ingest_ember.py"
        ),
    )

    load_duckdb = BashOperator(
        task_id="load_duckdb",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -u src/load_duckdb.py"
        ),
    )

    validate_raw_data = BashOperator(
        task_id="validate_raw_data",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -u src/validate_data.py"
        ),
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "dbt build "
            "--project-dir energy_analytics "
            "--profiles-dir config/dbt"
        ),
    )

    export_power_bi_data = BashOperator(
        task_id="export_power_bi_data",
        bash_command=(
            f"cd {PROJECT_ROOT} && "
            "python -u src/export_power_bi.py"
        ),
    )
    upload_outputs_to_s3 = BashOperator(
    task_id="upload_outputs_to_s3",
    bash_command=(
        f"cd {PROJECT_ROOT} && "
        'if [ -n "$S3_BUCKET" ]; then '
        "python -u src/upload_to_s3.py; "
        'else echo "S3_BUCKET is not set; skipping S3 upload."; '
        "fi"
    ),
)
    (
        ingest_ember_data
        >> load_duckdb
        >> validate_raw_data
        >> build_dbt_models
        >> export_power_bi_data
        >> upload_outputs_to_s3
    )
