import streamlit as st
import altair as alt
import pandas as pd

def plot_custom_grouped_bar_chart(df, x, x_title, y, y_title, x_offset, x_offset_title, title, x_scale_sort=None):
  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title, sort=x_scale_sort),
      y=alt.Y(f'{y}:Q', title=y_title),
      xOffset=alt.XOffset(f'{x_offset}:N', title=x_offset_title),
      color=f'{x_offset}:N',
      tooltip=[y]
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

def plot_custom_stacked_bar_chart(df, x, x_title, y, y_title, color, color_title, title):
  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title),
      y=alt.Y(f'{y}:Q', title=y_title, stack='zero'),
      color=alt.Color(f'{color}:N', title=color_title),
      tooltip=[x, color, y]
    ).properties(
      title=alt.TitleParams(
        text=title,
        anchor='start'
      )
    )
  )

  st.altair_chart(chart)

  return