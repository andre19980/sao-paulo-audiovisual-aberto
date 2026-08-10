import streamlit as st
import altair as alt

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