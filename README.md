# Panorama de visitantes a Guatemala

Avance del Laboratorio 10 — Jorge Luis Lopez, 221038.

Tablero para empresas turísticas con ocho visualizaciones:

1. Evolución temporal, con agregación mensual, trimestral o anual y zoom.
2. Volumen por vía de ingreso. Seleccionar una barra actualiza la evolución temporal.
3. Estacionalidad: mapa de calor por año y mes, con meses sin cobertura vacíos.
4. Mercados de origen: ranking por región con cantidad de regiones ajustable.
5. Evolución por región: líneas comparativas con selección de regiones.
6. Composición región–vía: barras al 100% con porcentajes y cantidades absolutas.
7. Observado y predicho: curvas de prueba de tres modelos del Laboratorio 1.
8. Error de los modelos: barras de MAE o RMSE, enlazadas con las curvas.

La navegación separa **Panorama** (1–3), **Mercados y vías** (4–6) y **Modelos y límites** (7–8). Los filtros de exploración se conservan entre las dos primeras secciones. Los modelos tienen controles propios para sus siete series evaluadas. Los colores de cada región son estables entre el ranking y la evolución; los de las vías se conservan en la composición.

Incluye filtros de período, región y vía; selección de gráficas visibles; restablecimiento y avisos de cobertura. Los períodos incompletos se identifican en el detalle al pasar el cursor. Usa visitantes comparables (Turista + Excursionista), conservando ceros y cantidades decimales de la base original.

## Ejecutar

Desde la raíz del repositorio, con Python 3.10 o posterior:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abrir la dirección local que indique Streamlit. La primera carga lee el Excel del Laboratorio 1; las siguientes usan caché. No requiere entrenar modelos ni instalar las dependencias de los notebooks.

## Estructura del proyecto

```text
app.py                  Interfaz y visualizaciones de Streamlit
src/datos.py            Limpieza y agregaciones para el tablero
src/exploracion.py      Visualizaciones de estacionalidad y mercados
src/modelos.py          Lectura y evaluación de predicciones exportadas
src/vista_modelos.py    Comparación interactiva de modelos
data/modelos/          Predicciones, observados, métricas y procedencia
scripts/               Reproducción de los ajustes existentes del Lab 1
.streamlit/config.toml  Paleta y tema de la interfaz
requirements.txt        Dependencias de la aplicación
docs/                   Documento de diseño en PDF
docs/enunciados/        Instrucciones del Laboratorio 10
referencias/lab1/       Notebook, base y documentos del Laboratorio 1
referencias/lab2/       Notebook, base y documentos del Laboratorio 2
```

Los laboratorios anteriores se conservan como antecedentes, con sus dependencias originales separadas de las del tablero. Para abrirlos y ejecutarlos, usar su propia carpeta como directorio de trabajo. El tablero lee la base de `referencias/lab1/`.

## Navegación y controles

La barra lateral solo sirve para cambiar de sección. Los controles de exploración están en el bloque «Período y detalle», sobre las gráficas. «Filtrar por regiones y vías» y «Elegir gráficas visibles» agrupan las opciones adicionales. Los controles específicos permanecen junto a su gráfica; MAE/RMSE se elige en la comparación de errores.

Los selectores usan opciones cerradas sin escritura ni búsqueda de texto. Las selecciones cortas (modelos y gráficas visibles) se activan con botones.

## Probar la interacción

Seleccionar una barra (por ejemplo, Terrestre): el encabezado y la línea de la primera gráfica mostrarán esa vía. Usar «Ver todas las vías en la evolución» para limpiar la selección. Cambiar fechas y regiones, alternar Mes/Trimestre/Año y ocultar una gráfica desde «Elegir gráficas visibles». Vaciar regiones o vías debe mostrar un mensaje en lugar de un error.

En **Mercados y vías**, ajustar la cantidad de regiones del ranking, elegir regiones en la evolución y revisar el desglose porcentual de cada vía. Al filtrar vías, los porcentajes se recalculan entre las vías seleccionadas. Las regiones con volumen cero no tienen composición porcentual. El mapa de calor siempre usa meses; el nivel de detalle temporal afecta a las líneas.

### Explorar con selecciones enlazadas

- En el mapa de estacionalidad, seleccionar el centro de una celda con datos: la gráfica de vías muestra ese mes. La línea temporal conserva todo el período como contexto. «Quitar selección de mes» devuelve el desglose al período completo.
- Seleccionar una vía en las barras sigue actualizando la línea temporal para esa vía.
- En el ranking de mercados, seleccionar una región actualiza su evolución y su composición por vía. Mayús permite añadir regiones; las herramientas de selección rectangular y lazo también permiten seleccionar varias. «Quitar selección de regiones del ranking» recupera la comparación manual.
- En composición, alternar «Porcentaje» y «Cantidad de visitantes» para comparar distribución o volumen. La selección del ranking se aplica en ambos modos.
- «Restablecer filtros» limpia todas las selecciones. Los mensajes junto a las gráficas indican los filtros derivados de las selecciones.

### Comparar los modelos

En **Modelos y límites**, elegir una de las siete series, los modelos y el período de prueba. Alternar MAE/RMSE y seleccionar una barra para enfocar ese modelo en las curvas; «Volver a comparar todos los modelos» limpia el enfoque. Las barras se recalculan con los meses seleccionados. Se pueden ocultar gráficas, mostrar contexto de entrenamiento y descargar el CSV del período.

Se comparan suavizamiento exponencial, Holt–Winters y los ARIMA/SARIMA ya seleccionados en el Lab 1. El entrenamiento termina en marzo de 2021 y las predicciones cubren abril de 2021–junio de 2026. Son evaluaciones históricas de horizonte fijo, no pronósticos posteriores a junio de 2026. Los modelos LSTM no se mezclan, porque el Lab 2 usa ventanas que incorporan observaciones reales previas de prueba.

Los resultados se leen de archivos exportados y no requieren entrenamiento para ejecutar la aplicación. Como el notebook original solo conservaba tablas y gráficas, se reprodujeron sus ajustes sin buscar configuraciones nuevas; las 21 combinaciones serie–modelo coinciden con las métricas publicadas al redondeo de la tabla. [Procedencia y reproducción](data/modelos/README.md).

Para verificar el tratamiento de meses ausentes, períodos parciales y porcentajes:

```sh
python -m unittest discover -s tests -v
```

## Documento

[Documento de diseño en PDF](docs/Lab10_Documento_Diseno_Jorge_Lopez.pdf).

Las gráficas 1–8 están implementadas. El PDF está actualizado con el diseño final, la navegación, las interacciones y la procedencia de los modelos. La revisión integral está completada.
