"""
models.py
Entrenamiento, predicción y serialización de Isolation Forest y Autoencoder.
"""

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


# ---------------------------------------------------------------------------
# Isolation Forest
# ---------------------------------------------------------------------------

def train_isolation_forest(X_train: np.ndarray, contamination: float = 0.01, random_state: int = 42) -> IsolationForest:
    """
    Entrena un Isolation Forest sobre transacciones normales.
    contamination: proporción esperada de anomalías en el dataset de evaluación.
    """
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train)
    return model


def predict_isolation_forest(model: IsolationForest, X: np.ndarray):
    """
    Devuelve (labels, scores) donde:
    - labels: 1 = anómalo, 0 = normal
    - scores: nivel de anomalía normalizado en [0, 1] (mayor = más anómalo)
    """
    raw_scores = model.score_samples(X)  # más negativo → más anómalo
    # Invertir y normalizar al rango [0, 1]
    scores = -raw_scores
    scores = (scores - scores.min()) / (scores.max() - scores.min())

    sklearn_labels = model.predict(X)  # -1 = anómalo, 1 = normal
    labels = (sklearn_labels == -1).astype(int)

    return labels, scores


# ---------------------------------------------------------------------------
# Local Outlier Factor
# ---------------------------------------------------------------------------

def train_lof(X_train: np.ndarray, n_neighbors: int = 20, contamination: float = 0.01) -> LocalOutlierFactor:
    """
    Entrena un LOF con novelty=True sobre transacciones normales.
    novelty=True es obligatorio para llamar predict() y decision_function() sobre datos nuevos.
    """
    model = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
        novelty=True,
        n_jobs=-1,
    )
    model.fit(X_train)
    return model


def predict_lof(model: LocalOutlierFactor, X: np.ndarray):
    """
    Devuelve (labels, scores) donde:
    - labels: 1 = anómalo, 0 = normal
    - scores: nivel de anomalía normalizado en [0, 1] (mayor = más anómalo)
    """
    raw_scores = model.decision_function(X)  # más negativo → más anómalo
    scores = -raw_scores
    scores = (scores - scores.min()) / (scores.max() - scores.min())

    sklearn_labels = model.predict(X)  # -1 = anómalo, 1 = normal
    labels = (sklearn_labels == -1).astype(int)

    return labels, scores


def save_lof(model: LocalOutlierFactor, path: str = "models/lof.pkl"):
    """Guarda el modelo LOF con joblib."""
    joblib.dump(model, path)
    print(f"Modelo guardado en {path}")


def load_lof(path: str = "models/lof.pkl") -> LocalOutlierFactor:
    """Carga el modelo LOF desde disco."""
    return joblib.load(path)


# ---------------------------------------------------------------------------
# Autoencoder
# ---------------------------------------------------------------------------

def build_autoencoder(input_dim: int, encoding_dim: int = 8):
    """
    Construye la arquitectura encoder-bottleneck-decoder.
    Arquitectura: input_dim → 16 → encoding_dim → 16 → input_dim
    La salida usa activación linear porque los datos están estandarizados (media 0).
    Devuelve el modelo Keras compilado con Adam y loss MSE.
    """
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


def train_autoencoder(X_train: np.ndarray, y_train: np.ndarray,
                      encoding_dim: int = 8,
                      epochs: int = 50, batch_size: int = 512,
                      contamination: float = 0.01,
                      validation_split: float = 0.1,
                      patience: int = 5):
    """
    Filtra X_train a solo transacciones normales (y_train == 0) y entrena el
    Autoencoder sobre ellas (entrada = salida objetivo).
    Usa EarlyStopping con monitor='val_loss' para evitar sobreajuste.
    Devuelve (model, history, threshold) donde:
    - history: objeto Keras History para la curva de aprendizaje
    - threshold: percentil (1 - contamination) del MSE sobre transacciones normales
    """
    from tensorflow import keras

    X_arr = np.asarray(X_train)
    y_arr = np.asarray(y_train).ravel()
    if len(y_arr) != len(X_arr):
        raise ValueError(
            f"X_train ({len(X_arr)}) e y_train ({len(y_arr)}) deben tener la misma longitud."
        )
    X_train_normal = X_arr[y_arr == 0]
    if X_train_normal.shape[0] == 0:
        raise ValueError("No hay transacciones normales para entrenar el Autoencoder.")

    input_dim = X_train_normal.shape[1]
    model = build_autoencoder(input_dim, encoding_dim)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=patience,
        restore_best_weights=True,
        verbose=1,
    )

    history = model.fit(
        X_train_normal, X_train_normal,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[early_stopping],
        verbose=0,
    )

    # Umbral basado en el error de reconstrucción sobre transacciones normales
    train_preds = model.predict(X_train_normal, verbose=0)
    train_errors = np.mean((X_train_normal - train_preds) ** 2, axis=1)
    threshold = float(np.percentile(train_errors, 100 * (1 - contamination)))

    return model, history, threshold


def predict_autoencoder(model, X: np.ndarray, threshold: float):
    """
    Devuelve (labels, scores) donde:
    - labels: 1 = anómalo (MSE >= threshold), 0 = normal
    - scores: error de reconstrucción normalizado en [0, 1] (mayor = más anómalo)
    Mismo patrón que predict_isolation_forest y predict_lof.
    """
    X = np.asarray(X)
    preds = model.predict(X, verbose=0)
    raw_errors = np.mean((X - preds) ** 2, axis=1)

    scores = (raw_errors - raw_errors.min()) / (raw_errors.max() - raw_errors.min())
    labels = (raw_errors >= threshold).astype(int)

    return labels, scores


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------

def save_isolation_forest(model: IsolationForest, path: str = "models/isolation_forest.pkl"):
    """Guarda el modelo Isolation Forest con joblib."""
    joblib.dump(model, path)
    print(f"Modelo guardado en {path}")


def load_isolation_forest(path: str = "models/isolation_forest.pkl") -> IsolationForest:
    """Carga el modelo Isolation Forest desde disco."""
    return joblib.load(path)


def save_autoencoder(model, threshold: float,
                     model_path: str = "models/autoencoder.keras",
                     threshold_path: str = "models/ae_threshold.pkl"):
    """Guarda el Autoencoder (formato Keras nativo) y el threshold (joblib)."""
    model.save(model_path)
    joblib.dump(threshold, threshold_path)
    print(f"Autoencoder guardado en {model_path}")
    print(f"Umbral guardado en {threshold_path}")


def load_autoencoder(model_path: str = "models/autoencoder.keras",
                     threshold_path: str = "models/ae_threshold.pkl"):
    """Carga el Autoencoder y su threshold desde disco. Devuelve (model, threshold)."""
    from tensorflow import keras
    model = keras.models.load_model(model_path)
    threshold = joblib.load(threshold_path)
    return model, threshold
