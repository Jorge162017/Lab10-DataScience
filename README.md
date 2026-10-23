# Panorama de visitantes a Guatemala

Avance del Laboratorio 10 — Jorge Luis Lopez, 221038.

Tablero para empresas turísticas con seis visualizaciones de datos observados:

1. Evolución temporal, con agregación mensual, trimestral o anual y zoom.
2. Volumen por vía de ingreso. Seleccionar una barra actualiza la evolución temporal.
3. Estacionalidad: mapa de calor por año y mes, con meses sin cobertura vacíos.
4. Mercados de origen: ranking por región con cantidad de regiones ajustable.
5. Evolución por región: líneas comparativas con selección de regiones.
6. Composición región–vía: barras al 100% con porcentajes y cantidades absolutas.

La navegación separa **Panorama** (1–3) de **Mercados y vías** (4–6). Los filtros globales se conservan al cambiar de sección. Los colores de cada región son estables entre el ranking y la evolución; los de las vías se conservan en la composición.

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
.streamlit/config.toml  Paleta y tema de la interfaz
requirements.txt        Dependencias de la aplicación
docs/                   Documento de diseño en PDF
docs/enunciados/        Instrucciones del Laboratorio 10
referencias/lab1/       Notebook, base y documentos del Laboratorio 1
referencias/lab2/       Notebook, base y documentos del Laboratorio 2
```

Los laboratorios anteriores se conservan como antecedentes, con sus dependencias originales separadas de las del tablero. Para abrirlos y ejecutarlos, usar su propia carpeta como directorio de trabajo. El tablero lee la base de `referencias/lab1/`.

## Probar la interacción

Seleccionar una barra (por ejemplo, Terrestre): el encabezado y la línea de la primera gráfica mostrarán esa vía. Usar «Ver todas las vías en la evolución» para limpiar la selección. Cambiar fechas y regiones, alternar Mes/Trimestre/Año y ocultar una gráfica desde el panel lateral. Vaciar regiones o vías debe mostrar un mensaje en lugar de un error.

En **Mercados y vías**, ajustar la cantidad de regiones del ranking, elegir regiones en la evolución y revisar el desglose porcentual de cada vía. Al filtrar vías, los porcentajes se recalculan entre las vías seleccionadas. Las regiones con volumen cero no tienen composición porcentual. El mapa de calor siempre usa meses; el nivel de detalle temporal afecta a las líneas.

### Explorar con selecciones enlazadas

- En el mapa de estacionalidad, seleccionar el centro de una celda con datos: la gráfica de vías muestra ese mes. La línea temporal conserva todo el período como contexto. «Quitar selección de mes» devuelve el desglose al período completo.
- Seleccionar una vía en las barras sigue actualizando la línea temporal para esa vía.
- En el ranking de mercados, seleccionar una región actualiza su evolución y su composición por vía. Mayús permite añadir regiones; las herramientas de selección rectangular y lazo también permiten seleccionar varias. «Quitar selección de regiones del ranking» recupera la comparación manual.
- En composición, alternar «Porcentaje» y «Cantidad de visitantes» para comparar distribución o volumen. La selección del ranking se aplica en ambos modos.
- «Restablecer filtros y selección» limpia todas las selecciones. Los mensajes junto a las gráficas indican los filtros derivados de las selecciones.

Para verificar el tratamiento de meses ausentes, períodos parciales y porcentajes:

```sh
python -m unittest discover -s tests -v
```

## Documento

[Documento de diseño en PDF](docs/Lab10_Documento_Diseno_Jorge_Lopez.pdf).

Las gráficas 1–6 están implementadas. Las gráficas 7–8 y la comparación de modelos corresponden a la siguiente tarea. El PDF conserva el diseño entregado en el avance.
