"""
models.py
Entrenamiento, predicción y serialización de modelos no supervisados (ML y redes).
"""

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


# ---------------------------------------------------------------------------
# Utilidades de score
# ---------------------------------------------------------------------------

def normalize_scores(scores: np.ndarray, ref_min: float = None, ref_max: float = None):
    """
    Normaliza scores al rango [0, 1] usando referencia fija (p. ej. min/max de val).
    Si ref_min/ref_max son None, usa min/max del batch actual.
    Devuelve (scores_norm, ref_min, ref_max).
    """
    scores = np.asarray(scores, dtype=float)
    if ref_min is None:
        ref_min = float(scores.min())
    if ref_max is None:
        ref_max = float(scores.max())
    denom = ref_max - ref_min
    if denom < 1e-12:
        return np.zeros_like(scores), ref_min, ref_max
    return (scores - ref_min) / denom, ref_min, ref_max


def score_refs_from_array(scores: np.ndarray) -> tuple[float, float]:
    scores = np.asarray(scores, dtype=float)
    return float(scores.min()), float(scores.max())


# ---------------------------------------------------------------------------
# Isolation Forest
# ---------------------------------------------------------------------------

def train_isolation_forest(
    X_train: np.ndarray, contamination: float = 0.01, random_state: int = 42
) -> IsolationForest:
    """Entrena un Isolation Forest sobre transacciones normales."""
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train)
    return model


def predict_isolation_forest(
    model: IsolationForest, X: np.ndarray, ref_min: float = None, ref_max: float = None
):
    """
    Devuelve (labels, scores). scores en [0, 1]; labels: 1 = anómalo.
    ref_min/ref_max fijan la normalización (p. ej. min/max de val aplicados a test).
    """
    raw_scores = -model.score_samples(X)
    scores, _, _ = normalize_scores(raw_scores, ref_min, ref_max)
    sklearn_labels = model.predict(X)
    labels = (sklearn_labels == -1).astype(int)
    return labels, scores


def predict_isolation_forest_with_refs(
    model: IsolationForest, X: np.ndarray, ref_min: float = None, ref_max: float = None
):
    """Como predict_isolation_forest pero devuelve también ref_min y ref_max."""
    raw_scores = -model.score_samples(X)
    scores, ref_min, ref_max = normalize_scores(raw_scores, ref_min, ref_max)
    labels = (model.predict(X) == -1).astype(int)
    return labels, scores, ref_min, ref_max


# ---------------------------------------------------------------------------
# Local Outlier Factor
# ---------------------------------------------------------------------------

def train_lof(
    X_train: np.ndarray, n_neighbors: int = 20, contamination: float = 0.01
) -> LocalOutlierFactor:
    """Entrena LOF con novelty=True sobre transacciones normales."""
    model = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        novelty=True,
        n_jobs=-1,
    )
    model.fit(X_train)
    return model


def predict_lof(
    model: LocalOutlierFactor, X: np.ndarray, ref_min: float = None, ref_max: float = None
):
    """Devuelve (labels, scores)."""
    raw_scores = -model.decision_function(X)
    scores, _, _ = normalize_scores(raw_scores, ref_min, ref_max)
    labels = (model.predict(X) == -1).astype(int)
    return labels, scores


def predict_lof_with_refs(
    model: LocalOutlierFactor, X: np.ndarray, ref_min: float = None, ref_max: float = None
):
    raw_scores = -model.decision_function(X)
    scores, ref_min, ref_max = normalize_scores(raw_scores, ref_min, ref_max)
    labels = (model.predict(X) == -1).astype(int)
    return labels, scores, ref_min, ref_max


def save_lof(model: LocalOutlierFactor, path: str = "models/lof.pkl"):
    joblib.dump(model, path)
    print(f"Modelo guardado en {path}")


def load_lof(path: str = "models/lof.pkl") -> LocalOutlierFactor:
    return joblib.load(path)


# ---------------------------------------------------------------------------
# Autoencoder
# ---------------------------------------------------------------------------

def build_autoencoder(input_dim: int, encoding_dim: int = 8):
    """Autoencoder clásico: input → 16 → bottleneck → 16 → output."""
    from tensorflow import keras
    from tensorflow.keras.layers import Dense, Input

    model = keras.Sequential([
        Input(shape=(input_dim,)),
        Dense(16, activation='relu'),
        Dense(encoding_dim, activation='relu'),
        Dense(16, activation='relu'),
        Dense(input_dim, activation='linear'),
    ])
    model.compile(optimizer='adam', loss='mse')
    return model


def _ae_reconstruction_errors(model, X: np.ndarray) -> np.ndarray:
    X = np.asarray(X)
    preds = model.predict(X, verbose=0)
    return np.mean((X - preds) ** 2, axis=1)


def train_autoencoder(
    X_train: np.ndarray,
    y_train: np.ndarray,
    encoding_dim: int = 8,
    epochs: int = 50,
    batch_size: int = 512,
    contamination: float = 0.01,
    validation_split: float = 0.1,
    patience: int = 5,
):
    """
    Entrena autoencoder solo con transacciones normales.
    Devuelve (model, history, threshold_mse). Umbral fino en val: calibrate_ae_threshold_on_val.
    """
    from tensorflow import keras

    X_arr = np.asarray(X_train)
    y_arr = np.asarray(y_train).ravel()
    if len(y_arr) != len(X_arr):
        raise ValueError("X_train e y_train deben tener la misma longitud.")
    X_normal = X_arr[y_arr == 0]
    if X_normal.shape[0] == 0:
        raise ValueError("No hay transacciones normales para entrenar el Autoencoder.")

    input_dim = X_normal.shape[1]
    model = build_autoencoder(input_dim, encoding_dim)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=patience,
        restore_best_weights=True,
        verbose=0,
    )

    history = model.fit(
        X_normal, X_normal,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[early_stopping],
        verbose=0,
    )

    train_errors = _ae_reconstruction_errors(model, X_normal)
    threshold = float(np.percentile(train_errors, 100 * (1 - contamination)))
    return model, history, threshold


def threshold_from_errors(errors: np.ndarray, contamination: float) -> float:
    """Umbral MSE crudo por percentil de contaminación."""
    return float(np.percentile(errors, 100 * (1 - contamination)))


def calibrate_ae_threshold_on_val(
    model, X_val: np.ndarray, y_val: np.ndarray, contamination: float = None
) -> float:
    """
    Calibra umbral MSE en validation: percentil fijo o F1 óptimo sobre errores crudos.
    Si contamination se pasa, usa ese percentil; si no, maximiza F1 en val.
    """
    errors = _ae_reconstruction_errors(model, X_val)
    if contamination is not None:
        return threshold_from_errors(errors[y_val == 0], contamination)

    from src.evaluation import find_optimal_threshold
    scores, _, _ = normalize_scores(errors)
    thresh_norm, _ = find_optimal_threshold(y_val, scores)
    # Convertir umbral normalizado a MSE crudo
    e_min, e_max = errors.min(), errors.max()
    return float(e_min + thresh_norm * (e_max - e_min))


def predict_autoencoder(
    model,
    X: np.ndarray,
    threshold: float,
    ref_min: float = None,
    ref_max: float = None,
):
    """
    Devuelve (labels, scores). labels usan threshold en MSE crudo; scores normalizados.
    """
    raw_errors = _ae_reconstruction_errors(model, X)
    scores, _, _ = normalize_scores(raw_errors, ref_min, ref_max)
    labels = (raw_errors >= threshold).astype(int)
    return labels, scores


def predict_autoencoder_with_refs(model, X, threshold, ref_min=None, ref_max=None):
    raw_errors = _ae_reconstruction_errors(model, X)
    scores, ref_min, ref_max = normalize_scores(raw_errors, ref_min, ref_max)
    labels = (raw_errors >= threshold).astype(int)
    return labels, scores, ref_min, ref_max


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------

def save_isolation_forest(model: IsolationForest, path: str = "models/isolation_forest.pkl"):
    joblib.dump(model, path)
    print(f"Modelo guardado en {path}")


def load_isolation_forest(path: str = "models/isolation_forest.pkl") -> IsolationForest:
    return joblib.load(path)


def save_autoencoder(
    model,
    threshold: float,
    model_path: str = "models/autoencoder.keras",
    threshold_path: str = "models/ae_threshold.pkl",
):
    model.save(model_path)
    joblib.dump(threshold, threshold_path)
    print(f"Autoencoder guardado en {model_path}")
    print(f"Umbral guardado en {threshold_path}")


def load_autoencoder(
    model_path: str = "models/autoencoder.keras",
    threshold_path: str = "models/ae_threshold.pkl",
):
    from tensorflow import keras
    model = keras.models.load_model(model_path)
    threshold = joblib.load(threshold_path)
    return model, threshold
