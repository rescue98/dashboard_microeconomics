import os
import mlflow
import pandas as pd
from sqlalchemy import create_engine
import pmdarima as pm
from sklearn.metrics import mean_absolute_error, mean_squared_error

mlflow.set_experiment("macro_arima_forecasting")

DB_URI = os.getenv("AIRFLOW__CORE__SQL_ALCHEMY_CONN")  # same as Airflow
TABLE = "macro_exports"
TARGET_COL = "value"
TIME_COL = "year"
MODEL_NAME = "arima_macro_model"

def load_data():
    engine = create_engine(DB_URI)
    df = pd.read_sql_table(TABLE, engine)
    # suponemos que table tiene country_code, year, value
    ts = df.groupby(TIME_COL)[TARGET_COL].mean().sort_index()
    return ts

def train_and_log(ts):
    with mlflow.start_run():
        model = pm.auto_arima(
            ts,
            start_p=1, start_q=1,
            max_p=5, max_q=5,
            seasonal=False,
            stepwise=True,
            suppress_warnings=True,
        )
        preds = model.predict_in_sample()
        mae = mean_absolute_error(ts, preds)
        mse = mean_squared_error(ts, preds)

        mlflow.log_params({"order": model.order, "aic": model.aic()})
        mlflow.log_metrics({"mae": mae, "mse": mse})

        mlflow.statsmodels.log_model(model, MODEL_NAME)
        print(f"Model logged with order={model.order}, AIC={model.aic()}")

if __name__ == "__main__":
    ts = load_data()
    train_and_log(ts)