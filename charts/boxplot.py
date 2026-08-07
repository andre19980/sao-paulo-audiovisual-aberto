import altair as alt
import streamlit as st

def plot_custom_boxplot_chart(df, x, x_title, y, y_title, title):
  chart = alt.Chart(df).mark_boxplot().encode(
    x=alt.X(f'{x}:O', title=x_title),
    y=alt.Y(f'{y}:Q', title=y_title),
  ).properties(
    title=alt.TitleParams(
      text=title,
      anchor='middle'
    )
  )
  
  st.altair_chart(chart)

  return