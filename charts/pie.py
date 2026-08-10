import streamlit as st
import altair as alt

def plot_custom_pie_chart(df, color, theta, title):
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

  pie = base.mark_arc(innerRadius=50, outerRadius=120)

  st.altair_chart(pie)

  return