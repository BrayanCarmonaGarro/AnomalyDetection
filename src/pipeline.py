"""
pipeline.py
Orquestación de alto nivel para el notebook: entrenar, puntuar y reportar modelos.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np

from src.models import (
    train_isolation_forest,
    predict_isolation_forest,
    predict_isolation_forest_with_refs,
    train_lof,
    predict_lof,
    predict_lof_with_refs,
    train_autoencoder,
    predict_autoencoder,
    predict_autoencoder_with_refs,
    calibrate_ae_threshold_on_val,
)
from src.evaluation import (
    find_optimal_threshold,
    apply_threshold,
    get_metrics,
    plot_precision_recall_curve,
)


@dataclass
class ModelBundle:
    model: Any
    labels: np.ndarray
    scores: np.ndarray
    scores_val: np.ndarray
    ref_min: float
    ref_max: float
    threshold: float | None = None
    history: Any = None


def print_detection_summary(labels: np.ndarray, y_test) -> None:
    """Resumen de anomalías detectadas vs fraudes reales en test."""
    y_test_arr = np.asarray(getattr(y_test, "values", y_test))
    labels = np.asarray(labels)
    print(f"Transacciones marcadas como anomalas : {labels.sum():,}  ({labels.mean()*100:.2f}%)")
    print(f"Fraudes reales en test               : {y_test_arr.sum():,}  ({y_test_arr.mean()*100:.2f}%)")


def _to_array(X) -> np.ndarray:
    return np.asarray(getattr(X, "values", X))


def run_isolation_forest(
    X_train,
    X_val,
    X_test,
    contamination_rate: float,
    random_state: int = 42,
) -> ModelBundle:
    """Entrena IF, normaliza scores con refs de val y predice en test."""
    X_tr, X_va, X_te = _to_array(X_train), _to_array(X_val), _to_array(X_test)
    model = train_isolation_forest(X_tr, contamination=contamination_rate, random_state=random_state)
    _, scores_val, ref_min, ref_max = predict_isolation_forest_with_refs(model, X_va)
    labels, scores = predict_isolation_forest(model, X_te, ref_min=ref_min, ref_max=ref_max)
    return ModelBundle(model, labels, scores, scores_val, ref_min, ref_max)


def run_lof(
    X_train,
    X_val,
    X_test,
    contamination_rate: float,
    n_neighbors: int = 20,
) -> ModelBundle:
    """Entrena LOF (novelty=True), normaliza scores con refs de val y predice en test."""
    X_tr, X_va, X_te = _to_array(X_train), _to_array(X_val), _to_array(X_test)
    model = train_lof(X_tr, n_neighbors=n_neighbors, contamination=contamination_rate)
    _, scores_val, ref_min, ref_max = predict_lof_with_refs(model, X_va)
    labels, scores = predict_lof(model, X_te, ref_min=ref_min, ref_max=ref_max)
    return ModelBundle(model, labels, scores, scores_val, ref_min, ref_max)


def run_autoencoder_vanilla(
    X_train,
    y_train,
    X_val,
    y_val,
    X_test,
    contamination_rate: float,
    encoding_dim: int = 8,
    epochs: int = 50,
    batch_size: int = 512,
) -> ModelBundle:
    """Entrena AE vanilla, calibra umbral MSE en val y predice en test."""
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

    X_tr = _to_array(X_train)
    y_tr = np.asarray(getattr(y_train, "values", y_train)).ravel()
    X_va = _to_array(X_val)
    y_va = np.asarray(getattr(y_val, "values", y_val)).ravel()
    X_te = _to_array(X_test)

    model, history, _ = train_autoencoder(
        X_tr,
        y_tr,
        encoding_dim=encoding_dim,
        epochs=epochs,
        batch_size=batch_size,
        contamination=contamination_rate,
        denoising=False,
    )

    epochs_run = len(history.history["loss"])
    print(f"Epocas ejecutadas: {epochs_run}")
    print(f"Loss final (train): {history.history['loss'][-1]:.6f}")
    print(f"Loss final (val)  : {history.history['val_loss'][-1]:.6f}")

    threshold = calibrate_ae_threshold_on_val(model, X_va, y_va)
    _, scores_val, ref_min, ref_max = predict_autoencoder_with_refs(model, X_va, threshold)
    labels, scores = predict_autoencoder(model, X_te, threshold, ref_min=ref_min, ref_max=ref_max)

    print(f"Umbral MSE calibrado en val          : {threshold:.6f}")

    return ModelBundle(
        model, labels, scores, scores_val, ref_min, ref_max,
        threshold=threshold, history=history,
    )


def report_f1_threshold(
    y_val,
    scores_val: np.ndarray,
    y_test,
    scores: np.ndarray,
    model_name: str,
) -> tuple[float, np.ndarray, dict]:
    """
    Calibra umbral por F1 en val, grafica PR en test y devuelve métricas en test.
    Devuelve (threshold, labels_opt, metrics_test).
    """
    y_val_arr = np.asarray(getattr(y_val, "values", y_val))
    y_test_arr = np.asarray(getattr(y_test, "values", y_test))

    threshold, _ = find_optimal_threshold(y_val_arr, scores_val)
    labels_opt = apply_threshold(scores, threshold)
    print(f"Umbral calibrado en val (max F1): {threshold:.4f}")

    plot_precision_recall_curve(
        y_test_arr, scores, threshold=threshold, model_name=model_name
    )

    metrics = get_metrics(
        y_test_arr,
        labels_opt,
        scores,
        model_name=f"{model_name} (umbral val → test)",
    )
    return threshold, labels_opt, metrics
