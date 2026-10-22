# Panorama de visitantes a Guatemala

Avance del Laboratorio 10 — Jorge Luis Lopez, 221038.

Tablero para empresas turísticas con dos visualizaciones de datos observados:

1. Evolución temporal, con agregación mensual, trimestral o anual y zoom.
2. Volumen por vía de ingreso. Seleccionar una barra actualiza la evolución temporal.

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

## Documento

[Documento de diseño en PDF](docs/Lab10_Documento_Diseno_Jorge_Lopez.pdf).

El avance implementa las gráficas 1 y 2. Las otras seis y la comparación de modelos siguen planificadas para la entrega final.
