import streamlit as st
import altair as alt

def plot_custom_strip_jitter_chart(df, y, y_title, x, x_title, color, color_title, title, height=480):
  # Strip/jitter plot: cada complexo vira um ponto com ruído aleatório no eixo X
  # (dentro da categoria do porte), evitando que os pontos fiquem sobrepostos.
  # O eixo Y mostra a quantidade de salas, destacando os megaplex no topo.
  chart = (
    alt.Chart(df)
      .transform_calculate(
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
      )
      .mark_circle(opacity=0.75, stroke='black', strokeWidth=0.4)
      .encode(
        x=alt.X('jitter:Q', title=None, axis=None).stack('center'),
        y=alt.Y(f'{y}:Q', title=y_title),
        color=alt.Color(f'{color}:N', title=color_title, legend=alt.Legend(orient='top')),
        tooltip=['NOME_COMPLEXO', 'BAIRRO_COMPLEXO', f'{y}:Q'],
      )
      .properties(
        width=620,
        height=height,
        title=alt.TitleParams(text=title, anchor='middle'),
      )
  )

  # Camada com a média de salas (linha tracejada de referência).
  mean_layer = (
    alt.Chart(df)
      .mark_rule(
        color='#888',
        strokeDash=[6, 4],
        opacity=0.6,
      )
      .encode(
        y=alt.Y(f'mean({y}):Q'),
      )
  )

  st.altair_chart(chart + mean_layer)

  return