import altair as alt
import streamlit as st

def plot_custom_violin_chart(df, x, x_title, y, y_title, title):
  chart = alt.Chart(df).transform_density(
    y,
    as_=[y, 'density'],
    groupby=[x],
  ).mark_area(orient='horizontal').encode(
    alt.X('density:Q', title=x_title)
      .stack('center')
      .impute(None)
      .title(None)
      .axis(labels=False, values=[0], grid=False, ticks=True),
      alt.Y(f'{y}:Q', title=y_title),
      alt.Color(f'{x}:N'),
      alt.Column(f'{x}:N')
        .spacing(0)
        .header(titleOrient='bottom', labelOrient='bottom', labelPadding=0)
  ).configure_view(
    stroke=None
  ).properties(
    title=alt.TitleParams(
      text=title,
      anchor='start',
    )
  )
  
  st.altair_chart(chart)

  return