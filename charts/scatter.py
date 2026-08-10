import altair as alt
import streamlit as st

def plot_custom_labeled_scatter_chart(df, x, x_title, y, y_title, size, label, highlight, title, log_x=False):
  scale_range = ['#4c78a8', '#e45756']
  domain = [False, True]

  hover_selection = alt.selection_point(
    on='mouseover',
    nearest=False,
    fields=[x, y],
    empty=False,
    clear='mouseout',
  )

  base = (
    alt.Chart(df)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Undefined),
        y=alt.Y(f'{y}:Q', title=y_title),
      )
      .add_params(
        hover_selection
      )
      .properties(
        height=460,
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  points = base.mark_circle(opacity=0.7).encode(
    size=alt.Size(f'{size}:Q', title='Total de salas', scale=alt.Scale(range=[100, 3000])),
    color=alt.Color(f'{highlight}:N', legend=None, scale=alt.Scale(domain=domain, range=scale_range)),
    tooltip=[label, x, y, size]
  )

  labels = base.mark_text(
    align='left',
    dx=8,
    dy=4,
    fontSize=10,
  ).encode(
    text=f'{label}:N',
    color=alt.Color(f'{highlight}:N', legend=None, scale=alt.Scale(domain=domain, range=['#333', '#e45756'])),
    fillOpacity=alt.condition(hover_selection, alt.value(1), alt.value(0)),
  )

  st.altair_chart(points + labels)

  return