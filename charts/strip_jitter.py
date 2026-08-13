import streamlit as st
import altair as alt

def plot_custom_strip_jitter_chart(df, y, y_title, x, x_title, color, color_title, title, height=480, tooltip_fields=None):
  chart = (
    alt.Chart(df)
      .transform_calculate(
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
      )
      .mark_circle(opacity=0.75, stroke='black', strokeWidth=0.4)
      .encode(
        x=alt.X('jitter:Q', title=None, axis=None).stack('center'),
        y=alt.Y(f'{y}:Q', title=y_title),
        color=alt.Color(f'{color}:N', title=color_title, legend=alt.Legend(orient='top', symbolStrokeWidth=0.4)),
        tooltip=tooltip_fields,
      )
      .properties(
        width=620,
        height=height,
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  # Camada com a média de salas (linha tracejada de referência).
  mean_layer = (
    alt.Chart(df)
      .mark_rule(
        color='#888',
        strokeDash=[6, 4],
        opacity=0.6,
      )
      .encode(
        y=alt.Y(f'mean({y}):Q'),
      )
  )

  st.altair_chart(chart + mean_layer)

  return