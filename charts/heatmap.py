import streamlit as st
import altair as alt
import pandas as pd
import json

def plot_custom_heatmap(df, x, x_title, y, y_title, color, color_title, title, cell_size=80, show_grid=True, grid_color='white', color_scheme='blues', log_color=False, color_domain_min=None, color_domain_max=None, invalid_color=None, tooltip=None, tooltip_format=',.0f'):
  scale_kwargs = {'scheme': color_scheme}
  if log_color:
    scale_kwargs['type'] = 'log'

  # O Vega-Lite não aceita None no array do domain (nem min, nem max). Portanto:
  # - linear: domain = [min, max], default min = 0;
  # - log: nunca fixar domain com None; se só o max for informado, inferir o
  #   menor valor positivo dos dados para compor um domain [min>0, max].
  if color_domain_min is not None and color_domain_max is not None:
    scale_kwargs['domain'] = [color_domain_min, color_domain_max]
  elif color_domain_max is not None and not log_color:
    scale_kwargs['domain'] = [0, color_domain_max]
  elif color_domain_max is not None and log_color:
    positivos = pd.to_numeric(df[color], errors='coerce').dropna()
    positivos = positivos[positivos > 0]
    if not positivos.empty:
      scale_kwargs['domain'] = [float(positivos.min()), color_domain_max]

  if tooltip is None:
    tooltip = [x, y, color]

  # Para colunas numéricas, cria uma cópia calculada que troca null/NaN por 0
  # apenas no tooltip (a coluna original permanece para a cor/invalid_color).
  # Usa o nome da coluna via json.dumps para tratar nomes com espaços/acentos.
  tooltip_transforms = []
  tooltip_fields = []
  for campo in tooltip:
    if isinstance(campo, alt.Tooltip):
      tooltip_fields.append(campo)
    elif campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      campo_json = json.dumps(campo)
      novo_campo = f'__tip_{campo}'
      tooltip_transforms.append({
        'as': novo_campo,
        'calculate': f'isValid(datum[{campo_json}]) ? datum[{campo_json}] : 0',
      })
      tooltip_fields.append(alt.Tooltip(f'{novo_campo}:Q', title=campo, format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  chart_base = alt.Chart(df)
  if tooltip_transforms:
    chart_base = chart_base.transform_calculate(**{
      t['as']: t['calculate'] for t in tooltip_transforms
    })

  chart = (
    chart_base.mark_rect(
      stroke=grid_color if show_grid else None,
      strokeWidth=2 if show_grid else 0,
    ).encode(
      x=alt.X(f'{x}:O', title=x_title, scale=alt.Scale(paddingInner=0)),
      y=alt.Y(f'{y}:O', title=y_title, scale=alt.Scale(paddingInner=0)),
      color=alt.Color(f'{color}:Q', title=color_title, scale=alt.Scale(**scale_kwargs)),
      tooltip=tooltip_fields
    ).properties(
      width={'step': cell_size},
      height={'step': cell_size},
      title=alt.TitleParams(
        text=title,
        anchor='start'
      )
    )
  )

  if invalid_color is not None:
    chart = chart.configure_scale(invalid={'color': {'value': invalid_color}})

  st.altair_chart(chart)

  return
