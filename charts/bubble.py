import streamlit as st
import altair as alt

def plot_custom_bubble_chart(df, x, x_title, y, y_title, size, size_title, color, color_title, title, log_x=False, color_type='N', color_scheme=None, tooltip_fields=None, height=420, size_range=[50, 3000]):
  color_kwargs = {'legend': alt.Legend(title=color_title)}
  if color_type == 'Q':
    color_kwargs.update({
      'scale': alt.Scale(scheme=color_scheme or 'blues'),
    })
  else:
    color_kwargs['title'] = color_title

  if tooltip_fields is None:
    tooltip_fields = [x, y, size, color]

  base = (
    alt.Chart(df)
      .mark_circle(opacity=0.6)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Undefined),
        y=alt.Y(f'{y}:Q', title=y_title),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(range=size_range)),
        color=alt.Color(f'{color}:{color_type}', **color_kwargs),
        tooltip=tooltip_fields
      )
      .properties(
        height=height,
        title=alt.TitleParams(
          text=title,
          anchor='start',
        )
      )
  )

  st.altair_chart(base)

  return