FROM apache/airflow:2.5.1-python3.8

USER root
# Instala PySpark, wbdata (WorldBank), pandas, requests y psycopg2
RUN pip install \
    pyspark \
    wbdata \
    pandas \
    requests \
    psycopg2-binary

USER airflow
