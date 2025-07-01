from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'tesis',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mlops_arima_pipeline',
    default_args=default_args,
    description='Train and register ARIMA model via MLflow',
    schedule_interval='@weekly',
    start_date=datetime(2025, 7, 1),
    catchup=False,
) as dag:

    train_arima = BashOperator(
        task_id='train_arima',
        bash_command="""
        python3 /opt/airflow/mlops/ml_train_arima.py
        """,
        env={
            'AIRFLOW__CORE__SQL_ALCHEMY_CONN': "postgresql+psycopg2://{{ var.value.POSTGRES_USER }}:{{ var.value.POSTGRES_PASSWORD }}@postgres:5432/{{ var.value.POSTGRES_DB }}",
            'MLFLOW_TRACKING_URI': 'http://mlflow:5000'
        }
    )

    train_arima