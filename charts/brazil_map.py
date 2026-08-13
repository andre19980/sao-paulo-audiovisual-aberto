import streamlit as st
import altair as alt
import json
import pandas as pd

def plot_custom_choropleth_brazil_map(df, geojson_path, uf_col, value_col, value_title, title, color_scheme='inferno', color_domain=None, width=760, height=620, tooltip_extra=None):
  """Mapa coroplético do Brasil colorindo cada estado por um valor agregado.

  Faz o join do dataframe (uma linha por UF) com as features do GeoJSON pela
  sigla da UF e pinta cada estado conforme o valor indicado.

  Parâmetros
  ----------
  df : pd.DataFrame
    Deve conter uma coluna de UF (sigla, ex.: 'SP') e uma coluna numérica com
    o valor a colorir. Apenas uma linha por UF é esperada.
  geojson_path : str
    Caminho local para o arquivo GeoJSON dos estados (FeatureCollection).
  uf_col : str
    Nome da coluna com a sigla da UF (ex.: 'UF').
  value_col : str
    Nome da coluna numérica a colorir (ex.: 'TOTAL_PRODUTORAS').
  value_title : str
    Título da legenda de cor.
  title : str
    Título do gráfico.
  color_scheme : str
    Esquema de cor da escala (default 'inferno').
  color_domain : list | None
    Domínio fixo da escala de cor (default None = derivado dos dados).
  width / height : int
    Dimensões do mapa.
  tooltip_extra : dict[str, str] | None
    Colunas adicionais do dataframe para exibir no tooltip, mapeando
    "nome da coluna" -> "título" (default None).
  """
  with open(geojson_path, 'r', encoding='utf-8') as file:
    geojson_uf = json.load(file)

  df_join = df[[uf_col, value_col] + list((tooltip_extra or {}).keys())].set_index(uf_col)
  for feat in geojson_uf['features']:
    sigla = feat['properties']['sigla']
    if sigla in df_join.index:
      feat['properties'][value_col] = float(df_join.loc[sigla, value_col])
      for extra_col in (tooltip_extra or {}):
        feat['properties'][extra_col] = float(df_join.loc[sigla, extra_col])
    else:
      feat['properties'][value_col] = None
      for extra_col in (tooltip_extra or {}):
        feat['properties'][extra_col] = None

  scale_kwargs = {'scheme': color_scheme}
  if color_domain is not None:
    scale_kwargs['domain'] = color_domain

  tooltip_fields = [
    alt.Tooltip('properties.name:N', title='Estado'),
    alt.Tooltip(f'properties.{value_col}:Q', title=value_title, format=','),
  ]
  for extra_col, extra_title in (tooltip_extra or {}).items():
    tooltip_fields.append(alt.Tooltip(f'properties.{extra_col}:Q', title=extra_title, format=','))

  choropleth_layer = (
    alt.Chart(alt.Data(values=geojson_uf, format=alt.DataFormat(property='features')))
      .mark_geoshape(stroke='#b6bfc9', strokeWidth=0.7)
      .encode(
        color=alt.Color(
          f'properties.{value_col}:Q',
          title=value_title,
          scale=alt.Scale(**scale_kwargs),
        ),
        tooltip=tooltip_fields,
      )
  )

  # Camada fantasma (grid com subset separado) para impedir que o Altair eleve o
  # GeoJSON ao `data` de nível superior do spec. Se isso acontecer, o Streamlit
  # extrai `data.values`, descarta o `format` do GeoJSON e serializa o
  # FeatureCollection como Arrow — fazendo o mapa renderizar sem nenhum estado.
  dummy_grid = pd.DataFrame({'x': [0.0], 'y': [0.0]})
  grid_layer = (
    alt.Chart(dummy_grid)
      .mark_point(opacity=0, size=0)
      .encode(
        x=alt.X('x:Q', axis=None),
        y=alt.Y('y:Q', axis=None),
      )
  )

  choropleth_uf = (
    alt.layer(choropleth_layer, grid_layer)
      .project(type='equalEarth')
      .properties(
        width=width,
        height=height,
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  st.altair_chart(choropleth_uf)

  return

def plot_custom_brazil_map(df, geojson_path, label, size, size_title, color, color_title, title, lat_col='Latitude', lon_col='Longitude', color_scale_domain=None, size_scale_domain=None, tooltip_fields=None):
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

  if tooltip_fields is None:
    tooltip_fields = [label, color, size]

  points = (
    alt.Chart(df)
      .mark_circle(opacity=0.9, stroke='white', strokeWidth=1)
      .encode(
        longitude=alt.Longitude(f'{lon_col}:Q'),
        latitude=alt.Latitude(f'{lat_col}:Q'),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(**size_scale_kwargs)),
        color=alt.Color(f'{color}:Q', title=color_title, scale=alt.Scale(**color_scale_kwargs)),
        tooltip=tooltip_fields,
      )
  )

  map_chart = (
    alt.layer(base_map, points)
      # Projeção adequada para o território brasileiro.
      .project(type='equalEarth')
      .properties(
        width=760,
        height=620,
        title=alt.TitleParams(text=title, anchor='start'),
      )
  )

  st.altair_chart(map_chart)

  return