"""
tuning.py
Búsqueda de hiperparámetros en validation y selección de ganadores ML / NL.
"""

from __future__ import annotations

import numpy as np

from src.evaluation import (
    find_optimal_threshold,
    get_metrics,
    pick_winner,
    ensemble_scores,
    compare_models,
)
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
    ensemble_val: dict[str, np.ndarray] = {}
    ensemble_test: dict[str, np.ndarray] = {}

    for cont in if_contaminations:
        name = f"Isolation Forest (cont={cont:.4f})"
        model = train_isolation_forest(X_train, contamination=cont)
        _, s_val, rmin, rmax = predict_isolation_forest_with_refs(model, X_val)
        _, s_test, _, _ = predict_isolation_forest_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)
        if abs(cont - contamination_rate) < 1e-9:
            ensemble_val["if"] = s_val
            ensemble_test["if"] = s_test

    for k in lof_neighbors:
        name = f"LOF (k={k})"
        model = train_lof(X_train, n_neighbors=k, contamination=contamination_rate)
        _, s_val, rmin, rmax = predict_lof_with_refs(model, X_val)
        _, s_test, _, _ = predict_lof_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)
        if k == 20:
            ensemble_val["lof"] = s_val
            ensemble_test["lof"] = s_test

    for nu in ocsvm_nus:
        name = f"One-Class SVM (nu={nu:.4f})"
        model = train_one_class_svm(X_train, nu=nu)
        _, s_val, rmin, rmax = predict_one_class_svm_with_refs(model, X_val)
        _, s_test, _, _ = predict_one_class_svm_with_refs(model, X_test, ref_min=rmin, ref_max=rmax)
        results[name] = _eval_ml_candidate(name, y_val, s_val, y_test, s_test, rmin, rmax)

    winner = pick_winner(results, primary="f1", secondary="pr_auc")
    configs["ml_winner"] = winner
    configs["ml_metrics"] = results[winner]
    if "if" in ensemble_val and "lof" in ensemble_val:
        configs["ensemble_scores_val"] = ensemble_val
        configs["ensemble_scores_test"] = ensemble_test
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


_METRIC_KEYS = ("modelo", "accuracy", "precision", "recall", "f1", "auc_roc", "pr_auc")


def _metrics_table(results: dict) -> dict:
    """Filtra métricas para compare_models."""
    return {
        k: {kk: v for kk, v in m.items() if kk in _METRIC_KEYS}
        for k, m in results.items()
    }


def _to_array(X) -> np.ndarray:
    return np.asarray(getattr(X, "values", X))


def run_comparative_section(
    X_train_sc,
    X_val_sc,
    X_test_sc,
    y_train,
    y_val,
    y_test,
    contamination_rate: float,
    stage: str = "all",
    state: dict | None = None,
) -> dict:
    """
    Orquesta la sección 8: tuning ML/NL, ensemble y tablas comparativas.

    stage: 'ml' | 'nl' | 'final' | 'all'
    state: dict opcional para encadenar etapas entre celdas del notebook.
    Devuelve dict con ml_results, nl_results, ml_winner, nl_winner, section8_winners, etc.
    """
    state = {} if state is None else state

    X_tr = _to_array(X_train_sc)
    X_va = _to_array(X_val_sc)
    X_te = _to_array(X_test_sc)
    y_tr = _to_array(y_train)
    y_va = _to_array(y_val)
    y_te = _to_array(y_test)

    if stage in ("ml", "all"):
        print("=== Tuning candidatos ML (umbral en val, métricas en test) ===")
        ml_results, ml_cfg = tune_ml_models(X_tr, X_va, X_te, y_va, y_te, contamination_rate)
        ml_winner = ml_cfg["ml_winner"]
        print(f"Ganador ML: {ml_winner}")
        compare_models(
            _metrics_table(ml_results),
            title="Candidatos ML — test con umbral calibrado en val",
        )
        state["ml_results"] = ml_results
        state["ml_cfg"] = ml_cfg
        state["ml_winner"] = ml_winner

    if stage in ("nl", "all"):
        print("=== Tuning candidatos NL ===")
        nl_results, nl_cfg = tune_nl_models(
            X_tr, y_tr, X_va, y_va, X_te, y_te, contamination_rate
        )
        nl_winner = nl_cfg["nl_winner"]
        print(f"Ganador NL: {nl_winner}")
        compare_models(
            _metrics_table(nl_results),
            title="Candidatos NL — test con umbral calibrado en val",
        )
        state["nl_results"] = nl_results
        state["nl_cfg"] = nl_cfg
        state["nl_winner"] = nl_winner

    if stage in ("final", "all"):
        ml_cfg = state.get("ml_cfg")
        nl_cfg = state.get("nl_cfg")
        if ml_cfg is None or nl_cfg is None:
            raise RuntimeError(
                "Ejecute stage='ml' y stage='nl' antes de 'final', o use stage='all'."
            )

        print("\n=== Ensemble IF + LOF ===")
        ens_val = ml_cfg.get("ensemble_scores_val")
        ens_test = ml_cfg.get("ensemble_scores_test")
        if ens_val is None or ens_test is None:
            if_model = train_isolation_forest(X_tr, contamination=contamination_rate)
            lof_model = train_lof(X_tr, n_neighbors=20, contamination=contamination_rate)
            _, if_va, r0, r1 = predict_isolation_forest_with_refs(if_model, X_va)
            _, if_te, _, _ = predict_isolation_forest_with_refs(if_model, X_te, ref_min=r0, ref_max=r1)
            _, lof_va, r0, r1 = predict_lof_with_refs(lof_model, X_va)
            _, lof_te, _, _ = predict_lof_with_refs(lof_model, X_te, ref_min=r0, ref_max=r1)
            ens_val = {"if": if_va, "lof": lof_va}
            ens_test = {"if": if_te, "lof": lof_te}

        ens_metrics = evaluate_ensemble(
            {},
            y_va,
            ens_val,
            y_te,
            ens_test,
            name="Ensemble IF+LOF (mean)",
        )

        ml_winner = state["ml_winner"]
        nl_winner = state["nl_winner"]
        section8_winners = {
            ml_winner: {
                k: ml_cfg["ml_metrics"][k]
                for k in _METRIC_KEYS
            },
            nl_winner: {
                k: nl_cfg["nl_metrics"][k]
                for k in _METRIC_KEYS
            },
            "Ensemble IF+LOF": ens_metrics,
        }
        compare_models(
            section8_winners,
            title="Ganadores ML vs NL vs Ensemble (test, umbral val)",
        )
        state["ens_metrics"] = ens_metrics
        state["section8_winners"] = section8_winners

    return state
