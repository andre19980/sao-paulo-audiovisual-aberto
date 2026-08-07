import streamlit as st
import altair as alt
import json

def plot_custom_brazil_map(df, geojson_path, label, size, size_title, color, color_title, title, lat_col='Latitude', lon_col='Longitude', color_scale_domain=None, size_scale_domain=None):
  """
  Mapa coroplético do Brasil com as capitais sobrepostas.

  - Camada de fundo: estados brasileiros (front: fronteiras), coloridos de forma neutra
    para dar contexto geográfico.
  - Camada de frente: "bolinhas" nas capitais, onde o tamanho representa uma métrica
    (ex.: número de complexos) e a intensidade da cor representa outra (ex.: média
    de salas por complexo).

  Parâmetros
  ----------
  df : pd.DataFrame
    Deve conter colunas 'Latitude' e 'Longitude' (posição das capitais), além das
    colunas apontadas por 'size', 'color' e 'label'.
  geojson_path : str
    Caminho local para o arquivo GeoJSON dos estados (FeatureCollection).
  label : str
    Coluna com o nome da capital (usada no tooltip).
  size / color : str
    Colunas numéricas usadas no tamanho e na cor das bolinhas.
  lat_col / lon_col : str
    Nomes das colunas de latitude/longitude do dataframe (defaults 'Latitude'/'Longitude').
  """
  # Carrega o GeoJSON dos estados como dados inline (embed no spec). Isso evita
  # que o Vega-fetch um URL relativo, que pode falhar dentro do Streamlit.
  with open(geojson_path, 'r', encoding='utf-8') as f:
    geo_data = json.load(f)

  geo_source = alt.Data(
    values=geo_data,
    format=alt.DataFormat(property='features'),
  )

  # Camada de fundo: contorno e preenchimento neutro dos estados.
  base_map = (
    alt.Chart(geo_source)
      .mark_geoshape(fill='#eef1f4', stroke='#b6bfc9', strokeWidth=0.7)
  )

  # Camada de frente: bolinhas nas capitais.
  # latitude/longitude fazem com que a camada respeite a mesma projeção do geoshape.
  # O domínio das escalas só é fixado quando informado (evita legenda colapsada).
  size_scale_kwargs = {'range': [60, 1600]}
  if size_scale_domain is not None:
    size_scale_kwargs['domain'] = size_scale_domain

  color_scale_kwargs = {'scheme': 'blues'}
  if color_scale_domain is not None:
    color_scale_kwargs['domain'] = color_scale_domain

  points = (
    alt.Chart(df)
      .mark_circle(opacity=0.9, stroke='white', strokeWidth=1)
      .encode(
        longitude=alt.Longitude(f'{lon_col}:Q'),
        latitude=alt.Latitude(f'{lat_col}:Q'),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(**size_scale_kwargs)),
        color=alt.Color(f'{color}:Q', title=color_title, scale=alt.Scale(**color_scale_kwargs)),
        tooltip=[label, color, size],
      )
  )

  map_chart = (
    alt.layer(base_map, points)
      # Projeção adequada para o território brasileiro.
      .project(type='equalEarth')
      .properties(
        width=760,
        height=620,
        title=alt.TitleParams(text=title, anchor='middle'),
      )
  )

  st.altair_chart(map_chart)

  return