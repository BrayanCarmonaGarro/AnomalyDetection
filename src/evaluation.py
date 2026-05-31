"""
evaluation.py
Cálculo de métricas, visualizaciones y comparativa entre modelos.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    ConfusionMatrixDisplay,
    precision_recall_fscore_support,
    average_precision_score,
)


def get_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    scores: np.ndarray,
    model_name: str = "",
    verbose: bool = True,
) -> dict:
    """
    Calcula accuracy, precision, recall, F1, AUC-ROC y PR-AUC.
    Devuelve un diccionario con todas las métricas listo para comparar modelos.
    """
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, pos_label=1, average="binary", zero_division=0
    )
    accuracy = (y_true == y_pred).mean()
    auc = roc_auc_score(y_true, scores)
    pr_auc = average_precision_score(y_true, scores)

    metrics = {
        "model": model_name,
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "auc_roc": round(float(auc), 4),
        "pr_auc": round(float(pr_auc), 4),
    }

    if verbose:
        print(f"\n{'='*50}")
        print(f"  {model_name}")
        print(f"{'='*50}")
        print(f"  Accuracy : {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall   : {metrics['recall']:.4f}")
        print(f"  F1       : {metrics['f1']:.4f}")
        print(f"  AUC-ROC  : {metrics['auc_roc']:.4f}")
        print(f"  PR-AUC   : {metrics['pr_auc']:.4f}")
        print(f"{'='*50}\n")

    return metrics


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = ""):
    """Muestra la matriz de confusión con etiquetas Normal / Anómalo."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Normal", "Anómalo"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"Matriz de Confusión — {model_name}", fontsize=13, pad=12)
    plt.tight_layout()
    plt.show()


def plot_roc_curve(y_true: np.ndarray, scores: np.ndarray, model_name: str = ""):
    """Grafica la curva ROC e imprime el AUC."""
    fpr, tpr, _ = roc_curve(y_true, scores)
    auc = roc_auc_score(y_true, scores)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2563EB", lw=2, label=f"AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1)
    ax.set_xlabel("Tasa de Falsos Positivos", fontsize=11)
    ax.set_ylabel("Tasa de Verdaderos Positivos", fontsize=11)
    ax.set_title(f"Curva ROC — {model_name}", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_score_distribution(scores: np.ndarray, y_true: np.ndarray, model_name: str = ""):
    """
    Histograma del nivel de anomalía separado por clase real.
    Útil para visualizar qué tan bien separa el modelo.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(scores[y_true == 0], bins=80, alpha=0.6, color="#3B82F6", label="Normal", density=True)
    ax.hist(scores[y_true == 1], bins=80, alpha=0.7, color="#EF4444", label="Fraude", density=True)
    ax.set_xlabel("Nivel de anomalía (0 = más normal, 1 = más anómalo)", fontsize=11)
    ax.set_ylabel("Densidad", fontsize=11)
    ax.set_title(f"Distribución del Score de Anomalía — {model_name}", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def find_optimal_threshold(y_true: np.ndarray, scores: np.ndarray):
    """
    Escanea todos los umbrales posibles del score y devuelve el que maximiza F1.
    Retorna (threshold_optimo, labels_con_threshold_optimo).
    Usar sobre el conjunto de validación, no sobre test.
    """
    from sklearn.metrics import precision_recall_curve

    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    f1 = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-10)
    best_idx = np.argmax(f1)
    best_threshold = thresholds[best_idx]
    best_labels = (scores >= best_threshold).astype(int)
    return float(best_threshold), best_labels


def apply_threshold(scores: np.ndarray, threshold: float) -> np.ndarray:
    """Etiquetas binarias a partir de scores y umbral calibrado."""
    return (np.asarray(scores) >= threshold).astype(int)


def calibrate_and_evaluate(
    y_val: np.ndarray,
    scores_val: np.ndarray,
    y_test: np.ndarray,
    scores_test: np.ndarray,
    model_name: str,
    verbose: bool = True,
) -> tuple[float, dict, dict]:
    """
    Calibra umbral óptimo por F1 en val y reporta métricas en val y test.
    Devuelve (threshold, metrics_val, metrics_test).
    """
    threshold, y_val_pred = find_optimal_threshold(y_val, scores_val)
    metrics_val = get_metrics(
        y_val, y_val_pred, scores_val, model_name=f"{model_name} (val, umbral val)", verbose=verbose
    )
    y_test_pred = apply_threshold(scores_test, threshold)
    metrics_test = get_metrics(
        y_test, y_test_pred, scores_test, model_name=f"{model_name} (test, umbral val)", verbose=verbose
    )
    return threshold, metrics_val, metrics_test


def plot_learning_curve(history, model_name: str = ""):
    """
    Grafica la evolución del loss (MSE) de entrenamiento y validación época a época.
    Recibe el objeto History devuelto por model.fit().
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(history.history['loss'], color="#2563EB", lw=2, label='Entrenamiento')
    ax.plot(history.history['val_loss'], color="#EF4444", lw=2, label='Validación')
    ax.set_xlabel("Época", fontsize=11)
    ax.set_ylabel("Loss (MSE)", fontsize=11)
    ax.set_title(f"Curva de Aprendizaje — {model_name}", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_precision_recall_curve(
    y_true: np.ndarray, scores: np.ndarray, threshold: float = None, model_name: str = ""
):
    """Grafica la curva Precision-Recall."""
    from sklearn.metrics import precision_recall_curve

    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    ap = average_precision_score(y_true, scores)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(recall, precision, color="#2563EB", lw=2, label=f"PR-AUC = {ap:.4f}")

    if threshold is not None and len(thresholds) > 0:
        idx = np.argmin(np.abs(thresholds - threshold))
        ax.scatter(recall[idx], precision[idx], color="#EF4444", zorder=5, s=100,
                   label=f"Umbral val ({threshold:.3f})")

    baseline = y_true.mean()
    ax.axhline(baseline, color="gray", linestyle="--", lw=1,
               label=f"Clasificador aleatorio ({baseline:.4f})")

    ax.set_xlabel("Recall", fontsize=11)
    ax.set_ylabel("Precision", fontsize=11)
    ax.set_title(f"Curva Precision-Recall — {model_name}", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def ensemble_scores(score_dict: dict, method: str = "mean") -> np.ndarray:
    """
    Combina scores normalizados de varios modelos.
    method: 'mean' | 'max'
    """
    stacked = np.column_stack([np.asarray(v) for v in score_dict.values()])
    if method == "max":
        return stacked.max(axis=1)
    return stacked.mean(axis=1)


def compare_models(results: dict, title: str = "Comparativa de Modelos"):
    """
    Recibe un dict {nombre_modelo: metricas_dict} y genera:
    - Tabla comparativa de métricas
    - Gráfico de barras comparando precision, recall, F1, AUC-ROC y PR-AUC
    """
    import pandas as pd

    df = pd.DataFrame(results.values()).set_index("model")
    print(f"\n{title}:")
    print(df.to_string())

    metrics_to_plot = ["precision", "recall", "f1", "auc_roc", "pr_auc"]
    x = np.arange(len(metrics_to_plot))
    n = len(results)
    width = min(0.8 / max(n, 1), 0.25)
    colors = ["#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED", "#0891B2"]

    fig, ax = plt.subplots(figsize=(10, 5))
    names = list(results.keys())
    for i, name in enumerate(names):
        vals = [results[name].get(m, 0) for m in metrics_to_plot]
        offset = (i - n / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=name, color=colors[i % len(colors)], alpha=0.85)
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{bar.get_height():.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(["Precision", "Recall", "F1", "AUC-ROC", "PR-AUC"], fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Valor", fontsize=11)
    ax.set_title(title, fontsize=13)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()

    return df


def pick_winner(results: dict, primary: str = "f1", secondary: str = "pr_auc") -> str:
    """Elige el modelo ganador por métrica primaria y desempate."""
    best_name = None
    best_primary = -1.0
    best_secondary = -1.0
    for name, m in results.items():
        p = m.get(primary, 0)
        s = m.get(secondary, 0)
        if p > best_primary or (p == best_primary and s > best_secondary):
            best_primary = p
            best_secondary = s
            best_name = name
    return best_name
