import streamlit as st
import altair as alt
import pandas as pd

def plot_custom_grouped_bar_chart(df, x, x_title, y, y_title, x_offset, x_offset_title, title, x_scale_sort=None, tooltip=None, tooltip_format=',.0f'):
  if tooltip is None:
    tooltip = [y]

  # Aplica o formato às colunas numéricas do tooltip (texto fica intacto).
  tooltip_fields = []
  for campo in tooltip:
    if isinstance(campo, alt.Tooltip):
      tooltip_fields.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title, sort=x_scale_sort),
      y=alt.Y(f'{y}:Q', title=y_title),
      xOffset=alt.XOffset(f'{x_offset}:N', title=x_offset_title),
      color=f'{x_offset}:N',
      tooltip=tooltip_fields
    ).properties(
      title=alt.TitleParams(
        text=title,
        anchor='start'
      )
    )
  )

  st.altair_chart(chart)

  return

def plot_custom_ranking_bar_chart(df, x, x_title, y, y_title, title, tooltip=None, color=None, color_scheme='blues', label_limit=200, step=22, log_x=False, tooltip_format=',.0f'):
  """Barra horizontal de ranking: categorias no eixo Y ordenadas pelo valor de 'x'.

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset com as colunas apontadas por 'x' e 'y'.
  x : str
    Coluna numérica com o valor das barras (eixo X).
  x_title : str
    Título do eixo X.
  y : str
    Coluna categórica com o rótulo de cada barra (eixo Y).
  y_title : str
    Título do eixo Y.
  title : str
    Título do gráfico.
  tooltip : list[str] | None
    Colunas exibidas no tooltip (default: [y, x]).
  color : str | None
    Coluna numérica que controla a cor das barras (default None = cor única).
  color_scheme : str
    Esquema de cor usado quando 'color' é informado (default 'blues').
  label_limit : int
    Limite de largura dos rótulos do eixo Y.
  step : int
    Altura por barra (padding do eixo Y).
  log_x : bool
    Usar escala logarítmica no eixo X (default False).
  tooltip_format : str
    Formato (d3-format) aplicado às colunas numéricas do tooltip
    (default ',.0f' = separador de milhar). Colunas de texto ficam intactas.
  """
  if tooltip is None:
    tooltip = [y, x]

  # Aplica o formato às colunas numéricas do tooltip (texto fica intacto).
  tooltip_fields = []
  for campo in tooltip:
    if isinstance(campo, alt.Tooltip):
      tooltip_fields.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  color_encoding = (
    alt.Color(f'{color}:Q', legend=None, scale=alt.Scale(scheme=color_scheme))
    if color is not None
    else alt.value('#4c78a8')
  )

  chart = (
    alt.Chart(df)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Undefined),
        y=alt.Y(f'{y}:N', title=y_title, sort='-x', axis=alt.Axis(labelLimit=label_limit)),
        color=color_encoding,
        tooltip=tooltip_fields,
      )
      .properties(
        height={'step': step},
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  st.altair_chart(chart)

  return

def plot_custom_layered_bar_chart(df, x, x_title, y, y_title, color, color_title, title, sort_by=None, tooltip=None, label_limit=200, step=26, opacity=0.7, tooltip_format=',.0f', color_scheme=None):
  """Barra horizontal em camadas: categorias no eixo Y com barras sobrepostas por grupo.

  Cada categoria do eixo Y recebe uma barra por valor distinto da coluna 'color',
  sobrepostas (stack=None) — útil para comparar uma parte (ex.: São Paulo) dentro
  de um total (ex.: Brasil).

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset em formato longo, com as colunas apontadas por 'x', 'y' e 'color'.
  x : str
    Coluna numérica com o comprimento das barras (eixo X).
  x_title : str
    Título do eixo X.
  y : str
    Coluna categórica com o rótulo de cada barra (eixo Y).
  y_title : str
    Título do eixo Y.
  color : str
    Coluna categórica que define os grupos sobrepostos (cor).
  color_title : str
    Título da legenda de cor (default None = sem legenda).
  title : str
    Título do gráfico.
  sort_by : str | None
    Coluna usada para ordenar o eixo Y (default None = ordem dos dados).
  tooltip : list | None
    Campos do tooltip (default [y, color, x]). Colunas numéricas recebem
    'tooltip_format'.
  label_limit : int
    Limite de largura dos rótulos do eixo Y.
  step : int
    Altura por barra (padding do eixo Y).
  opacity : float
    Opacidade das barras (default 0.7).
  tooltip_format : str
    Formato (d3-format) das colunas numéricas no tooltip (default ',.0f').
  color_scheme : str | None
    Esquema de cor para os grupos (default None = paleta padrão do Altair).
  """
  if tooltip is None:
    tooltip = [y, color, x]

  tooltip_fields = []
  for campo in tooltip:
    if isinstance(campo, alt.Tooltip):
      tooltip_fields.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  y_encoding = alt.Y(f'{y}:N', title=y_title, axis=alt.Axis(labelLimit=label_limit))
  if sort_by is not None:
    # Em formato longo cada categoria aparece em várias linhas (ex.: Brasil/SP);
    # deduplica após ordenar para gerar uma lista de ordem sem repetições.
    ordem = df.sort_values(sort_by, ascending=False).drop_duplicates(y)[y].tolist()
    y_encoding = alt.Y(f'{y}:N', title=y_title, sort=ordem, axis=alt.Axis(labelLimit=label_limit))

  color_kwargs = {'title': color_title}
  if color_scheme is not None:
    color_kwargs['scale'] = alt.Scale(scheme=color_scheme)

  chart = (
    alt.Chart(df)
      .mark_bar(opacity=opacity)
      .encode(
        y=y_encoding,
        x=alt.X(f'{x}:Q', title=x_title).stack(None),
        color=alt.Color(f'{color}:N', **color_kwargs),
        tooltip=tooltip_fields,
      )
      .properties(
        height={'step': step},
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  st.altair_chart(chart)

  return

def plot_custom_stacked_bar_chart(df, x, x_title, y, y_title, color, color_title, title, x_scale_sort=None, tooltip=None, tooltip_format=',.0f', height=None):
  """Barra vertical com uma barra por categoria, colorida pela própria categoria.

  Útil para comparar uma medida (eixo Y) entre categorias do eixo X, dando uma
  cor distinta para cada categoria (ex.: proporção de assentos acessíveis por
  categoria de exibidor).

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset com as colunas apontadas por 'x', 'y' e 'color'.
  x : str
    Coluna categórica do eixo X.
  x_title : str
    Título do eixo X.
  y : str
    Coluna numérica com o valor das barras (eixo Y).
  y_title : str
    Título do eixo Y.
  color : str
    Coluna categórica que dá cor a cada barra (mesma de 'x' na maioria dos casos).
  color_title : str
    Título da legenda de cor.
  title : str
    Título do gráfico.
  x_scale_sort : list | None
    Ordem das categorias no eixo X (default None = ordem dos dados).
  tooltip : list | None
    Campos do tooltip (default [x, color, y]). Colunas numéricas recebem
    'tooltip_format'.
  tooltip_format : str
    Formato (d3-format) das colunas numéricas no tooltip (default ',.0f').
  height : int | None
    Altura do gráfico em pixels (default None = automática).
  """
  if tooltip is None:
    tooltip = [x, color, y]

  # Aplica o formato às colunas numéricas do tooltip (texto fica intacto).
  tooltip_fields = []
  for campo in tooltip:
    if isinstance(campo, alt.Tooltip):
      tooltip_fields.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title, sort=x_scale_sort),
      y=alt.Y(f'{y}:Q', title=y_title, stack='zero'),
      color=alt.Color(f'{color}:N', title=color_title),
      tooltip=tooltip_fields
    ).properties(
      height=height,
      title=alt.TitleParams(
        text=title,
        anchor='start'
      )
    )
  )

  st.altair_chart(chart)

  return

def plot_custom_stacked_horizontal_bar_echarts(df, y, x, series, series_title, title, color_scheme=None, height='520px', normalize=True, key=None):
  """Barra horizontal empilhada normalizada (100%) usando ECharts.

  Cada categoria do eixo Y é uma barra composta pelas séries da coluna 'series',
  e o comprimento de cada fatia é a participação (%) da série naquela categoria.
  Quando 'normalize' é True, as barras somam 100%; caso contrário, mostram o
  valor absoluto.

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset em formato longo, com as colunas apontadas por 'y', 'x' e 'series'.
  y : str
    Coluna categórica do eixo Y (categorias das barras).
  x : str
    Coluna numérica com o valor de cada fatia.
  series : str
    Coluna categórica que define as séries (cores).
  series_title : str
    Título da legenda de séries.
  title : str
    Título do gráfico.
  color_scheme : str | list[str] | None
    Paleta de cores das séries: pode ser uma lista de cores hex/rgb (ex.:
    ['#5470c6', '#91cc75', ...]) ou o nome de uma paleta predefinida
    (ex.: 'category', 'dark', 'vintage', 'macarons', 'infographic',
    'shine', 'roma', 'walden'). Default None = paleta padrão do ECharts.
  height : str
    Altura do gráfico (CSS, ex.: '520px').
  normalize : bool
    Se True, converte cada linha para porcentagem (soma 100); se False, usa
    os valores absolutos.
  key : str | None
    Chave do componente Streamlit. Se informada, deve ser uma string estável
    (sem espaços/acentos), evitando que o gráfico remonte a cada rerun.
  """
  from streamlit_echarts import st_echarts, JsCode

  # Paletas predefinidas do ECharts (mapa nome -> lista de cores).
  _PALETAS = {
    'category': ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'],
    'dark': ['#dd6b66', '#759aa0', '#e69d87', '#8dc1a9', '#ea7e53', '#eedd78', '#73a373', '#73b9bc', '#7289ab'],
    'vintage': ['#d87c7c', '#919e8b', '#d7ab82', '#6e7074', '#61a0a8', '#efa18d', '#787464', '#cc7e63', '#724e47'],
    'macarons': ['#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80', '#8d98b3', '#e5cf0d', '#97b552', '#95706d'],
    'infographic': ['#c1232b', '#27727b', '#fcce10', '#e87c25', '#b5c334', '#fe8463', '#9bca63', '#fad860', '#f3a43b'],
    'shine': ['#c12e34', '#e6b600', '#0098d9', '#2b821d', '#005eaa', '#339ca8', '#cda819', '#32a487'],
    'roma': ['#e01f54', '#001852', '#f5e8c8', '#b8d2c7', '#c6b38e', '#a4d8c2', '#f3d999', '#d3758f', '#dcc392'],
    'walden': ['#3fb1e3', '#6be6c1', '#626c91', '#a0a7e6', '#c4ebad', '#96dee8', '#c89f4f', '#4e73b9'],
  }
  colors = None
  if isinstance(color_scheme, str) and color_scheme in _PALETAS:
    colors = _PALETAS[color_scheme]
  elif color_scheme is not None:
    colors = color_scheme  # lista de cores fornecida diretamente

  pivot = df.pivot_table(index=y, columns=series, values=x, aggfunc='sum', fill_value=0)
  categorias = pivot.index.tolist()
  series_names = pivot.columns.tolist()

  data = {}
  for cat in categorias:
    row = pivot.loc[cat]
    total = float(row.sum())
    if normalize and total > 0:
      data[cat] = [round(float(row[s]) / total * 100, 1) for s in series_names]
    else:
      data[cat] = [float(row[s]) for s in series_names]

  # Paleta de cores das séries. Se definida, aplica a cor em cada série
  # via itemStyle (mais robusto que depender apenas do color global).
  palette = colors or []
  series = []
  for i, s in enumerate(series_names):
    cor = palette[i % len(palette)] if palette else None
    item = {
      'name': s,
      'type': 'bar',
      'stack': 'total',
      'barWidth': '60%',
      'label': {
        'show': True,
        'formatter': JsCode('function(params) { return Math.round(params.value * 10) / 10 + "%"; }').js_code
        if normalize else {'show': False},
      },
      'data': [data[cat][i] for cat in categorias],
    }
    if cor is not None:
      item['itemStyle'] = {'color': cor}
    series.append(item)

  options = {
    'title': {'text': title, 'left': 'center', 'top': 0},
    'tooltip': {
      'trigger': 'axis',
      'axisPointer': {'type': 'shadow'},
    },
    'legend': {'data': series_names, 'top': 36},
    'grid': {'left': '3%', 'right': '4%', 'top': 70, 'bottom': '3%', 'containLabel': True},
    'xAxis': {
      'type': 'value',
      'max': 100 if normalize else None,
    },
    'yAxis': {
      'type': 'category',
      'data': categorias,
      'axisLabel': {'width': 200, 'overflow': 'truncate'},
    },
    'series': series,
  }

  if colors:
    options['color'] = colors

  st_echarts(
    options=options,
    height=height,
    key=key,
  )

  return