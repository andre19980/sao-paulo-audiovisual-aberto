import streamlit as st
import altair as alt

def plot_custom_bubble_chart(df, x, x_title, y, y_title, size, size_title, color, color_title, title, log_x=False):
  base = (
    alt.Chart(df)
      .mark_circle(opacity=0.6)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Undefined),
        y=alt.Y(f'{y}:Q', title=y_title),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(range=[50, 3000])),
        color=alt.Color(f'{color}:N', title=color_title, legend=alt.Legend(title=color_title)),
        tooltip=[x, y, size, color]
      )
      .properties(
        height=420,
        title=alt.TitleParams(
          text=title,
          anchor='start',
        )
      )
  )

  st.altair_chart(base)

  return