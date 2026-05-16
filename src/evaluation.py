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
)


def get_metrics(y_true: np.ndarray, y_pred: np.ndarray, scores: np.ndarray, model_name: str = "") -> dict:
    """
    Calcula accuracy, precision, recall, F1 y AUC-ROC.
    Devuelve un diccionario con todas las métricas listo para comparar modelos.
    """
    pass


def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = ""):
    """Muestra la matriz de confusión con etiquetas Normal / Anómalo."""
    pass


def plot_roc_curve(y_true: np.ndarray, scores: np.ndarray, model_name: str = ""):
    """Grafica la curva ROC e imprime el AUC."""
    pass


def plot_score_distribution(scores: np.ndarray, y_true: np.ndarray, model_name: str = ""):
    """
    Histograma del nivel de anomalía separado por clase real.
    Útil para visualizar qué tan bien separa el modelo.
    """
    pass


def compare_models(results: dict):
    """
    Recibe un dict {nombre_modelo: metricas_dict} y genera:
    - Tabla comparativa de métricas
    - Gráfico de barras comparando F1 y AUC-ROC
    """
    pass
