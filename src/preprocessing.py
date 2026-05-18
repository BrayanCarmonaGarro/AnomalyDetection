"""
preprocessing.py
Carga, limpieza, feature engineering, escalado y split del dataset.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def load_data(path: str) -> pd.DataFrame:
    """Carga el dataset desde un CSV y devuelve el DataFrame."""
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina columnas que no aportan información al modelo.
    Conserva trans_date_trans_time y dob para feature engineering.
    """
    drop_cols = [
        'Unnamed: 0', 'cc_num', 'unix_time', 'trans_num', 'zip',
        'merchant', 'first', 'last', 'street', 'city', 'state', 'job', 'gender'
    ]
    return df.drop(columns=drop_cols)


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea features derivadas y elimina las columnas originales de las que provienen.
    - hora, dia_semana: extraídos de trans_date_trans_time
    - edad: días desde dob hasta 2021-01-01 dividido 365.25
    - distancia: Haversine en km entre titular y comercio
    - cat_*: one-hot encoding de category (14 columnas)
    """
    df = df.copy()

    dt = pd.to_datetime(df['trans_date_trans_time'])
    df['hora'] = dt.dt.hour
    df['dia_semana'] = dt.dt.dayofweek

    ref = pd.Timestamp('2021-01-01')
    df['edad'] = ((ref - pd.to_datetime(df['dob'])).dt.days / 365.25).astype(int)

    lat1 = np.radians(df['lat'].values)
    lon1 = np.radians(df['long'].values)
    lat2 = np.radians(df['merch_lat'].values)
    lon2 = np.radians(df['merch_long'].values)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    df['distancia'] = 6371 * 2 * np.arcsin(np.sqrt(a))

    dummies = pd.get_dummies(df['category'], prefix='cat').astype(int)
    df = df.drop(columns=['trans_date_trans_time', 'dob', 'lat', 'long',
                           'merch_lat', 'merch_long', 'category'])
    df = pd.concat([df, dummies], axis=1)

    return df


def scale_data(X_train: pd.DataFrame, X_test: pd.DataFrame, scaler: StandardScaler = None):
    """
    Escala las features con StandardScaler.
    Ajusta el scaler solo sobre X_train para evitar data leakage.
    Si se pasa un scaler ya ajustado, lo aplica directamente (útil en inferencia).
    Devuelve (X_train_scaled, X_test_scaled, scaler).
    """
    if scaler is None:
        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns
        )
    else:
        X_train_scaled = pd.DataFrame(
            scaler.transform(X_train), columns=X_train.columns
        )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=X_test.columns
    )
    return X_train_scaled, X_test_scaled, scaler


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Separa en train y test estratificado por is_fraud.
    El modelo se entrena solo con transacciones normales (is_fraud == 0).
    Las etiquetas se reservan únicamente para evaluación.
    Devuelve (X_train, X_test, y_test).
    """
    X = df.drop(columns=['is_fraud'])
    y = df['is_fraud']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    X_train = X_train[y_train == 0]
    return X_train, X_test, y_test


def get_feature_columns() -> list:
    """Devuelve la lista de columnas que entran al modelo después del preprocesamiento."""
    base = ['amt', 'city_pop', 'hora', 'dia_semana', 'edad', 'distancia']
    cats = [
        'cat_entertainment', 'cat_food_dining', 'cat_gas_transport',
        'cat_grocery_net', 'cat_grocery_pos', 'cat_health_fitness',
        'cat_home', 'cat_kids_pets', 'cat_misc_net', 'cat_misc_pos',
        'cat_personal_care', 'cat_shopping_net', 'cat_shopping_pos', 'cat_travel'
    ]
    return base + cats


def describe_dataset(df: pd.DataFrame) -> None:
    """Imprime un resumen formal del dataset: dimensiones, clases, tipos, nulos y estadísticas."""
    print(f"Dimensiones: {df.shape[0]:,} filas × {df.shape[1]} columnas")
    print(f"\nDistribución de clases:")
    print(df['is_fraud'].value_counts().rename({0: 'Normal', 1: 'Fraude'}))
    print(f"\nPorcentaje de fraude: {df['is_fraud'].mean()*100:.2f}%")
    print(f"\nTipos de datos:")
    print(df.dtypes)
    print(f"\nValores nulos:")
    nulos = df.isnull().sum()
    nulos = nulos[nulos > 0]
    print(nulos if not nulos.empty else "Ninguno")
    print(f"\nPrimeras filas:")
    display(df.head())
    print(f"\nResumen estadístico (variables numéricas):")
    display(df.describe().T)
