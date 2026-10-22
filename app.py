import pandas as pd
import plotly.express as px
import streamlit as st
from src.datos import cargar_visitantes, serie_temporal

st.set_page_config(page_title='Panorama de visitantes a Guatemala', page_icon='🌿', layout='wide')


@st.cache_data(show_spinner='Preparando los datos de visitantes…')
def datos():
    return cargar_visitantes()


def restablecer():
    for clave in ['periodo', 'regiones', 'vias', 'detalle', 'visibles']:
        st.session_state.pop(clave, None)
    st.session_state['version_barras'] = st.session_state.get('version_barras', 0) + 1


def estilo(fig):
    fig.update_layout(paper_bgcolor='#0B141B', plot_bgcolor='#14251F', font_color='#E7F0EB',
                      margin=dict(l=15, r=15, t=25, b=20), separators=',.',
                      xaxis=dict(gridcolor='#294037'), yaxis=dict(gridcolor='#294037'),
                      hoverlabel=dict(bgcolor='#14251F', font_color='#E7F0EB'))
    return fig


st.title('Panorama de visitantes a Guatemala')
st.write('Explora la afluencia y las vías de ingreso para orientar la planificación de servicios turísticos.')
st.caption('PANORAMA · Avance: evolución temporal y volumen por vía')
df = datos()
inicio, fin = df.Fecha.min(), df.Fecha.max()
with st.sidebar:
    st.header('Explorar visitantes')
    st.button('Restablecer filtros y selección', on_click=restablecer, width='stretch')
    meses = pd.date_range(inicio, fin, freq='MS').to_pydatetime().tolist()
    periodo = st.select_slider('Período', options=meses, value=(meses[0], meses[-1]),
                               format_func=lambda x: x.strftime('%m/%Y'), key='periodo')
    regiones = st.multiselect('Regiones de procedencia', sorted(df['Región dos'].dropna().unique()),
                              default=sorted(df['Región dos'].dropna().unique()), key='regiones')
    vias = st.multiselect('Vías de ingreso', sorted(df['Vía'].dropna().unique()),
                          default=sorted(df['Vía'].dropna().unique()), key='vias')
    detalle = st.radio('Nivel de detalle temporal', ['Mes', 'Trimestre', 'Año'], horizontal=True, key='detalle')
    visibles = st.multiselect('Gráficas visibles', ['Evolución temporal', 'Volumen por vía'],
                              default=['Evolución temporal', 'Volumen por vía'], key='visibles')
    st.caption('Visitantes = turistas + excursionistas. Los filtros se aplican a ambas gráficas.')

filtrado = df.loc[df.Fecha.between(*periodo) & df['Región dos'].isin(regiones) & df['Vía'].isin(vias)]
st.caption(f'Período seleccionado: {periodo[0]:%m/%Y}–{periodo[1]:%m/%Y} · {len(regiones)} regiones · {len(vias)} vías')
st.info('2026 contiene datos hasta junio. Compara períodos con los mismos meses. Los trimestres o años incompletos se identifican en el detalle de la gráfica.')
if filtrado.empty:
    st.warning('No hay información para esta selección. Elige al menos una región y una vía, o restablece los filtros.')
    st.stop()
if not visibles:
    st.info('Selecciona una o ambas gráficas en el panel lateral para explorar los datos.')
    st.stop()

# Los contenedores conservan el orden visual; la selección se procesa antes de dibujar la línea.
linea = st.container()
barras = st.container()
seleccionada = None
if 'Volumen por vía' in visibles:
    with barras:
        st.subheader('2. ¿Por dónde ingresan los visitantes?')
        st.write('Selecciona una barra para mostrar la evolución de esa vía en la primera gráfica.')
        totales = filtrado.groupby('Vía', as_index=False)['Viajero'].sum().sort_values('Viajero', ascending=False)
        total = totales.Viajero.sum()
        totales['Participación'] = totales.Viajero / total * 100 if total else 0
        fig = px.bar(totales, x='Vía', y='Viajero', custom_data=['Vía', 'Participación'],
                     labels={'Viajero': 'Visitantes'}, color_discrete_sequence=['#62D9C4'])
        fig.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,.0f} visitantes<br>%{customdata[1]:.1f}% del total filtrado<extra></extra>',
                          selected=dict(marker=dict(color='#F4B860')), unselected=dict(marker=dict(opacity=0.65)))
        evento = st.plotly_chart(estilo(fig), width='stretch', on_select='rerun',
                                 selection_mode='points', key=f"barras_{st.session_state.get('version_barras', 0)}")
        puntos = evento['selection']['points']
        if puntos:
            candidata = puntos[0]['customdata'][0]
            if candidata in vias:
                seleccionada = candidata
        st.button('Ver todas las vías en la evolución', on_click=lambda: st.session_state.update(
            version_barras=st.session_state.get('version_barras', 0) + 1))
        st.caption('La altura representa el volumen acumulado dentro del período y las regiones seleccionadas. Una vía con cero no implica ausencia real de actividad.')

if 'Evolución temporal' in visibles:
    with linea:
        st.subheader('1. ¿Cómo evoluciona la afluencia de visitantes?')
        detalle_df = filtrado if seleccionada is None else filtrado.loc[filtrado['Vía'].eq(seleccionada)]
        st.write(f"Mostrando: **{seleccionada or 'todas las vías seleccionadas'}** · suma por {detalle.lower()}.")
        serie = serie_temporal(detalle_df, {'Mes': 'M', 'Trimestre': 'Q', 'Año': 'Y'}[detalle])
        if serie.empty:
            st.warning('No hay datos para la vía seleccionada. Limpia la selección de barras.')
        else:
            fig = px.line(serie, x='Fecha', y='Visitantes', custom_data=['Cobertura'], markers=True,
                          color_discrete_sequence=['#62D9C4'])
            fig.update_traces(connectgaps=False, hovertemplate='%{x|%m/%Y}<br>%{y:,.0f} visitantes<br>%{customdata[0]}<extra></extra>')
            fig.update_layout(xaxis_title='Período', yaxis_title='Visitantes', dragmode='zoom')
            st.plotly_chart(estilo(fig), width='stretch', key='evolucion', config={'displaylogo': False})
            st.caption('Acerca una zona arrastrando sobre la gráfica; haz doble clic para recuperar la vista. Cambia el nivel de detalle en el panel lateral.')

with st.expander('Cómo interpretar la información'):
    st.write('Se reutiliza la definición comparable del Laboratorio 1: Turista + Excursionista. Las cantidades decimales de la fuente se conservan al calcular; el detalle visual se redondea a personas.')
    st.write('El cambio metodológico desde 2023 afecta otras categorías de viajero y la cobertura marítima requiere cautela. La caída alrededor de 2020 coincide con la pandemia; la gráfica por sí sola no establece causas.')
    st.write('Las entradas nacionales no equivalen a personas únicas, ventas, ocupación hotelera ni demanda de una empresa o destino particular. Los resultados son académicos y no se presentan como cifras oficiales.')
    st.caption('Fuente: base migratoria incluida en el Laboratorio 1 · enero de 2009–junio de 2026. Este avance presenta datos observados; la comparación predictiva corresponde a una etapa posterior.')
