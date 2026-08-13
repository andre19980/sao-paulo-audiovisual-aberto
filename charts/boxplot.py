import altair as alt
import streamlit as st

def plot_custom_boxplot_chart(df, x, x_title, y, y_title, title, size=30, outliers=True):
  """Boxplot do valor de 'y' agrupado pela categoria 'x'.

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset no formato "long": uma linha por observação, com a coluna 'x'
    (categoria) e a coluna 'y' (valor numérico). Passar dados já agregados
    (ex.: uma linha por município com totais) faz o boxplot colapsar em
    um único traço, pois não há distribuição.
  x : str
    Coluna categórica que define os grupos (eixo X).
  x_title : str
    Título do eixo X.
  y : str
    Coluna numérica com os valores de cada observação (eixo Y).
  y_title : str
    Título do eixo Y.
  title : str
    Título do gráfico.
  size : int
    Espessura (largura) de cada caixa.
  outliers : bool
    Exibir ou não os outliers (pontos acima do bigode).
  """
  chart = alt.Chart(df).mark_boxplot(size=size, outliers=outliers).encode(
    x=alt.X(f'{x}:O', title=x_title),
    y=alt.Y(f'{y}:Q', title=y_title, scale=alt.Scale(zero=True)),
  ).properties(
    title=alt.TitleParams(
      text=title,
      anchor='start'
    )
  )

  st.altair_chart(chart)

  return
