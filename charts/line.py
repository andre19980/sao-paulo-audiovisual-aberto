import streamlit as st
import altair as alt
import pandas as pd

def plot_custom_line_chart(df, x, x_title, y, y_title, title, tooltip_format=',.0f'):
  tooltip_fields = []
  for campo in [x, y]:
    if campo in df.columns and pd.api.types.is_numeric_dtype(df[campo]):
      tooltip_fields.append(alt.Tooltip(f'{campo}:Q', format=tooltip_format))
    else:
      tooltip_fields.append(campo)

  base = (
    alt.Chart(df)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, axis=alt.Axis(labelAngle=0, format='d')),
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
