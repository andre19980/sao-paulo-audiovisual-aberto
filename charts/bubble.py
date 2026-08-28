import streamlit as st
import altair as alt
import pandas as pd

def plot_custom_bubble_chart(df, x, x_title, y, y_title, size, size_title, color, color_title, title, log_x=False, color_type='N', color_scheme=None, tooltip_fields=None, height=420, size_range=[50, 3000], show_color_legend=True, tooltip_format=',.0f', x_zero=True, y_zero=True, opacity=0.6):
  color_kwargs = {'legend': alt.Legend(title=color_title) if show_color_legend else None}
  if color_type == 'Q':
    color_kwargs.update({
      'scale': alt.Scale(scheme=color_scheme or 'blues'),
    })
  else:
    color_kwargs['title'] = color_title
    # Para categorias, aceita uma lista de cores explícita (range) ou o nome de
    # uma paleta (scheme). Sem isso o Altair usa a paleta padrão, que tende ao azul.
    if isinstance(color_scheme, list):
      color_kwargs['scale'] = alt.Scale(range=color_scheme)
    elif isinstance(color_scheme, str):
      color_kwargs['scale'] = alt.Scale(scheme=color_scheme)

  if tooltip_fields is None:
    tooltip_fields = [x, y, size, color]

  # Aplica o formato às colunas numéricas do tooltip (texto e alt.Tooltip intactos).
  formatted_tooltip = []
  for campo in tooltip_fields:
    if isinstance(campo, alt.Tooltip):
      formatted_tooltip.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      formatted_tooltip.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      formatted_tooltip.append(campo)

  base = (
    alt.Chart(df)
      .mark_circle(opacity=opacity)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Scale(zero=x_zero)),
        y=alt.Y(f'{y}:Q', title=y_title, scale=alt.Scale(zero=y_zero)),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(range=size_range)),
        color=alt.Color(f'{color}:{color_type}', **color_kwargs),
        tooltip=formatted_tooltip
      )
      .properties(
        height=height,
        title=alt.TitleParams(
          text=title,
          anchor='start',
        )
      )
  )

  st.altair_chart(base)

  return