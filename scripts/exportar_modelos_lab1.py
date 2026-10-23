"""Reproduce únicamente ajustes existentes del Lab 1; no busca modelos nuevos.

El notebook conserva tablas e imágenes, no parámetros serializados ni curvas
numéricas. Este script conserva su configuración, datos y corte originales y
contrasta MAE/RMSE contra las tablas HTML guardadas antes de publicar archivos.
Se ejecuta fuera de Streamlit y no modifica el notebook.
"""
from pathlib import Path
import sys
import json
import re
import html
import hashlib
import warnings
import numpy as np
import pandas as pd
import statsmodels
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.datos import ARCHIVO


def filas_html(cell):
    texto = next(''.join(o['data']['text/html']) for o in cell['outputs'] if 'text/html' in o.get('data', {}))
    return [[html.unescape(re.sub('<[^>]+>', '', x)).strip()
             for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', fila, re.S)]
            for fila in re.findall(r'<tr>(.*?)</tr>', texto, re.S)]


def exportar():
    ruta = ROOT / 'referencias/lab1/Lab1_AnalisisSeriesTiempo.ipynb'
    notebook = json.loads(ruta.read_text())
    seleccion = {f[0]: f for f in filas_html(notebook['cells'][20]) if len(f) == 13 and f[1].startswith(('ARIMA(', 'SARIMA('))}
    referencias = {(f[1], f[2]): (float(f[3].replace(',', '')), float(f[4].replace(',', '')))
                   for f in filas_html(notebook['cells'][28]) if len(f) == 7 and f[0].isdigit()}
    # Mantener la agregación directa de filas del notebook: reagrupar primero
    # por región/vía cambia redondeos flotantes y puede alterar el optimizador.
    datos = pd.read_excel(ARCHIVO, sheet_name='Datos')
    datos.columns = datos.columns.str.strip()
    for col in datos.select_dtypes(include=['object', 'string']).columns:
        datos[col] = datos[col].astype('string').str.strip().str.replace(r'\\s+', ' ', regex=True)
    datos['Región dos'] = datos['Región dos'].replace('0', 'Sin clasificar')
    datos['Año'] = pd.to_numeric(datos['Año'], errors='coerce').astype('Int64')
    datos['Mes cod'] = pd.to_numeric(datos['Mes cod'], errors='coerce').astype('Int64')
    datos['Viajero'] = pd.to_numeric(datos['Viajero'], errors='coerce')
    datos = datos.drop_duplicates().copy()
    datos['Fecha'] = pd.to_datetime(dict(year=datos['Año'], month=datos['Mes cod'], day=1), errors='coerce')
    datos = datos.loc[datos.Fecha.notna() & datos.Viajero.notna() & datos.Viajero.ge(0)]
    datos = datos.loc[datos['Tipo de Viajero'].isin(['Turista', 'Excursionista'])]
    indice = pd.date_range(datos.Fecha.min(), datos.Fecha.max(), freq='MS')
    def mensual(df):
        return df.groupby('Fecha').Viajero.sum().reindex(indice, fill_value=0).astype(float)
    series = {'Total visitantes': mensual(datos)}
    for via in ['Aérea', 'Terrestre', 'Marítima']:
        series[f'Vía — {via}'] = mensual(datos.loc[datos.Vía.eq(via)])
    for region in datos.groupby('Región dos').Viajero.sum().nlargest(3).index:
        series[f'Región — {region}'] = mensual(datos.loc[datos['Región dos'].eq(region)])
    corte = int(np.floor(.7 * len(indice)))
    predicciones, metricas, observados, configuraciones = [], [], [], {}
    for nombre, serie in series.items():
        train, test = serie.iloc[:corte], serie.iloc[corte:]
        fila = seleccion[nombre]
        order = tuple(map(int, fila[2:5]))
        seasonal_order = tuple(map(int, fila[5:9]))
        print(f'Reproduciendo {nombre}: {fila[1]}, SES y Holt–Winters', flush=True)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            arima = SARIMAX(np.log1p(train), order=order, seasonal_order=seasonal_order,
                            trend='n', enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=150)
            ses = SimpleExpSmoothing(train, initialization_method='estimated').fit(optimized=True)
            hw = ExponentialSmoothing(train, trend='add', damped_trend=True, seasonal='add',
                                      seasonal_periods=12, initialization_method='estimated').fit(optimized=True, use_brute=True)
        resultados = {
            'ARIMA/SARIMA': np.maximum(np.expm1(np.asarray(arima.get_forecast(steps=len(test)).predicted_mean)), 0),
            'Suavizamiento exponencial': np.maximum(np.asarray(ses.forecast(len(test))), 0),
            'Holt-Winters': np.maximum(np.asarray(hw.forecast(len(test))), 0),
        }
        configuraciones[nombre] = fila[1]
        for fecha, real in serie.items():
            observados.append({'Serie': nombre, 'Fecha': fecha, 'Observado': real,
                               'Conjunto': 'Entrenamiento' if fecha < test.index[0] else 'Prueba'})
        for modelo, pred in resultados.items():
            if not np.isfinite(pred).all():
                raise ValueError(f'Predicciones no finitas: {nombre}, {modelo}')
            mae = float(np.abs(test.to_numpy() - pred).mean())
            rmse = float(np.sqrt(np.mean((test.to_numpy() - pred) ** 2)))
            ref_mae, ref_rmse = referencias[nombre, modelo]
            # La referencia fue guardada con cero decimales. No ocultar divergencias.
            coincide = abs(mae - ref_mae) <= .51 and abs(rmse - ref_rmse) <= .51
            metricas.append({'Serie': nombre, 'Modelo': modelo, 'MAE': mae, 'RMSE': rmse,
                             'MAE_lab1_redondeado': ref_mae, 'RMSE_lab1_redondeado': ref_rmse,
                             'Coincide_redondeo': coincide, 'Meses': len(test)})
            for fecha, real, valor in zip(test.index, test.to_numpy(), pred):
                predicciones.append({'Serie': nombre, 'Modelo': modelo, 'Fecha': fecha,
                                     'Observado': real, 'Predicho': valor})
    salida = ROOT / 'data/modelos'
    tabla = pd.DataFrame(metricas)
    pd.DataFrame(predicciones).to_csv(salida / 'predicciones_lab1.csv', index=False)
    tabla.to_csv(salida / 'metricas_lab1.csv', index=False)
    pd.DataFrame(observados).to_csv(salida / 'observados_lab1.csv', index=False)
    metadata = {
        'origen': 'Reproducción de ajustes existentes del Laboratorio 1; sin búsqueda de modelos ni hiperparámetros nuevos.',
        'notebook': str(ruta.relative_to(ROOT)),
        'sha256_notebook': hashlib.sha256(ruta.read_bytes()).hexdigest(),
        'statsmodels': statsmodels.__version__, 'numpy': np.__version__, 'pandas': pd.__version__,
        'entrenamiento_fin': str(indice[corte-1].date()), 'prueba_inicio': str(indice[corte].date()),
        'prueba_fin': str(indice[-1].date()), 'meses_entrenamiento': corte, 'meses_prueba': len(indice)-corte,
        'protocolo': 'Pronóstico de horizonte fijo de 63 meses desde marzo de 2021; sin incorporar observaciones de prueba.',
        'sarima_seleccionados': configuraciones,
        'configuracion_ses': 'SimpleExpSmoothing; initialization_method=estimated; optimized=True',
        'configuracion_hw': 'ExponentialSmoothing; trend=add; damped_trend=True; seasonal=add; seasonal_periods=12; initialization_method=estimated; optimized=True; use_brute=True',
        'transformacion_arima': 'log1p; inversión expm1 y recorte de negativos a cero',
        'comparaciones_coincidentes_al_redondeo': int(tabla.Coincide_redondeo.sum()),
        'comparaciones_totales': len(tabla),
    }
    (salida / 'procedencia.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print(tabla.to_string(index=False), flush=True)


if __name__ == '__main__':
    exportar()
