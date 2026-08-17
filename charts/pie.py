import streamlit as st
import altair as alt
import json

def plot_custom_pie_chart(df, color, theta, title, inner_radius=50, outer_radius=120, show_percentage=True):
  theta_json = json.dumps(theta)
  base = (
    alt.Chart(df)
      .transform_joinaggregate(
        total=f'sum({theta})',
      )
      .transform_calculate(
        percent=f'datum[{theta_json}] / datum.total * 100',
      )
      .encode(
        theta=alt.Theta(f'{theta}:Q'),
        color=alt.Color(f'{color}:N'),
        tooltip=[
          color,
          alt.Tooltip(f'{theta}:Q', format=',.0f'),
          alt.Tooltip('percent:Q', title='Percentual (%)', format='.1f'),
        ] if show_percentage else [color, theta],
      )
      .properties(
        title=alt.TitleParams(
          text=title,
          anchor='start',
        )
      )
  )

  pie = base.mark_arc(innerRadius=inner_radius, outerRadius=outer_radius)

  st.altair_chart(pie)

  return