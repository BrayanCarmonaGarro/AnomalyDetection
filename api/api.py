"""
api.py
API FastAPI para detección de anomalías en transacciones con tarjeta de crédito.
"""

from __future__ import annotations

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib

from src.preprocessing import feature_engineering, clean_data, get_feature_columns
from src.models import (
    load_isolation_forest, load_lof, load_autoencoder,
    load_scaler, load_refs,
    predict_isolation_forest, predict_lof, predict_autoencoder,
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT_DIR, "models")
DATA_PATH = os.path.join(ROOT_DIR, "data.csv")

def model_path(filename: str) -> str:
    return os.path.join(MODELS_DIR, filename)

# ---------------------------------------------------------------------------
# Estado global
# ---------------------------------------------------------------------------

loaded = {}
eda_cache = {}

# ---------------------------------------------------------------------------
# Carga de modelos
# ---------------------------------------------------------------------------

def load_all_models():
    try:
        loaded["scaler"] = load_scaler(model_path("scaler.pkl"))
        loaded["if_model"] = load_isolation_forest(model_path("isolation_forest.pkl"))
        loaded["if_refs"] = load_refs(model_path("if_refs.pkl"))
        loaded["lof_model"] = load_lof(model_path("lof.pkl"))
        loaded["lof_refs"] = load_refs(model_path("lof_refs.pkl"))
        loaded["ae_model"], loaded["ae_threshold"] = load_autoencoder(
            model_path("autoencoder.keras"), model_path("ae_threshold.pkl")
        )
        loaded["ae_refs"] = load_refs(model_path("ae_refs.pkl"))
        print("Todos los modelos cargados correctamente.")
    except Exception as e:
        print(f"Error cargando modelos: {e}")


# ---------------------------------------------------------------------------
# Precálculo de EDA desde el CSV
# ---------------------------------------------------------------------------

def compute_eda(df: pd.DataFrame):
    """Precalcula todos los datos de EDA y los guarda en eda_cache."""

    # 1. Distribución de clases
    counts = df["is_fraud"].value_counts()
    eda_cache["class_distribution"] = {
        "normal": int(counts.get(0, 0)),
        "fraud": int(counts.get(1, 0)),
        "total": len(df),
        "fraud_pct": round(float(df["is_fraud"].mean() * 100), 4),
    }

    # 2. Montos por clase
    normal_amt = df[df["is_fraud"] == 0]["amt"]
    fraud_amt = df[df["is_fraud"] == 1]["amt"]
    def box_stats(s):
        return {
            "min": round(float(s.min()), 2),
            "q1": round(float(s.quantile(0.25)), 2),
            "median": round(float(s.median()), 2),
            "q3": round(float(s.quantile(0.75)), 2),
            "max": round(float(s.max()), 2),
            "mean": round(float(s.mean()), 2),
        }
    eda_cache["amount_by_class"] = {
        "normal": box_stats(normal_amt),
        "fraud": box_stats(fraud_amt),
        "normal_log": box_stats(np.log1p(normal_amt)),
        "fraud_log": box_stats(np.log1p(fraud_amt)),
    }

    # 3. Tasa de fraude por categoría
    fraud_by_cat = (
        df.groupby("category")["is_fraud"]
        .agg(["sum", "count"])
        .reset_index()
    )
    fraud_by_cat["rate"] = fraud_by_cat["sum"] / fraud_by_cat["count"]
    fraud_by_cat = fraud_by_cat.sort_values("rate", ascending=False)
    eda_cache["fraud_by_category"] = [
        {
            "category": row["category"].replace("_", " "),
            "fraud_rate": round(float(row["rate"]) * 100, 3),
            "fraud_count": int(row["sum"]),
            "total": int(row["count"]),
        }
        for _, row in fraud_by_cat.iterrows()
    ]

    # 4. Patrones temporales
    df["_dt"] = pd.to_datetime(df["trans_date_trans_time"])
    df["_hour"] = df["_dt"].dt.hour
    df["_dow"] = df["_dt"].dt.dayofweek

    by_hour = df.groupby("_hour")["is_fraud"].agg(["sum", "count"])
    eda_cache["fraud_by_hour"] = [
        {"hour": int(h), "fraud_rate": round(float(row["sum"] / row["count"]) * 100, 3)}
        for h, row in by_hour.iterrows()
    ]

    dow_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    by_dow = df.groupby("_dow")["is_fraud"].agg(["sum", "count"])
    eda_cache["fraud_by_dow"] = [
        {"day": dow_names[int(d)], "fraud_rate": round(float(row["sum"] / row["count"]) * 100, 3)}
        for d, row in by_dow.iterrows()
    ]

    # 5. Tasa de fraude por género
    by_gender = df.groupby("gender")["is_fraud"].agg(["sum", "count"])
    eda_cache["fraud_by_gender"] = [
        {
            "gender": "Femenino" if str(g) == "F" else "Masculino",
            "fraud_rate": round(float(row["sum"] / row["count"]) * 100, 3),
            "total": int(row["count"]),
        }
        for g, row in by_gender.iterrows()
    ]

    # Limpiar columnas temporales
    df.drop(columns=["_dt", "_hour", "_dow"], inplace=True)
    print("EDA precalculado correctamente.")


def load_dataset():
    if not os.path.exists(DATA_PATH):
        print(f"CSV no encontrado en {DATA_PATH}, endpoints de EDA no disponibles.")
        return
    try:
        df = pd.read_csv(DATA_PATH)
        compute_eda(df)
        loaded["df"] = df
    except Exception as e:
        print(f"Error cargando dataset: {e}")


# ---------------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------------

load_all_models()
load_dataset()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TransactionInput(BaseModel):
    amt: float
    trans_date_trans_time: str
    category: str
    lat: float
    long: float
    merch_lat: float
    merch_long: float
    city_pop: int
    dob: str
    model: str = "lof"

# ---------------------------------------------------------------------------
# Helpers de preprocesamiento e inferencia
# ---------------------------------------------------------------------------

CATEGORIES = [
    "entertainment", "food_dining", "gas_transport", "grocery_net",
    "grocery_pos", "health_fitness", "home", "kids_pets",
    "misc_net", "misc_pos", "personal_care", "shopping_net",
    "shopping_pos", "travel"
]

def preprocess_input(data: TransactionInput) -> np.ndarray:
    row = {
        "trans_date_trans_time": data.trans_date_trans_time,
        "amt": data.amt,
        "lat": data.lat,
        "long": data.long,
        "merch_lat": data.merch_lat,
        "merch_long": data.merch_long,
        "city_pop": data.city_pop,
        "dob": data.dob,
        "category": data.category,
    }
    df = pd.DataFrame([row])
    df = feature_engineering(df)

    feature_cols = get_feature_columns()
    
    print("Columnas tras feature_engineering:", list(df.columns))
    print("Columnas esperadas:", feature_cols)
    
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_cols].astype(float)
    
    print("Columnas finales:", list(df.columns))
    
    scaled = loaded["scaler"].transform(df)
    return scaled


def run_prediction(X: np.ndarray, model_name: str) -> dict:
    if model_name == "isolation_forest":
        refs = loaded["if_refs"]
        labels, scores = predict_isolation_forest(
            loaded["if_model"], X,
            ref_min=refs["ref_min"], ref_max=refs["ref_max"]
        )
        threshold = 0.5
    elif model_name == "lof":
        refs = loaded["lof_refs"]
        labels, scores = predict_lof(
            loaded["lof_model"], X,
            ref_min=refs["ref_min"], ref_max=refs["ref_max"]
        )
        threshold = 0.5
    elif model_name == "autoencoder":
        refs = loaded["ae_refs"]
        labels, scores = predict_autoencoder(
            loaded["ae_model"], X,
            threshold=loaded["ae_threshold"],
            ref_min=refs["ref_min"], ref_max=refs["ref_max"]
        )
        threshold = 0.5
    else:
        raise HTTPException(status_code=400, detail=f"Modelo desconocido: {model_name}")

    score = float(np.clip(scores[0], 0.0, 1.0))
    is_anomaly = score >= threshold

    return {
        "label": int(is_anomaly),
        "score": round(score, 4),
        "is_anomaly": bool(is_anomaly),
    }


# ---------------------------------------------------------------------------
# Endpoints — Estado
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "models_loaded": [k for k in loaded if "model" in k or k == "scaler"],
        "dataset_loaded": "df" in loaded,
        "eda_ready": len(eda_cache) > 0,
    }


@app.get("/features")
def get_features():
    return {
        "features": get_feature_columns(),
        "categories": CATEGORIES,
    }

# ---------------------------------------------------------------------------
# Endpoints — Predicción
# ---------------------------------------------------------------------------

@app.post("/predict")
def predict(data: TransactionInput):
    if "scaler" not in loaded:
        raise HTTPException(status_code=503, detail="Modelos no cargados")
    try:
        X = preprocess_input(data)
        result = run_prediction(X, data.model)
        return {"model": data.model, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------------------------
# Endpoints — EDA
# ---------------------------------------------------------------------------

def require_eda():
    if not eda_cache:
        raise HTTPException(status_code=503, detail="EDA no disponible: CSV no cargado")


@app.get("/eda/class-distribution")
def eda_class_distribution():
    require_eda()
    return eda_cache["class_distribution"]


@app.get("/eda/amount-by-class")
def eda_amount_by_class():
    require_eda()
    return eda_cache["amount_by_class"]


@app.get("/eda/fraud-by-category")
def eda_fraud_by_category():
    require_eda()
    return eda_cache["fraud_by_category"]


@app.get("/eda/time-patterns")
def eda_time_patterns():
    require_eda()
    return {
        "by_hour": eda_cache["fraud_by_hour"],
        "by_dow": eda_cache["fraud_by_dow"],
    }


@app.get("/eda/fraud-by-gender")
def eda_fraud_by_gender():
    require_eda()
    return eda_cache["fraud_by_gender"]

@app.get("/debug/scaler-features")
def debug_scaler():
    return {"feature_names": list(loaded["scaler"].feature_names_in_)}

# ---------------------------------------------------------------------------
# Endpoints — Análisis contextual
# ---------------------------------------------------------------------------

class ContextualRequest(BaseModel):
    reference_transactions: list[TransactionInput]
    target_transaction: TransactionInput
    model: str = "lof"


def compute_statistical_score(ref_features: np.ndarray, target_features: np.ndarray) -> dict:
    """
    Compara la transacción target contra el perfil estadístico de las referencias.
    Devuelve un score entre 0 y 1 y los detalles por dimensión.
    """
    mean = ref_features.mean(axis=0)
    std = ref_features.std(axis=0)
    std[std < 1e-6] = 1e-6

    z_scores = np.abs((target_features[0] - mean) / std)
    score = float(np.clip(z_scores.mean() / 5.0, 0.0, 1.0))

    feature_cols = get_feature_columns()
    top_idx = np.argsort(z_scores)[::-1][:5]
    top_deviations = [
        {
            "feature": feature_cols[i],
            "z_score": round(float(z_scores[i]), 2),
            "reference_mean": round(float(mean[i]), 4),
            "target_value": round(float(target_features[0][i]), 4),
        }
        for i in top_idx
    ]

    return {
        "score": round(score, 4),
        "is_anomaly": score >= 0.5,
        "top_deviations": top_deviations,
    }


def compute_lof_local_score(ref_features: np.ndarray, target_features: np.ndarray) -> dict:
    """
    Entrena un LOF pequeño solo con las transacciones de referencia
    y evalúa la transacción target contra ese perfil local.
    """
    from sklearn.neighbors import LocalOutlierFactor

    n_neighbors = min(5, len(ref_features) - 1)
    if n_neighbors < 1:
        return {"score": 0.0, "is_anomaly": False, "note": "Pocas referencias"}

    lof = LocalOutlierFactor(n_neighbors=n_neighbors, novelty=True)
    lof.fit(ref_features)

    raw_score = -lof.decision_function(target_features)
    ref_scores = -lof.decision_function(ref_features)

    ref_min = float(ref_scores.min())
    ref_max = float(ref_scores.max())
    denom = ref_max - ref_min if ref_max - ref_min > 1e-6 else 1.0
    score = float(np.clip((raw_score[0] - ref_min) / denom, 0.0, 1.0))

    return {
        "score": round(score, 4),
        "is_anomaly": score >= 0.5,
        "n_references": len(ref_features),
        "n_neighbors_used": n_neighbors,
    }


@app.post("/analyze-contextual")
def analyze_contextual(data: ContextualRequest):
    if "scaler" not in loaded:
        raise HTTPException(status_code=503, detail="Modelos no cargados")
    if len(data.reference_transactions) < 2:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 2 transacciones de referencia")

    try:
        ref_scaled = np.vstack([
            preprocess_input(t) for t in data.reference_transactions
        ])

        target_scaled = preprocess_input(data.target_transaction)

        global_result = run_prediction(target_scaled, data.model)

        statistical_result = compute_statistical_score(ref_scaled, target_scaled)

        lof_local_result = compute_lof_local_score(ref_scaled, target_scaled)

        return {
            "global": {**global_result, "model": data.model},
            "statistical": statistical_result,
            "lof_local": lof_local_result,
            "n_references": len(data.reference_transactions),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))