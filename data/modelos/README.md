# Resultados de los modelos del Laboratorio 1

Estos archivos permiten ejecutar Streamlit sin ajustar modelos ni instalar statsmodels.

- `observados_lab1.csv`: las siete series mensuales y su división entrenamiento/prueba.
- `predicciones_lab1.csv`: 1,323 registros (7 series × 3 modelos × 63 meses), con observado y predicho en visitantes.
- `metricas_lab1.csv`: MAE/RMSE de las curvas exportadas y métricas originales redondeadas para contrastarlas.
- `procedencia.json`: configuración SARIMA seleccionada, versiones del entorno, protocolo y huella SHA-256 del notebook fuente.

## Procedencia

El notebook `referencias/lab1/Lab1_AnalisisSeriesTiempo.ipynb` guarda tablas HTML de métricas e imágenes de curvas. No incluye modelos serializados ni exportaciones de las predicciones numéricas. Por eso estos CSV provienen de **reproducir los ajustes existentes**, conservando la limpieza, la agregación directa de las filas, las siete series y el corte cronológico originales. No son una recuperación de los valores desde las imágenes.

Se reutilizan los órdenes SARIMA ya seleccionados en la tabla del notebook; no se repite la búsqueda de candidatos. Se mantienen la transformación `log1p`, la inversión y el recorte de negativos, y las configuraciones originales de suavizamiento exponencial y Holt–Winters. No se incorporan modelos nuevos.

La prueba comprende abril de 2021–junio de 2026. El entrenamiento comprende enero de 2009–marzo de 2021 (147 meses). Cada curva es un pronóstico de horizonte fijo de 63 meses, sin actualización con observaciones de prueba. Las 21 combinaciones serie–modelo concuerdan con MAE y RMSE guardados, a la precisión de la tabla original (enteros; tolerancia 0.51 visitantes). Esta comprobación no demuestra identidad bit a bit de las curvas, cuyos valores originales no se conservaron.

No se comparan con LSTM del Lab 2: sus ventanas de prueba incorporan historia real previa a cada mes y representan otro protocolo. La vía marítima registra ceros en toda la prueba bajo esta definición; errores cercanos a cero no implican ausencia real de actividad ni superioridad general.

## Reproducir la exportación

Solo es necesario si se desea regenerar los CSV. Usar un entorno separado del tablero, con Python 3.13:

```sh
python3 -m venv .venv-exportacion
source .venv-exportacion/bin/activate
python -m pip install -r scripts/requirements-exportacion.txt
python scripts/exportar_modelos_lab1.py
```

El script ajusta de nuevo los modelos originales fuera de Streamlit y registra las coincidencias y diferencias; no modifica los notebooks ni oculta divergencias del entorno numérico. Revisar `Coincide_redondeo` y `procedencia.json` antes de sustituir archivos versionados. No se debe usar la prueba para seleccionar nuevos hiperparámetros.
