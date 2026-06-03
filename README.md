# AnomalyDetection
Detección de anomalías en transacciones monetarias. Proyecto Final - Inteligencia Artificial, UNA 2026.

## Estructura del Proyecto

```
AnomalyDetection/
├── proyecto.ipynb          # Notebook principal: narrativa, decisiones, resultados (entregable)
├── src/
│   ├── preprocessing.py    # Limpieza, feature engineering, escalado y split train/val/test
│   ├── eda.py              # Gráficos y utilidades del análisis exploratorio
│   ├── models.py           # Isolation Forest, LOF y Autoencoder; entrenamiento y predicción
│   ├── evaluation.py       # Métricas, curvas ROC/PR, comparativa entre modelos
│   └── pipeline.py         # Orquestación y comparativa final (S8)
├── app.py                  # Streamlit
├── models/                 # Modelos serializados (.pkl, .keras)
├── data.csv                # Dataset de transacciones (no versionado en git)
├── requirements.txt
└── README.md
```

### Cómo fluye el proyecto

1. `proyecto.ipynb` importa funciones de `src/` para mantener el notebook limpio y narrativo.
2. En S5-7 se entrenan Isolation Forest, LOF (k=20) y Autoencoder.
3. En S8, `run_final_comparison` reporta métricas en test sin reentrenar.
4. Opcionalmente, los modelos pueden serializarse en `models/`; `app.py` los cargaría sin re-ejecutar el notebook.

## Dataset

**Fraud_detection** — reemkasaab (El Cairo, Egipto)  
Kaggle: https://www.kaggle.com/datasets/reemkasaab/fraud-detection
Licencia: No especificada · Usabilidad Kaggle: 5.29/10

Dataset sintético de transacciones con tarjeta de crédito, generado con la herramienta **Sparkov Data Generation** (Brandon Harris). Cubre el período enero 2019 – diciembre 2020, con 1,000 clientes y 800 comerciantes simulados. Los patrones de comportamiento (frecuencia, montos por categoría, distribución temporal) se definen mediante perfiles JSON que el simulador usa con la librería Faker.

1,852,394 transacciones, 23 columnas (22 variables del dataset + índice del archivo) y 0.52% fraudes

## Modelos

Evaluados en el proyecto:

- **Isolation Forest** — aislamiento en árboles aleatorios.
- **LOF (k=20)** — anomalías por densidad local.
- **Autoencoder** — error de reconstrucción sobre comportamiento normal.

## Setup

### Requisitos de Python

- **Requerido:** Python **3.12.x**
- **Evitar:** Python 3.13 o superior con el `requirements.txt` actual porque no hay compatibilidad con tensorflow
- **Descarga:** [python.org/downloads](https://www.python.org/downloads/) — en Windows, marcar *Add python.exe to PATH*
- **Comprobar** antes de crear el entorno virtual:

```bash
python --version
```

### 1. Crear y activar el entorno virtual

El directorio `.venv` **no** está en git; cada persona lo crea en local **con Python 3.12**.

**Windows** (usa el launcher `py` para no tomar por error una versión más nueva del PATH):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python --version
```

**macOS / Linux:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version
```

### 2. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

### 3. Iniciar JupyterLab

```bash
jupyter lab
```
