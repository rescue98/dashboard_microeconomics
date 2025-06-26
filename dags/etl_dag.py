import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Importamos funciones de nuestro paquete
from src.etl.worldbank import fetch_worldbank
from src.etl.clean_csv import clean_all_raw

# Carga variables de entorno
RAW_DIR   = os.getenv("RAW_CSV_DIR", "/opt/airflow/data/raw")
CLEAN_DIR = os.getenv("CLEAN_CSV_DIR", "/opt/airflow/data/clean")
WB_PATH   = os.getenv("WORLD_BANK_CSV_PATH", "/opt/airflow/data/worldbank.csv")

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 6, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_macroeconomico",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["tesis","etl"]
) as dag:

    t1 = PythonOperator(
        task_id="clean_raw_csv",
        python_callable=clean_all_raw,
        op_kwargs={"raw_dir": RAW_DIR, "clean_dir": CLEAN_DIR}
    )

    t2 = PythonOperator(
        task_id="fetch_worldbank",
        python_callable=fetch_worldbank,
        op_kwargs={
            "indicators": {"NY.GDP.MKTP.CD": "gdp_usd"},
            "start_date": "2000",
            "end_date": "2024",
            "dest_path": WB_PATH
        }
    )

    # Orden de ejecución
    t1 >> t2
