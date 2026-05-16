"""
preprocessing.py
Carga, limpieza, feature engineering, normalización y split del dataset.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def load_data(path: str) -> pd.DataFrame:
    """Carga el dataset desde un CSV y devuelve el DataFrame."""
    pass


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas irrelevantes para el modelo (identificadores, texto libre)
    y maneja valores nulos si los hay.
    """
    pass


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea features derivadas útiles para detectar anomalías:
    - Hora del día y día de la semana a partir de trans_date_trans_time
    - Edad del titular a partir de dob
    - Distancia entre la ubicación del titular y el comercio
    """
    pass


def normalize(df: pd.DataFrame, scaler: StandardScaler = None):
    """
    Escala las features numéricas con StandardScaler.
    Si se pasa un scaler ya ajustado, lo aplica directamente (útil en inferencia).
    Devuelve (df_scaled, scaler).
    """
    pass


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Separa en train y test estratificado por is_fraud.
    El modelo se entrena solo con transacciones normales (is_fraud == 0).
    Las etiquetas se reservan únicamente para evaluación.
    Devuelve (X_train, X_test, y_test).
    """
    pass


def get_feature_columns() -> list:
    """Devuelve la lista de columnas que entran al modelo después del preprocesamiento."""
    pass
