import pandas as pd
import glob
import os
from typing import Tuple

def clean_all_raw(raw_dir: str, clean_dir: str) -> None:
    """
    Recorre todos los CSV en raw_dir, aplica limpieza básica
    y guarda en clean_dir con el mismo nombre.
    """
    os.makedirs(clean_dir, exist_ok=True)
    for filepath in glob.glob(f"{raw_dir}/*.csv"):
        df = pd.read_csv(filepath)
        df_clean = basic_clean(df)
        filename = os.path.basename(filepath)
        df_clean.to_csv(os.path.join(clean_dir, filename), index=False)

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza básica:
    - Elimina columnas totalmente vacías
    - Estandariza nombres a minúsculas y sin espacios
    - Elimina filas duplicadas
    """
    df = df.dropna(axis=1, how="all")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    return df
