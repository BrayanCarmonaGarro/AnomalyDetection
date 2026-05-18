# AnomalyDetection
Detección de anomalías en transacciones monetarias mediante Isolation Forest y Autoencoder (red neuronal). Proyecto Final — Inteligencia Artificial, UNA 2026.

## Estructura del Proyecto

```
AnomalyDetection/
├── proyecto.ipynb          # Notebook principal: narrativa, decisiones, resultados (entregable)
├── src/
│   ├── preprocessing.py    # Limpieza, feature engineering, normalización y split del dataset
│   ├── models.py           # Implementación de Isolation Forest y Autoencoder; serialización
│   └── evaluation.py       # Métricas, matrices de confusión, curvas ROC y comparativa
├── app.py                  # Sistema interactivo en Streamlit: ingreso de datos → predicción
├── models/                 # Modelos entrenados serializados (.pkl para IF, .keras para AE)
├── data.csv                # Dataset de transacciones (no versionado en git)
├── requirements.txt
└── README.md
```

### Cómo fluye el proyecto

1. `proyecto.ipynb` importa funciones de `src/` para mantener el notebook limpio y narrativo.
2. Al finalizar el entrenamiento, los modelos se serializan en `models/`.
3. `app.py` carga los modelos de `models/` sin re-ejecutar el notebook y expone la interfaz Streamlit.

## Dataset

**Fraud_detection** — reemkasaab (El Cairo, Egipto)  
Kaggle: https://www.kaggle.com/datasets/reemkasaab/fraud-detection
Licencia: No especificada · Usabilidad Kaggle: 5.29/10

Dataset sintético de transacciones con tarjeta de crédito, generado con la herramienta **Sparkov Data Generation** (Brandon Harris). Cubre el período enero 2019 – diciembre 2020, con 1,000 clientes y 800 comerciantes simulados. Los patrones de comportamiento (frecuencia, montos por categoría, distribución temporal) se definen mediante perfiles JSON que el simulador usa con la librería Faker.

1,852,394 transacciones, 23 columnas (22 variables del dataset + índice del archivo) y 0.52% fraudes

## Modelos

### Isolation Forest
Modelo no supervisado diseñado específicamente para detección de anomalías. Construye árboles de decisión aleatorios y mide qué tan fácil es "aislar" un registro del resto: los registros anómalos son más fáciles de aislar y por lo tanto reciben un mayor puntaje de anomalía. Se entrena únicamente con transacciones normales, lo que lo hace robusto ante el fuerte desbalance del dataset (>99% transacciones legítimas). Ideal para detectar fraudes con patrones nuevos o desconocidos.

### Autoencoder (Red Neuronal)
Red neuronal que aprende a comprimir y reconstruir transacciones normales. Cuando se le presenta una transacción anómala, el error de reconstrucción es alto porque el modelo no fue entrenado para representar ese tipo de patrón. Ese error de reconstrucción se usa directamente como el nivel de anomalía. Captura relaciones no lineales complejas entre las variables, lo que lo hace complementario al Isolation Forest.

### Por qué detección de anomalías y no clasificación binaria
Aunque el dataset tiene etiquetas (`is_fraud`), se optó por un enfoque de detección de anomalías por dos razones principales:
- El fraude evoluciona constantemente, por lo que un clasificador entrenado con ejemplos históricos de fraude puede fallar ante patrones nuevos.
- El desbalance extremo del dataset perjudica a los clasificadores supervisados. Los modelos de anomalías aprenden solo el comportamiento normal y detectan cualquier desviación, sin depender de ejemplos de fraude.

Las etiquetas se usan únicamente para **evaluar** el desempeño de los modelos, no para entrenarlos.

## Setup

### 1. Create and activate the virtual environment

The virtual environment is **not** tracked by git, so each person must create it locally.

**Create:**
```bash
python -m venv .venv
```

**Activate:**
- Windows:
  ```bash
  .venv\Scripts\activate
  ```
- macOS / Linux:
  ```bash
  source .venv/bin/activate
  ```

### 2. Install dependencies

With the virtual environment activated, run:

```bash
pip install -r requirements.txt
```

### 3. Start JupyterLab

```bash
jupyter lab
```
