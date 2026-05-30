"""
tuning.py
Búsqueda de hiperparámetros en validation y selección de ganadores ML / NL.
"""

from __future__ import annotations

import numpy as np

from src.evaluation import find_optimal_threshold, get_metrics, pick_winner, ensemble_scores
from src.models import (
    train_isolation_forest,
    predict_isolation_forest_with_refs,
    train_lof,
    predict_lof_with_refs,
    train_one_class_svm,
    predict_one_class_svm_with_refs,
    train_autoencoder,
    predict_autoencoder_with_refs,
    calibrate_ae_threshold_on_val,
)


def _eval_ml_candidate(
    name: str,
    y_val: np.ndarray,
    scores_val: np.ndarray,
    y_test: np.ndarray,
    scores_test: np.ndarray,
    ref_min: float,
    ref_max: float,
) -> dict:
    """Calibra umbral en val y devuelve métricas de test + metadata."""
    threshold, _ = find_optimal_threshold(y_val, scores_val)
    y_test_pred = (scores_test >= threshold).astype(int)
    metrics = get_metrics(y_test, y_test_pred, scores_test, model_name=name, verbose=False)
    metrics["threshold"] = round(threshold, 4)
    metrics["ref_min"] = ref_min
    metrics["ref_max"] = ref_max
    return metrics


def tune_ml_models(
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    contamination_rate: float,
    lof_neighbors: list[int] | None = None,
    if_contaminations: list[float] | None = None,
    ocsvm_nus: list[float] | None = None,
) -> tuple[dict, dict]:
    """
    Entrena candidatos ML, calibra umbral en val, reporta métricas en test.
    Devuelve (results_test, best_configs).
    """
    if lof_neighbors is None:
        lof_neighbors = [20, 50]
    if if_contaminations is None:
        if_contaminations = [contamination_rate, min(contamination_rate * 2, 0.02)]
    if ocsvm_nus is None:
        ocsvm_nus = [contamination_rate, min(contamination_rate * 2, 0.02)]

    results = {}
    configs = {}

    for cont in if_contaminations:
        name = f"Isolation Forest (cont={cont:.4f})"
        model = train_isolation_forest(X_train, contamination=cont)
        _, s_val, rmin, rmax = predict_isolation_forest_with_refs(model, X_val)
        _, s_test, _, _ = predict_isolation_forest_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)

    for k in lof_neighbors:
        name = f"LOF (k={k})"
        model = train_lof(X_train, n_neighbors=k, contamination=contamination_rate)
        _, s_val, rmin, rmax = predict_lof_with_refs(model, X_val)
        _, s_test, _, _ = predict_lof_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)

    for nu in ocsvm_nus:
        name = f"One-Class SVM (nu={nu:.4f})"
        model = train_one_class_svm(X_train, nu=nu)
        _, s_val, rmin, rmax = predict_one_class_svm_with_refs(model, X_val)
        _, s_test, _, _ = predict_one_class_svm_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)

    winner = pick_winner(results, primary="f1", secondary="pr_auc")
    configs["ml_winner"] = winner
    configs["ml_metrics"] = results[winner]
    return results, configs


def tune_nl_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    contamination_rate: float,
    epochs: int = 50,
    batch_size: int = 512,
) -> tuple[dict, dict]:
    """
    Compara Autoencoder vanilla vs Denoising Autoencoder.
    Umbral calibrado en val (F1); métricas finales en test.
    """
    results = {}
    configs = {}

    candidates = [
        ("Autoencoder (vanilla)", False, 8),
        ("Denoising Autoencoder", True, 4),
    ]

    for name, denoising, enc_dim in candidates:
        model, _, _ = train_autoencoder(
            X_train,
            y_train,
            encoding_dim=enc_dim,
            epochs=epochs,
            batch_size=batch_size,
            contamination=contamination_rate,
            denoising=denoising,
        )
        threshold = calibrate_ae_threshold_on_val(model, X_val, y_val)
        _, s_val, rmin, rmax = predict_autoencoder_with_refs(model, X_val, threshold)
        _, s_test, _, _ = predict_autoencoder_with_refs(model, X_test, threshold, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)
        results[name]["threshold_mse"] = round(threshold, 6)
        results[name]["denoising"] = denoising
        results[name]["encoding_dim"] = enc_dim

    winner = pick_winner(results, primary="f1", secondary="auc_roc")
    configs["nl_winner"] = winner
    configs["nl_metrics"] = results[winner]
    return results, configs


def evaluate_ensemble(
    ml_scores_test: dict[str, np.ndarray],
    y_val: np.ndarray,
    score_dict_val: dict[str, np.ndarray],
    y_test: np.ndarray,
    score_dict_test: dict[str, np.ndarray],
    name: str = "Ensemble IF+LOF (mean)",
) -> dict:
    """Ensemble de scores en val/test con umbral calibrado en val."""
    s_val = ensemble_scores(score_dict_val, method="mean")
    s_test = ensemble_scores(score_dict_test, method="mean")
    return _eval_ml_candidate(name, y_val, s_val, y_test, s_test, s_val.min(), s_val.max())
