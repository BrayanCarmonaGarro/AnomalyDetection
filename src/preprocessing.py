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
    - hora, dia_semana, is_noche: extraídos de trans_date_trans_time
    - log_amt: log1p del monto (reduce skew)
    - edad: días desde dob hasta 2021-01-01 dividido 365.25
    - distancia: Haversine en km entre titular y comercio
    - cat_*: one-hot encoding de category (14 columnas)
    """
    df = df.copy()

    dt = pd.to_datetime(df['trans_date_trans_time'])
    df['hora'] = dt.dt.hour
    df['dia_semana'] = dt.dt.dayofweek
    df['is_noche'] = ((df['hora'] >= 22) | (df['hora'] <= 5)).astype(int)
    df['log_amt'] = np.log1p(df['amt'].astype(float))

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
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )
    else:
        X_train_scaled = pd.DataFrame(
            scaler.transform(X_train), columns=X_train.columns, index=X_train.index
        )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test), columns=X_test.columns, index=X_test.index
    )
    return X_train_scaled, X_test_scaled, scaler


def scale_splits(
    X_train: pd.DataFrame,
    X_val: pd.DataFrame,
    X_test: pd.DataFrame,
    scaler: StandardScaler = None,
):
    """
    Escala train, val y test. El scaler se ajusta exclusivamente sobre X_train.
    Devuelve (X_train_sc, X_val_sc, X_test_sc, scaler).
    """
    if scaler is None:
        scaler = StandardScaler()
        X_train_sc = pd.DataFrame(
            scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index
        )
    else:
        X_train_sc = pd.DataFrame(
            scaler.transform(X_train), columns=X_train.columns, index=X_train.index
        )
    X_val_sc = pd.DataFrame(
        scaler.transform(X_val), columns=X_val.columns, index=X_val.index
    )
    X_test_sc = pd.DataFrame(
        scaler.transform(X_test), columns=X_test.columns, index=X_test.index
    )
    return X_train_sc, X_val_sc, X_test_sc, scaler





def split_data_three_way(
    df: pd.DataFrame,
    val_size: float = 0.2,
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    Split estratificado  train / val / test  (por defecto 60% / 20% / 20%).
    Solo X_train se filtra a transacciones normales para entrenamiento no supervisado.
    val y test conservan fraudes para calibrar umbrales y evaluar.

    Devuelve:
        X_train, X_val, X_test, y_train, y_val, y_test, contamination_rate
    """
    if val_size + test_size >= 1.0:
        raise ValueError("val_size + test_size debe ser menor que 1.0")

    X = df.drop(columns=['is_fraud'])
    y = df['is_fraud']

    X_dev, X_test, y_dev, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    val_ratio = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_dev, y_dev, test_size=val_ratio, random_state=random_state, stratify=y_dev
    )

    contamination_rate = float(y_train.mean())
    normal_mask = y_train == 0
    X_train = X_train.loc[normal_mask].reset_index(drop=True)
    y_train = y_train.loc[normal_mask].reset_index(drop=True)

    X_val = X_val.reset_index(drop=True)
    y_val = y_val.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    return X_train, X_val, X_test, y_train, y_val, y_test, contamination_rate


def get_feature_columns() -> list:
    """Devuelve la lista de columnas que entran al modelo después del preprocesamiento."""
    base = ['amt', 'log_amt', 'city_pop', 'hora', 'dia_semana', 'is_noche', 'edad', 'distancia']
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
