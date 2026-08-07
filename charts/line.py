import streamlit as st
import altair as alt

def plot_custom_line_chart(df, x, x_title, y, y_title, title):
  base = (
    alt.Chart(df)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, axis=alt.Axis(labelAngle=0, format='d')),
        y=alt.Y(f'{y}:Q', title=y_title),
        tooltip=[x, y]
      )
      .properties(
        title=alt.TitleParams(
          text=title,
          anchor='middle',
        )
      )
  )

  hover_selection = alt.selection_point(
    on='mouseover',
    nearest=True,
    fields=[x],
    empty=False,
    clear='mouseout'
  )

  line_layer = base.mark_line()

  point_layer = base.mark_circle(size=80).encode(
    opacity=alt.condition(hover_selection, alt.value(1), alt.value(0))
  ).add_params(
    hover_selection 
  )

  final_chart = (line_layer + point_layer).configure_axisX(grid=False).configure_view(strokeOpacity=0)
  st.altair_chart(final_chart)
  
  return
