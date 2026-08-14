import streamlit as st
import altair as alt

def plot_custom_pie_chart(df, color, theta, title, inner_radius=50, outer_radius=120):
  base = (
    alt.Chart(df)
      .encode(
        theta=alt.Theta(f'{theta}:Q'),
        color=alt.Color(f'{color}:N'),
        tooltip=[color, theta]
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