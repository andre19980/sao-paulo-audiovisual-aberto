import streamlit as st
import altair as alt

def plot_custom_heatmap(df, x, x_title, y, y_title, color, color_title, title, cell_size=80, show_grid=True, grid_color='white'):
  chart = (
    alt.Chart(df).mark_rect(
      stroke=grid_color if show_grid else None,
      strokeWidth=2 if show_grid else 0,
    ).encode(
      x=alt.X(f'{x}:O', title=x_title, scale=alt.Scale(paddingInner=0)),
      y=alt.Y(f'{y}:O', title=y_title, scale=alt.Scale(paddingInner=0)),
      color=alt.Color(f'{color}:Q', title=color_title, scale=alt.Scale(scheme='blues')),
      tooltip=[x, y, color]
    ).properties(
      width={'step': cell_size},
      height={'step': cell_size},
      title=alt.TitleParams(
        text=title,
        anchor='start'
      )
    )
  )

  st.altair_chart(chart)

  return
