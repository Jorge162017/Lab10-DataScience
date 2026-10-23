"""Lectura y evaluación de resultados exportados. No ajusta modelos."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

CARPETA = Path(__file__).resolve().parents[1] / 'data/modelos'


def cargar_resultados():
    pred = pd.read_csv(CARPETA / 'predicciones_lab1.csv', parse_dates=['Fecha'])
    metricas = pd.read_csv(CARPETA / 'metricas_lab1.csv')
    observados = pd.read_csv(CARPETA / 'observados_lab1.csv', parse_dates=['Fecha'])
    procedencia = json.loads((CARPETA / 'procedencia.json').read_text())
    return pred, metricas, observados, procedencia


def evaluar(predicciones):
    filas = []
    for modelo, grupo in predicciones.groupby('Modelo'):
        error = grupo.Observado.to_numpy() - grupo.Predicho.to_numpy()
        filas.append({'Modelo': modelo, 'MAE': float(np.abs(error).mean()),
                      'RMSE': float(np.sqrt(np.mean(error ** 2))), 'Meses': len(grupo)})
    return pd.DataFrame(filas, columns=['Modelo', 'MAE', 'RMSE', 'Meses'])
