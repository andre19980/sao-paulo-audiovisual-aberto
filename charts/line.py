import streamlit as st
import altair as alt
import pandas as pd

def plot_custom_line_chart(df, x, x_title, y, y_title, title, tooltip_format=',.0f', x_nice=None):
  tooltip_fields = []
  for campo in [x, y]:
    if campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  x_scale = alt.Undefined
  if x_nice is not None:
    x_scale = alt.Scale(nice=x_nice)

  base = (
    alt.Chart(df)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=x_scale, axis=alt.Axis(labelAngle=0, format='d')),
        y=alt.Y(f'{y}:Q', title=y_title),
        tooltip=tooltip_fields
      )
      .properties(
        title=alt.TitleParams(
          text=title,
          anchor='start',
        )
      )
  )

  hover_selection = alt.selection_point(
    on='mouseover',
    nearest=True,
    fields=[x],
    empty=False,
    clear='mouseout'
  )

  line_layer = base.mark_line()

  point_layer = base.mark_circle(size=80).encode(
    opacity=alt.condition(hover_selection, alt.value(1), alt.value(0))
  ).add_params(
    hover_selection 
  )

  final_chart = (line_layer + point_layer).configure_axisX(grid=False).configure_view(strokeOpacity=0)
  st.altair_chart(final_chart)
  
  return

def plot_custom_grouped_line_chart(df, x, x_title, y, y_title, group, group_title, title, color_scheme='dark2', tooltip=None, tooltip_format=',.0f', height='500px', key=None):
  """Line chart com uma linha por grupo da coluna 'group' (ECharts).

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset em formato longo, com uma linha por (x, group).
  x : str
    Coluna numérica do eixo X (ex.: ano).
  x_title : str
    Título do eixo X.
  y : str
    Coluna numérica do eixo Y.
  y_title : str
    Título do eixo Y.
  group : str
    Coluna categórica que define os grupos (uma linha por grupo).
  group_title : str
    Título da legenda de cor (default None = sem legenda).
  title : str
    Título do gráfico.
  color_scheme : str
    Nome da paleta de cores do ECharts (ex.: 'dark2' -> 'dark', 'category',
    'vintage', 'macarons'). Default 'dark2'.
  tooltip : list | None
    Campos do tooltip (default [x, group, y]). Mantido por compatibilidade;
    o ECharts mostra automaticamente os valores.
  tooltip_format : str
    Formato (d3-format) das colunas numéricas no tooltip (default ',.0f').
  height : str
    Altura do gráfico (CSS, ex.: '500px').
  key : str | None
    Chave estável do componente Streamlit (sem espaços/acentos).
  """
  from streamlit_echarts import st_echarts

  # Paletas predefinidas (nome -> lista de cores).
  _PALETAS = {
    'dark2': ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02', '#a6761d', '#666666'],
    'category': ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4'],
    'dark': ['#dd6b66', '#759aa0', '#e69d87', '#8dc1a9', '#ea7e53', '#eedd78', '#73a373', '#73b9bc'],
    'vintage': ['#d87c7c', '#919e8b', '#d7ab82', '#6e7074', '#61a0a8', '#efa18d', '#787464', '#cc7e63'],
    'macarons': ['#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80', '#8d98b3', '#e5cf0d', '#97b552'],
  }
  palette = _PALETAS.get(color_scheme, list(_PALETAS.get('dark2', [])))

  pivot = df.pivot_table(index=x, columns=group, values=y, aggfunc='sum', fill_value=0)
  pivot = pivot.sort_index()
  xs = pivot.index.tolist()
  group_names = pivot.columns.tolist()

  series = []
  for i, gname in enumerate(group_names):
    series.append({
      'name': gname,
      'type': 'line',
      'smooth': False,
      'symbolSize': 6,
      'data': [float(pivot.loc[xx, gname]) for xx in xs],
      'itemStyle': {'color': palette[i % len(palette)]},
      'lineStyle': {'color': palette[i % len(palette)]},
    })

  options = {
    'title': {'text': title, 'left': 'center', 'top': 0},
    'tooltip': {'trigger': 'axis'},
    'legend': {'data': group_names, 'top': 36},
    'grid': {'left': '3%', 'right': '4%', 'top': 120, 'bottom': '3%', 'containLabel': True},
    'xAxis': {
      'type': 'category',
      'name': x_title,
      'data': xs,
    },
    'yAxis': {
      'type': 'value',
      'name': y_title,
      'nameLocation': 'middle',
      'nameGap': 40,
    },
    'series': series,
  }

  st_echarts(
    options=options,
    height=height,
    key=key,
  )

  return
