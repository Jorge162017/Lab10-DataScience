"""Preparación de visitantes comparables, siguiendo el Laboratorio 1."""
from pathlib import Path
import pandas as pd

ARCHIVO = Path(__file__).resolve().parents[1] / 'referencias' / 'lab1' / 'Laboratorio 1. Series de Tiempo 2026 - Base_Migracion_2009-2026jun.xlsx'


def cargar_visitantes():
    df = pd.read_excel(ARCHIVO, sheet_name='Datos')
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].astype('string').str.strip().str.replace(r'\s+', ' ', regex=True)
    df['Región dos'] = df['Región dos'].replace('0', 'Sin clasificar')
    for col in ['Año', 'Mes cod', 'Viajero']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.drop_duplicates().copy()
    df['Fecha'] = pd.to_datetime(dict(year=df['Año'], month=df['Mes cod'], day=1), errors='coerce')
    df = df.loc[df['Fecha'].notna() & df['Viajero'].notna() & df['Viajero'].ge(0)]
    df = df.loc[df['Tipo de Viajero'].isin(['Turista', 'Excursionista'])]
    return df.groupby(['Fecha', 'Región dos', 'Vía'], as_index=False, dropna=False)['Viajero'].sum()


def serie_temporal(df, frecuencia):
    """Conservar meses sin registros como ausentes, sin inventar ceros."""
    mensual = df.groupby('Fecha')['Viajero'].sum().sort_index()
    if mensual.empty:
        return pd.DataFrame(columns=['Fecha', 'Visitantes', 'Cobertura'])
    mensual = mensual.reindex(pd.date_range(mensual.index.min(), mensual.index.max(), freq='MS'))
    periodos = mensual.index.to_period(frecuencia)
    filas = []
    for periodo in periodos.unique():
        valores = mensual[periodos == periodo]
        esperados = {'M': 1, 'Q': 3, 'Y': 12}[frecuencia]
        completos = valores.notna().sum() == esperados
        filas.append({'Fecha': periodo.start_time, 'Visitantes': valores.sum(min_count=1),
                      'Cobertura': 'Completo' if completos else f'Parcial: {valores.notna().sum()} de {esperados} meses'})
    return pd.DataFrame(filas)


def estacionalidad(df, inicio, fin):
    """Matriz año × mes: ausencias como NaN, ceros registrados como cero."""
    mensual = df.groupby('Fecha')['Viajero'].sum()
    indice = pd.date_range(inicio, fin, freq='MS')
    tabla = mensual.reindex(indice).rename('Visitantes').to_frame()
    tabla['Año'] = tabla.index.year
    tabla['Mes'] = tabla.index.month
    return tabla.pivot(index='Año', columns='Mes', values='Visitantes').reindex(columns=range(1, 13))


def evolucion_regional(df, regiones, frecuencia):
    partes = []
    for region in regiones:
        serie = serie_temporal(df.loc[df['Región dos'].eq(region)], frecuencia)
        serie['Región'] = region
        partes.append(serie)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def composicion_regional(df):
    tabla = df.groupby(['Región dos', 'Vía'], as_index=False)['Viajero'].sum()
    totales = tabla.groupby('Región dos')['Viajero'].transform('sum')
    tabla['Participación'] = tabla.Viajero.div(totales.where(totales.gt(0))) * 100
    return tabla
