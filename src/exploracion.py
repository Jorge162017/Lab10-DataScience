"""Visualizaciones exploratorias 3–6."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.datos import estacionalidad, evolucion_regional, composicion_regional

MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
PALETA = ['#62D9C4', '#A9BCFF', '#F4B860', '#DCA7D8', '#86C7F3', '#D6D17C',
          '#F49D90', '#A5D69A', '#C7B4ED', '#B6C7BE', '#E4C6A3']
VIAS = {'Aérea': '#A9BCFF', 'Terrestre': '#62D9C4', 'Marítima': '#F4B860'}


def mostrar_estacionalidad(df, periodo, estilo):
    st.subheader('3. ¿En qué meses se concentra la afluencia?')
    st.write('Selecciona el centro de una celda para consultar el desglose por vía de ese mes en la gráfica 2.')
    matriz = estacionalidad(df, *periodo)
    fig = px.imshow(matriz.to_numpy(), x=MESES, y=[str(x) for x in matriz.index],
                    aspect='auto', color_continuous_scale=['#14251F', '#287B69', '#62D9C4'],
                    labels={'x': 'Mes', 'y': 'Año', 'color': 'Visitantes'})
    fig.update_traces(hoverongaps=False,
                      hovertemplate='%{y} · %{x}<br>%{z:,.0f} visitantes<extra></extra>')
    fig.update_layout(height=max(360, min(750, len(matriz) * 30 + 140)))
    fig.update_xaxes(side='bottom')
    # Heatmap no emite selecciones de puntos: una capa Scatter sobre las celdas
    # con datos permite seleccionar meses sin convertir las ausencias en ceros.
    puntos = [(str(a), MESES[m - 1], f'{a}-{m:02d}-01', float(v))
              for a, fila in matriz.iterrows() for m, v in fila.items() if pd.notna(v)]
    fig.add_trace(go.Scatter(x=[p[1] for p in puntos], y=[p[0] for p in puntos],
                            mode='markers', showlegend=False,
                            customdata=[[p[2], p[3]] for p in puntos],
                            marker=dict(symbol='square', size=24, color='#FFFFFF', opacity=0.01),
                            selected=dict(marker=dict(opacity=0.7, color='#F4B860')),
                            unselected=dict(marker=dict(opacity=0.01)),
                            hovertemplate='%{y} · %{x}<br>%{customdata[1]:,.0f} visitantes<extra></extra>'))
    evento = st.plotly_chart(estilo(fig), width='stretch', on_select='rerun', selection_mode='points',
                             key=f"estacionalidad_{st.session_state.get('version_mapa', 0)}")
    seleccion = None
    for punto in evento['selection']['points']:
        valor = punto.get('customdata', [])
        if valor:
            fecha = pd.to_datetime(valor[0], errors='coerce')
            if pd.notna(fecha) and pd.Timestamp(periodo[0]) <= fecha <= pd.Timestamp(periodo[1]) and df.Fecha.eq(fecha).any():
                seleccion = fecha
    if seleccion is not None:
        st.success(f'Mes seleccionado: {seleccion:%m/%Y}. La gráfica 2 muestra sus vías de ingreso.')
    st.button('Quitar selección de mes', key='limpiar_mes', on_click=lambda: st.session_state.update(
        version_mapa=st.session_state.get('version_mapa', 0) + 1))
    st.caption('Cada celda representa un mes. Los espacios vacíos indican meses fuera del período o sin registros; no se convierten en cero. El mapa usa datos mensuales aunque cambies el detalle de las líneas.')
    return seleccion


def mostrar_mercados(df, visibles, detalle, colores, estilo):
    ranking = df.groupby('Región dos')['Viajero'].sum().sort_values(ascending=False)
    regiones = ranking.index.tolist()
    regiones_activas = []
    if 'Mercados de origen' in visibles:
        st.subheader('4. ¿Qué regiones aportan más visitantes?')
        st.session_state.setdefault('cantidad_regiones', min(5, len(regiones)))
        cantidad = st.selectbox('Cantidad de regiones en el ranking', list(range(1, len(regiones) + 1)),
                                index=None, key='cantidad_regiones', filter_mode=None)
        tabla = ranking.head(cantidad).rename('Visitantes').reset_index()
        total = ranking.sum()
        tabla['Participación'] = tabla.Visitantes / total * 100 if total else 0
        fig = px.bar(tabla, x='Visitantes', y='Región dos', orientation='h', color='Región dos',
                     color_discrete_map=colores, custom_data=['Región dos', 'Participación'],
                     labels={'Región dos': 'Región de procedencia'})
        fig.update_layout(showlegend=False, height=max(320, cantidad * 38 + 120))
        fig.update_yaxes(categoryorder='array', categoryarray=tabla['Región dos'].tolist()[::-1])
        fig.update_traces(hovertemplate='%{y}<br>%{x:,.0f} visitantes<br>%{customdata[1]:.1f}% del total filtrado<extra></extra>')
        st.write('Selecciona una barra para explorar esa región en las gráficas 5 y 6. Usa Mayús para seleccionar varias regiones.')
        fig.update_traces(selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=0.35)))
        evento = st.plotly_chart(estilo(fig), width='stretch', on_select='rerun',
                                 selection_mode=['points', 'box', 'lasso'],
                                 key=f"mercados_{st.session_state.get('version_mercados', 0)}")
        regiones_activas = list(dict.fromkeys(p['customdata'][0] for p in evento['selection']['points']
                              if p.get('customdata') and p['customdata'][0] in tabla['Región dos'].values))
        st.button('Quitar selección de regiones del ranking', key='limpiar_ranking',
                  on_click=lambda: st.session_state.update(version_mercados=st.session_state.get('version_mercados', 0) + 1))
        st.caption('El ranking suma el período y las vías seleccionadas. El porcentaje usa todas las regiones filtradas, aunque solo se muestren las primeras del ranking.')

    if regiones_activas:
        st.success('Regiones seleccionadas en el ranking: ' + ', '.join(regiones_activas))
    detalle_df = df.loc[df['Región dos'].isin(regiones_activas)] if regiones_activas else df

    if 'Evolución por región' in visibles:
        st.subheader('5. ¿Cómo evoluciona cada mercado de origen?')
        if 'comparar_regiones' not in st.session_state:
            st.session_state['comparar_regiones'] = regiones[:3]
        if regiones_activas:
            seleccion = regiones_activas
            st.caption('La selección del ranking controla esta evolución. Limpia esa selección para elegir regiones manualmente.')
        else:
            seleccion = st.multiselect('Regiones a comparar en la evolución', regiones, key='comparar_regiones', filter_mode=None, wrap=True)
        if not seleccion:
            st.info('Selecciona al menos una región para ver su evolución.')
        else:
            tabla = evolucion_regional(df, seleccion, {'Mes': 'M', 'Trimestre': 'Q', 'Año': 'Y'}[detalle])
            fig = px.line(tabla, x='Fecha', y='Visitantes', color='Región', color_discrete_map=colores,
                          custom_data=['Región', 'Cobertura'], markers=True)
            fig.update_traces(connectgaps=False, hovertemplate='%{customdata[0]}<br>%{x|%m/%Y}<br>%{y:,.0f} visitantes<br>%{customdata[1]}<extra></extra>')
            fig.update_layout(xaxis_title='Período', yaxis_title='Visitantes', legend_title_text='Región de procedencia')
            st.plotly_chart(estilo(fig), width='stretch', key='evolucion_regional')
            st.caption('Compara volúmenes absolutos con el mismo período y agregación. Usa la leyenda para ocultar o recuperar una serie y arrastra para acercar un tramo.')

    if 'Composición región–vía' in visibles:
        st.subheader('6. ¿Qué vías predominan en cada región?')
        modo = st.radio('Mostrar composición como', ['Porcentaje', 'Cantidad de visitantes'], horizontal=True, key='modo_composicion')
        tabla = composicion_regional(detalle_df)
        sin_volumen = tabla.groupby('Región dos')['Viajero'].sum().eq(0)
        if modo == 'Porcentaje':
            tabla = tabla.loc[tabla['Participación'].notna()]
        if tabla.empty:
            st.info('Las regiones seleccionadas no registran volumen positivo: no se puede calcular su composición porcentual.')
        else:
            campo = 'Participación' if modo == 'Porcentaje' else 'Viajero'
            fig = px.bar(tabla, x=campo, y='Región dos', color='Vía', orientation='h',
                          color_discrete_map=VIAS, custom_data=['Vía', 'Viajero', 'Participación'],
                          labels={'Participación': 'Participación (%)', 'Viajero': 'Visitantes', 'Región dos': 'Región de procedencia'})
            fig.update_layout(barmode='stack', height=max(350, len(regiones) * 38 + 120))
            if modo == 'Porcentaje':
                fig.update_xaxes(range=[0, 100], ticksuffix='%')
            fig.update_yaxes(categoryorder='array', categoryarray=regiones[::-1])
            fig.update_traces(hovertemplate='%{y} · %{customdata[0]}<br>%{customdata[1]:,.0f} visitantes<br>Participación: %{customdata[2]:.1f}%<extra></extra>')
            st.plotly_chart(estilo(fig), width='stretch', key='composicion')
        st.caption('En modo porcentaje, cada región con volumen positivo suma 100% entre las vías filtradas. Cambia a cantidades para comparar el tamaño de los flujos. El ranking permite enfocar ambas gráficas en una o varias regiones.')
        if sin_volumen.any():
            st.caption('Sin porcentaje por volumen cero: ' + ', '.join(sin_volumen[sin_volumen].index))
