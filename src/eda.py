"""
eda.py
Visualizaciones exploratorias del dataset de transacciones.
Cada función imprime estadísticas relevantes y genera su gráfico.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_class_distribution(df: pd.DataFrame) -> None:
    counts = df['is_fraud'].value_counts().rename({0: 'Normal', 1: 'Fraude'})
    pcts = counts / counts.sum() * 100

    print("Distribución de clases:")
    for label in ['Normal', 'Fraude']:
        print(f"  {label}: {counts[label]:,} ({pcts[label]:.2f}%)")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    counts.plot(kind='bar', ax=axes[0], color=['steelblue', 'tomato'], edgecolor='white')
    axes[0].set_title('Distribución de clases (conteo)')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Transacciones')
    axes[0].tick_params(axis='x', rotation=0)

    axes[1].pie(pcts, labels=pcts.index, autopct='%1.2f%%', colors=['steelblue', 'tomato'])
    axes[1].set_title('Distribución de clases (%)')

    plt.tight_layout()
    plt.show()


def plot_amount_by_class(df: pd.DataFrame) -> None:
    print("Estadísticas de monto por clase:")
    print(df.groupby('is_fraud')['amt'].describe().rename(index={0: 'Normal', 1: 'Fraude'}).to_string())

    data = df[['amt', 'is_fraud']].copy()
    data['class_label'] = data['is_fraud'].map({0: 'Normal', 1: 'Fraude'})

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.boxplot(data=data, x='class_label', y='amt', hue='class_label',
                palette={'Normal': 'steelblue', 'Fraude': 'tomato'}, legend=False, ax=axes[0])
    axes[0].set_title('Monto por clase')
    axes[0].set_ylabel('Monto (USD)')

    # Escala logarítmica para ver la distribución sin que los outliers dominen
    sns.boxplot(data=data, x='class_label', y='amt', hue='class_label',
                palette={'Normal': 'steelblue', 'Fraude': 'tomato'}, legend=False, ax=axes[1])
    axes[1].set_yscale('log')
    axes[1].set_title('Monto por clase (escala log)')
    axes[1].set_ylabel('Monto (USD, log)')

    plt.tight_layout()
    plt.show()


def plot_fraud_by_category(df: pd.DataFrame) -> None:
    fraud_rate = (
        df.groupby('category')['is_fraud']
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .round(2)
    )

    print("Tasa de fraude por categoría (%):")
    print(fraud_rate.to_string())

    plt.figure(figsize=(12, 5))
    sns.barplot(data=fraud_rate.reset_index(), x='category', y='is_fraud', color='tomato')
    plt.title('Tasa de fraude por categoría de comercio')
    plt.xlabel('Categoría')
    plt.ylabel('Tasa de fraude (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_time_patterns(df: pd.DataFrame) -> None:
    data = df[['trans_date_trans_time', 'is_fraud']].copy()
    data['datetime'] = pd.to_datetime(data['trans_date_trans_time'])
    day_map = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    data['hour'] = data['datetime'].dt.hour
    data['weekday'] = data['datetime'].dt.dayofweek.map(day_map)

    fraud_by_hour = data.groupby('hour')['is_fraud'].mean().mul(100).round(2)
    day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    fraud_by_day = data.groupby('weekday')['is_fraud'].mean().mul(100).round(2).reindex(day_order)

    print("Tasa de fraude por hora:")
    print(fraud_by_hour.to_string())
    print("\nTasa de fraude por día:")
    print(fraud_by_day.to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(fraud_by_hour.index, fraud_by_hour.values, marker='o', color='tomato')
    axes[0].set_title('Tasa de fraude por hora del día')
    axes[0].set_xlabel('Hora')
    axes[0].set_ylabel('Tasa de fraude (%)')
    axes[0].set_xticks(range(0, 24))

    axes[1].bar(fraud_by_day.index, fraud_by_day.values, color='tomato')
    axes[1].set_title('Tasa de fraude por día de la semana')
    axes[1].set_xlabel('Día')
    axes[1].set_ylabel('Tasa de fraude (%)')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


def plot_ranges(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include='number')
    stats = pd.DataFrame({
        'min': numeric_cols.min(),
        'max': numeric_cols.max(),
        'value_range': numeric_cols.max() - numeric_cols.min()
    }).sort_values('value_range', ascending=False)

    print("Min, max y rango por variable numérica:")
    print(stats.to_string(float_format=lambda x: f'{x:,.2f}'))

    plt.figure(figsize=(10, 5))
    stats['value_range'].plot(kind='bar', color='steelblue', edgecolor='white')
    plt.title('Rango de variables numéricas')
    plt.ylabel('Rango (max - min)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_correlation_matrix(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include='number').drop(columns=['is_fraud'], errors='ignore')
    corr = numeric_cols.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                linewidths=0.5, annot_kws={'size': 8})
    plt.title('Matriz de correlación, variables numéricas')
    plt.tight_layout()
    plt.show()


def plot_numeric_analysis(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include='number')
    stats = pd.DataFrame({
        'min': numeric_cols.min(),
        'max': numeric_cols.max(),
        'value_range': numeric_cols.max() - numeric_cols.min()
    }).sort_values('value_range', ascending=False)

    print("Min, max y rango por columna numérica:")
    print(stats.to_string(float_format=lambda x: f'{x:,.2f}'))

    corr = numeric_cols.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                linewidths=0.5, annot_kws={'size': 7})
    plt.title('Correlación entre columnas numéricas (dataset crudo)')
    plt.tight_layout()
    plt.show()


def plot_text_analysis(df: pd.DataFrame) -> None:
    text_cols = df.select_dtypes(include='object')
    cardinality = text_cols.nunique().sort_values(ascending=False)

    print("Cardinalidad de columnas de texto (valores únicos):")
    print(cardinality.to_string())

    plt.figure(figsize=(8, 5))
    cardinality.plot(kind='barh', color='steelblue', edgecolor='white')
    plt.title('Cardinalidad de columnas de texto')
    plt.xlabel('Valores únicos')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


def plot_fraud_by_gender(df: pd.DataFrame) -> None:
    stats = df.groupby('gender')['is_fraud'].agg(['sum', 'count', 'mean']).reset_index()
    stats.columns = ['gender', 'fraud_count', 'total', 'fraud_rate']
    stats['fraud_rate_pct'] = (stats['fraud_rate'] * 100).round(2)
    stats['gender'] = stats['gender'].map({'M': 'Masculino', 'F': 'Femenino'})

    print("Tasa de fraude por género:")
    print(stats.rename(columns={
        'gender': 'Género',
        'total': 'Total',
        'fraud_count': 'Fraudes',
        'fraud_rate_pct': 'Tasa (%)',
    })[['Género', 'Total', 'Fraudes', 'Tasa (%)']].to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].bar(stats['gender'], stats['total'], color='steelblue', label='Total')
    axes[0].bar(stats['gender'], stats['fraud_count'], color='tomato', label='Fraudes')
    axes[0].set_title('Transacciones totales vs fraudes por género')
    axes[0].set_ylabel('Transacciones')
    axes[0].legend()

    axes[1].bar(stats['gender'], stats['fraud_rate_pct'], color='tomato')
    axes[1].set_title('Tasa de fraude por género')
    axes[1].set_ylabel('Tasa de fraude (%)')

    plt.tight_layout()
    plt.show()
