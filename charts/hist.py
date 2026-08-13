import streamlit as st
import altair as alt

def plot_custom_histogram_chart(df, x, x_title, y, y_title, faixas, title, color_scale_scheme='blues', height=420):
  """Histograma de barras por faixas categóricas pré-definidas.

  Parâmetros
  ----------
  df : pd.DataFrame
    Dataset com as colunas apontadas por 'x' e 'y'.
  x : str
    Nome da coluna com a categoria de cada faixa (eixo X).
  x_title : str
    Título do eixo X.
  y : str
    Nome da coluna com a contagem (eixo Y).
  y_title : str
    Título do eixo Y.
  faixas : list[str]
    Ordem das faixas a exibir no eixo X (cada elemento deve existir na coluna 'x').
  title : str
    Título do gráfico.
  color_scale_scheme : str
    Esquema de cor para as barras (default 'blues').
  height : int
    Altura do gráfico.
  """
  df_ord = df.copy()
  df_ord['__ORDEM__'] = df_ord[x].map({f: i for i, f in enumerate(faixas)})

  chart = (
    alt.Chart(df_ord)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        x=alt.X(f'{x}:N', title=x_title, sort=None, axis=alt.Axis(labelAngle=0, labelLimit=120)),
        y=alt.Y(f'{y}:Q', title=y_title),
        color=alt.Color(f'{x}:N', legend=None, scale=alt.Scale(scheme=color_scale_scheme)),
        tooltip=[x, y],
      )
      .properties(
        height=height,
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  st.altair_chart(chart)

  return
