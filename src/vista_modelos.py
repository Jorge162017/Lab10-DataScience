import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.modelos import cargar_resultados, evaluar

COLORES = {'ARIMA/SARIMA': '#A9BCFF', 'Suavizamiento exponencial': '#F4B860', 'Holt-Winters': '#DCA7D8'}


@st.cache_data
def resultados():
    return cargar_resultados()


def mostrar_modelos(estilo):
    st.header('Modelos y límites')
    try:
        pred, metricas_originales, observados, meta = resultados()
    except FileNotFoundError:
        st.error('No se encontraron los archivos de resultados en data/modelos. Revisa la instalación del repositorio.')
        return
    st.write('Compara tres métodos ya utilizados en el Laboratorio 1: sus predicciones históricas y el error frente a los visitantes observados.')
    with st.container(border=True):
        st.markdown('**¿Qué quieres comparar?**')
        izquierda, derecha = st.columns([1, 2])
        with izquierda:
            nombres = list(dict.fromkeys(pred.Serie))
            serie = st.selectbox('Serie evaluada', nombres, key='serie_modelo', filter_mode=None)
        with derecha:
            modelos = st.pills('Modelos visibles', list(COLORES), selection_mode='multi',
                               default=list(COLORES), key='modelos_visibles')
        fechas = sorted(pred.Fecha.unique())
        with st.expander('Ajustar período y gráficas'):
            periodo = st.select_slider('Período de evaluación', fechas, value=(fechas[0], fechas[-1]),
                                       format_func=lambda x: pd.Timestamp(x).strftime('%m/%Y'), key='periodo_modelos')
            visibles = st.pills('Gráficas de modelos', ['Observado y predicho', 'Error de los modelos'], selection_mode='multi',
                                default=['Observado y predicho', 'Error de los modelos'], key='graficas_modelos')
            contexto = st.checkbox('Mostrar últimos 12 meses de entrenamiento', value=True, key='contexto_modelos')
        st.caption('Esta comparación tiene su propio período y solo incluye las siete series evaluadas.')
    st.info('Evaluación histórica: entrenamiento hasta marzo de 2021 y prueba de abril de 2021 a junio de 2026 (63 meses). Los pronósticos se hicieron desde un único corte, sin actualizarse con los datos reales de prueba. No son predicciones actuales ni posteriores a junio de 2026.')
    if 'Marítima' in serie:
        st.warning('La serie marítima comparable registra ceros en toda la prueba. Un error cercano a cero refleja la cobertura de esta fuente y no demuestra ausencia real de actividad ni superioridad general del modelo.')
    if not modelos:
        st.warning('Selecciona al menos un modelo para explorar sus resultados; selecciona los tres para compararlos.')
        return
    muestra = pred.loc[pred.Serie.eq(serie) & pred.Modelo.isin(modelos) & pred.Fecha.between(*periodo)].copy()
    st.caption(f'Serie: {serie} · período evaluado: {pd.Timestamp(periodo[0]):%m/%Y}–{pd.Timestamp(periodo[1]):%m/%Y} · {muestra.Fecha.nunique()} meses · {len(modelos)} modelos')
    if periodo[0] != fechas[0] or periodo[1] != fechas[-1]:
        st.caption('Las barras se recalculan sobre el intervalo seleccionado; pueden diferir de la evaluación completa del Laboratorio 1.')
    curva = st.container()
    barras = st.container()
    enfocado = None
    if 'Error de los modelos' in visibles:
        with barras:
            st.subheader('8. ¿Qué modelo registra menor error?')
            metrica = st.radio('Medida de error', ['RMSE', 'MAE'], horizontal=True, key='metrica_modelos')
            st.caption(('RMSE penaliza más los errores grandes.' if metrica == 'RMSE' else 'MAE es el error absoluto promedio.') + ' Se mide en visitantes; menor es mejor.')
            resumen = evaluar(muestra).sort_values(metrica)
            st.write('Selecciona una barra para enfocar ese modelo en la gráfica 7.')
            fig = px.bar(resumen, x='Modelo', y=metrica, color='Modelo', color_discrete_map=COLORES,
                         custom_data=['Modelo', 'Meses'])
            fig.update_traces(hovertemplate='%{customdata[0]}<br>%{y:,.0f} visitantes de error<br>%{customdata[1]} meses evaluados<extra></extra>',
                              selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=.4)))
            fig.update_layout(showlegend=False, yaxis_title=f'{metrica} (visitantes)', xaxis_title=None)
            # El contexto en la clave evita conservar una selección de otra serie o métrica.
            clave = f"errores_{serie}_{metrica}_{st.session_state.get('version_errores', 0)}"
            evento = st.plotly_chart(estilo(fig), width='stretch', on_select='rerun', selection_mode='points', key=clave)
            puntos = evento['selection']['points']
            if puntos and puntos[0].get('customdata', [None])[0] in modelos:
                enfocado = puntos[0]['customdata'][0]
            st.button('Volver a comparar todos los modelos', key='limpiar_modelo', on_click=lambda: st.session_state.update(
                version_errores=st.session_state.get('version_errores', 0) + 1))
            st.caption('Todos los modelos se comparan con los mismos meses observados y en la misma escala. Menor error histórico no garantiza mejor desempeño futuro.')
    if 'Observado y predicho' in visibles:
        with curva:
            st.subheader('7. ¿Qué tan cerca estuvieron las predicciones?')
            if enfocado:
                st.success(f'Modelo enfocado desde las barras: {enfocado}')
            fig = go.Figure()
            reales = muestra.drop_duplicates('Fecha').sort_values('Fecha')
            if contexto:
                train = observados.loc[observados.Serie.eq(serie) & observados.Conjunto.eq('Entrenamiento')].tail(12)
                fig.add_trace(go.Scatter(x=train.Fecha, y=train.Observado, name='Entrenamiento', line=dict(color='#B6C7BE')))
            fig.add_trace(go.Scatter(x=reales.Fecha, y=reales.Observado, name='Observado en prueba',
                                    line=dict(color='#62D9C4', width=3)))
            for modelo in ([enfocado] if enfocado else modelos):
                tabla = muestra.loc[muestra.Modelo.eq(modelo)].sort_values('Fecha')
                fig.add_trace(go.Scatter(x=tabla.Fecha, y=tabla.Predicho, name=modelo,
                                        line=dict(color=COLORES[modelo], dash='dash'),
                                        customdata=(tabla.Predicho - tabla.Observado).to_numpy(),
                                        hovertemplate='%{x|%m/%Y}<br>Predicción: %{y:,.0f}<br>Predicho − observado: %{customdata:,.0f}<extra>%{fullData.name}</extra>'))
            fig.add_vline(x=pd.Timestamp(meta['prueba_inicio']).timestamp() * 1000, line_dash='dot', line_color='#B6C7BE')
            fig.update_layout(xaxis_title='Mes', yaxis_title='Visitantes', hovermode='x unified', legend_title_text=None)
            st.plotly_chart(estilo(fig), width='stretch', key='predicciones', config={'displaylogo': False})
            st.caption('Línea continua: observado. Líneas discontinuas: estimaciones. Arrastra para acercar un tramo y usa la leyenda para ocultar series. La línea vertical marca el inicio de la prueba; el contexto de entrenamiento no interviene en las métricas.')
    if not visibles:
        st.info('Activa al menos una gráfica en «Ajustar período y gráficas».')
    st.download_button('Descargar predicciones del período (CSV)', muestra.to_csv(index=False).encode('utf-8-sig'),
                       file_name='comparacion_modelos.csv', mime='text/csv')
    with st.expander('Evaluación completa, métodos y limitaciones'):
        st.write('Errores sobre los 63 meses completos de prueba:')
        st.dataframe(metricas_originales.loc[metricas_originales.Serie.eq(serie), ['Modelo', 'MAE', 'RMSE', 'Meses']],
                     hide_index=True, width='stretch', column_config={
                         'MAE': st.column_config.NumberColumn('MAE (visitantes)', format='%.2f'),
                         'RMSE': st.column_config.NumberColumn('RMSE (visitantes)', format='%.2f')})
        st.write('Suavizamiento exponencial estima un nivel; Holt–Winters combina nivel, tendencia amortiguada y estacionalidad anual; ARIMA/SARIMA usa dependencias temporales y una transformación logarítmica. La configuración SARIMA de esta serie es: ' + meta['sarima_seleccionados'][serie])
        st.write('La recuperación pospandemia no estaba disponible al ajustar los modelos. El error en este horizonte refleja tanto sus limitaciones como el cambio estructural. No se atribuyen causas ni se garantizan ventas u ocupación empresarial.')
        st.write('Procedencia: se reprodujeron los ajustes existentes del Lab 1 con su misma configuración y corte para exportar las curvas numéricas; no se buscaron modelos nuevos. Streamlit solo lee los CSV y calcula métricas del período seleccionado.')
        coinciden = meta['comparaciones_coincidentes_al_redondeo']
        total = meta['comparaciones_totales']
        st.caption(f'Contraste con las tablas guardadas del notebook: {coinciden} de {total} combinaciones serie–modelo coinciden en MAE y RMSE al redondeo publicado. Las columnas de referencia conservan los valores originales redondeados.')
        if coinciden != total:
            st.warning('Algunos ajustes reproducidos difieren del redondeo publicado. Las curvas y las barras utilizan los valores reproducidos, no sustituyen las métricas originales. Consulta las columnas de referencia para ver la diferencia.')
        st.caption('LSTM no se mezcla en esta comparación: en el Lab 2 usa ventanas con observaciones reales previas de prueba, mientras aquí se evalúa un horizonte fijo desde un solo corte.')
