"""
models.py
Entrenamiento, predicción y serialización de Isolation Forest y Autoencoder.
"""

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest


# ---------------------------------------------------------------------------
# Isolation Forest
# ---------------------------------------------------------------------------

def train_isolation_forest(X_train: np.ndarray, contamination: float = 0.01, random_state: int = 42) -> IsolationForest:
    """
    Entrena un Isolation Forest sobre transacciones normales.
    contamination: proporción esperada de anomalías en el dataset de evaluación.
    """
    pass


def predict_isolation_forest(model: IsolationForest, X: np.ndarray):
    """
    Devuelve (labels, scores) donde:
    - labels: 1 = anómalo, 0 = normal
    - scores: nivel de anomalía normalizado en [0, 1] (mayor = más anómalo)
    """
    pass


# ---------------------------------------------------------------------------
# Autoencoder
# ---------------------------------------------------------------------------

def build_autoencoder(input_dim: int, encoding_dim: int = 16):
    """
    Construye la arquitectura del Autoencoder.
    Devuelve el modelo Keras compilado.
    """
    pass


def train_autoencoder(X_train: np.ndarray, encoding_dim: int = 16, epochs: int = 50, batch_size: int = 256):
    """
    Entrena el Autoencoder sobre transacciones normales.
    Devuelve (model, threshold) donde threshold es el percentil 95 del error de reconstrucción en train.
    """
    pass


def predict_autoencoder(model, X: np.ndarray, threshold: float):
    """
    Devuelve (labels, scores) donde:
    - labels: 1 = anómalo (error > threshold), 0 = normal
    - scores: error de reconstrucción normalizado en [0, 1]
    """
    pass


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------

def save_isolation_forest(model: IsolationForest, path: str = "models/isolation_forest.pkl"):
    """Guarda el modelo Isolation Forest con joblib."""
    pass


def load_isolation_forest(path: str = "models/isolation_forest.pkl") -> IsolationForest:
    """Carga el modelo Isolation Forest desde disco."""
    pass


def save_autoencoder(model, threshold: float, model_path: str = "models/autoencoder.keras", threshold_path: str = "models/ae_threshold.pkl"):
    """Guarda el Autoencoder (formato Keras) y el threshold (joblib)."""
    pass


def load_autoencoder(model_path: str = "models/autoencoder.keras", threshold_path: str = "models/ae_threshold.pkl"):
    """Carga el Autoencoder y su threshold desde disco. Devuelve (model, threshold)."""
    pass
