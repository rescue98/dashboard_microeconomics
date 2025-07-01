import os
import pandas as pd
import streamlit as st
import mlflow
import mlflow.pyfunc
from sqlalchemy import create_engine

DB_URI = os.getenv('DATABASE_URL', None)
if not DB_URI:
    DB_URI = 'postgresql+psycopg2://airflow:airflow@postgres:5432/macromonitor'
engine = create_engine(DB_URI)

def load_data():
    df = pd.read_sql_table('macro_exports', engine)
    df['year'] = df['year'].astype(int)
    return df

@st.cache_resource
def load_model():
    model = mlflow.pyfunc.load_model('models:/arima_macro_model/Production')
    return model

st.title('Dashboard Macroeconómico')

df = load_data()
country = st.sidebar.selectbox('Country', sorted(df['country_code'].unique()))
df_sel = df[df['country_code']==country]

st.subheader(f'Valores históricos - {country}')
st.line_chart(df_sel.set_index('year')['value'])


st.subheader('Forecast con ARIMA')
model = load_model()
horizon = st.slider('Años a predecir', 1, 10, 3)
last_year = int(df_sel['year'].max())

forecast = model.predict(horizon)
years = list(range(last_year+1, last_year+horizon+1))

fc_df = pd.DataFrame({'year': years, 'forecast': forecast})
fc_df = fc_df.set_index('year')
st.line_chart(fc_df)