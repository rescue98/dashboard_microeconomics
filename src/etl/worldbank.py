import wbdata
import pandas as pd
import os
from datetime import datetime

def fetch_worldbank(indicators: dict, start_date: str, end_date: str, dest_path: str):
    """
    Descarga datos de World Bank para los indicadores dados
    y los guarda en CSV en dest_path.
    - indicators: {'NY.GDP.MKTP.CD': 'GDP', ...}
    - fechas en formato 'YYYY'
    """
    # wbdata trabaja con fechas en datetime
    data = wbdata.get_dataframe(
        indicators,
        country="all",
        data_date=(datetime(int(start_date), 1, 1), datetime(int(end_date), 12, 31)),
        convert_date=True
    )

    # Resetear índice y normalizar nombres
    df = data.reset_index().rename(columns={'country': 'pais', 'date': 'fecha'})
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    df.to_csv(dest_path, index=False)
