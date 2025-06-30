import argparse, json, os
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col

def read_raw_files(spark, path):
    dfs = []
    for f in os.listdir(path):
        full = os.path.join(path, f)
        if f.lower().endswith(".csv"):
            df = spark.read.csv(full, header=True, inferSchema=True)
            df = df.withColumn("source", lit("csv"))
            dfs.append(df)
        elif f.lower().endswith((".xls", ".xlsx")):
            df = (spark.read
                  .format("com.crealytics.spark.excel")
                  .option("header", "true")
                  .option("inferSchema", "true")
                  .option("dataAddress", "A1")
                  .load(full))
            df = df.withColumn("source", lit("excel"))
            dfs.append(df)
    if not dfs:
        raise ValueError(f"No raw files found in {path}")
    # Une todos permitiendo columnas faltantes
    base = dfs[0]
    if len(dfs) > 1:
        base = base.unionByName(*dfs[1:], allowMissingColumns=True)
    return base

def main(args):
    spark = (SparkSession.builder
             .appName("ETL MacroExports")
             .config("spark.jars", ",".join([
                 "/opt/airflow/jars/postgresql-42.5.0.jar",
                 "/opt/bitnami/spark/jars/spark-excel_2.12-0.13.5.jar"
             ]))
             .getOrCreate())

    # 1) Raw (CSV + Excel)
    df_raw = read_raw_files(spark, args.raw_path)

    # 2) World Bank JSON (viene de XCom)
    wb_json = json.loads(args.json_xcom)
    df_wb = (spark.createDataFrame(wb_json[1])
             .selectExpr("country.id AS country_code", "date AS year", "value")
             .withColumn("value", col("value").cast("double"))
             .withColumn("source", lit("worldbank")))

    # 3) Union final
    df_all = df_raw.unionByName(df_wb, allowMissingColumns=True)

    # 4) Guarda en PostgreSQL
    (df_all.write
       .format("jdbc")
       .option("url", args.jdbc_url)
       .option("dbtable", args.db_table)
       .option("user", args.db_user)
       .option("password", args.db_pass)
       .mode("append")
       .save())

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_xcom', required=True)
    parser.add_argument('--raw_path',    required=True)
    parser.add_argument('--jdbc_url',    required=True)
    parser.add_argument('--db_table',    required=True)
    parser.add_argument('--db_user',     required=True)
    parser.add_argument('--db_pass',     required=True)
    args = parser.parse_args()
    main(args)
