from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'tesis',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='etl_macro_exports',
    default_args=default_args,
    description='ETL WorldBank + CSV → PostgreSQL via Spark',
    schedule_interval='@daily',
    start_date=datetime(2025, 6, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_worldbank = SimpleHttpOperator(
        task_id='fetch_worldbank',
        http_conn_id='worldbank_api',
        endpoint='/indicator/NY.GDP.MKTP.CD?format=json',
        response_filter=lambda r: r.json(),
        xcom_push=True,
    )

    run_spark_etl = SparkSubmitOperator(
    task_id='run_spark_etl',
    application='/opt/airflow/scripts/etl_spark.py',
    conn_id='spark_default',
    application_args=[
        '--json_xcom', '{{ ti.xcom_pull("fetch_worldbank") }}',
        '--raw_path', '/opt/data/raw',
        '--jdbc_url', 'jdbc:postgresql://postgres:5432/macromonitor',
        '--db_table', 'macro_exports',
        '--db_user', '{{ var.value.POSTGRES_USER }}',
        '--db_pass', '{{ var.value.POSTGRES_PASSWORD }}'
    ],
    )

    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS macro_exports (
          country_code TEXT,
          year INTEGER,
          value DOUBLE PRECISION,
          source TEXT
        );
        """,
    )

    fetch_worldbank >> create_table >> run_spark_etl
