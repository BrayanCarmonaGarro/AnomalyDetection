"""
evaluation.py
Cálculo de métricas, visualizaciones y comparativa entre modelos.
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    ConfusionMatrixDisplay,
    precision_recall_fscore_support,
)


def get_metrics(y_true: np.ndarray, y_pred: np.ndarray, scores: np.ndarray, model_name: str = "") -> dict:
    """
    Calcula accuracy, precision, recall, F1 y AUC-ROC.
    Devuelve un diccionario con todas las métricas listo para comparar modelos.
    """
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, pos_label=1, average="binary", zero_division=0
    )
    accuracy = (y_true == y_pred).mean()
    auc = roc_auc_score(y_true, scores)

    metrics = {
        "modelo": model_name,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "auc_roc": round(auc, 4),
    }

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(f"  Accuracy : {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall   : {metrics['recall']:.4f}")
    print(f"  F1       : {metrics['f1']:.4f}")
    print(f"  AUC-ROC  : {metrics['auc_roc']:.4f}")
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
    """
    from sklearn.metrics import precision_recall_curve
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    # precision_recall_curve devuelve len(thresholds) == len(precision) - 1
    f1 = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-10)
    best_idx = np.argmax(f1)
    best_threshold = thresholds[best_idx]
    best_labels = (scores >= best_threshold).astype(int)
    return best_threshold, best_labels


def plot_precision_recall_curve(y_true: np.ndarray, scores: np.ndarray, threshold: float = None, model_name: str = ""):
    """
    Grafica la curva Precision-Recall.
    Si se pasa threshold, marca el punto óptimo sobre la curva.
    """
    from sklearn.metrics import precision_recall_curve, average_precision_score
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    ap = average_precision_score(y_true, scores)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(recall, precision, color="#2563EB", lw=2, label=f"AP = {ap:.4f}")

    if threshold is not None:
        idx = np.argmin(np.abs(thresholds - threshold))
        ax.scatter(recall[idx], precision[idx], color="#EF4444", zorder=5, s=100,
                   label=f"Umbral óptimo ({threshold:.3f})")

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


def compare_models(results: dict):
    """
    Recibe un dict {nombre_modelo: metricas_dict} y genera:
    - Tabla comparativa de métricas
    - Gráfico de barras comparando F1 y AUC-ROC
    """
    import pandas as pd

    df = pd.DataFrame(results.values()).set_index("modelo")
    print("\nComparativa de modelos:")
    print(df.to_string())

    metrics_to_plot = ["precision", "recall", "f1", "auc_roc"]
    x = np.arange(len(metrics_to_plot))
    width = 0.35
    colors = ["#2563EB", "#16A34A", "#DC2626", "#D97706"]

    fig, ax = plt.subplots(figsize=(8, 5))
    names = list(results.keys())
    for i, name in enumerate(names):
        vals = [results[name][m] for m in metrics_to_plot]
        offset = (i - len(names) / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width, label=name, color=colors[i % len(colors)], alpha=0.85)
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{bar.get_height():.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(["Precision", "Recall", "F1", "AUC-ROC"], fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Valor", fontsize=11)
    ax.set_title("Comparativa de Modelos", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()
