"""
app.py
Sistema interactivo en Streamlit para detección de anomalías en tiempo real.
El usuario ingresa los datos de una transacción y obtiene:
  - Predicción: Normal / Anómalo
  - Nivel de anomalía (0–100%) para cada modelo
  - Modelo recomendado según la evaluación comparativa
"""

import streamlit as st
import pandas as pd
import numpy as np

from src.preprocessing import feature_engineering, scale_data, get_feature_columns
from src.models import load_isolation_forest, load_autoencoder, predict_isolation_forest, predict_autoencoder

# ---------------------------------------------------------------------------
# Carga de modelos (se ejecuta una sola vez gracias a st.cache_resource)
# ---------------------------------------------------------------------------

@st.cache_resource
def load_models():
    """Carga los modelos serializados desde models/."""
    pass


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

def main():
    st.title("Detección de Anomalías en Transacciones")
    st.markdown("Ingresá los datos de la transacción para obtener una predicción en tiempo real.")

    # --- Formulario de entrada ---
    with st.form("transaction_form"):
        # Aquí irán los campos del formulario una vez definidas las features finales
        pass

        submitted = st.form_submit_button("Analizar transacción")

    # --- Predicción y resultado ---
    if submitted:
        # Preprocesar entrada, predecir con ambos modelos y mostrar resultados
        pass


if __name__ == "__main__":
    main()
