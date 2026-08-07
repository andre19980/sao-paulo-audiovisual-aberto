import streamlit as st
import json
import unicodedata
import pandas as pd
import numpy as np
import altair as alt

st.title('Eixo 1 - Mapeamento da Oferta Cultural (Cinemas e Salas de Exibição)')

DATA_URLS = {
  'salas_de_exibicao_e_complexos': 'https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-e-complexos.csv',
  'salas_evolucao': 'https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-evolucao-anual.csv',
  'complexos_evolucao': 'https://dados.ancine.gov.br/dados-abertos/complexos-cinematograficos-evolucao-anual.csv'
}

@st.cache_data(scope='session')
def load_data(url):
  data = pd.read_csv(url, sep=';')

  return data

# Plot functions
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

def plot_custom_grouped_bar_chart(df, x, x_title, y, y_title, x_offset, x_offset_title, title, x_scale_sort=None):
  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title, sort=x_scale_sort),
      y=alt.Y(f'{y}:Q', title=y_title),
      xOffset=alt.XOffset(f'{x_offset}:N', title=x_offset_title),
      color=f'{x_offset}:N',
      tooltip=[y]
    ).properties(
      title=alt.TitleParams(
        text=title,
        anchor='middle'
      )
    )
  )

  st.altair_chart(chart)

  return

def plot_custom_boxplot_chart(df, x, x_title, y, y_title, title):
  chart = alt.Chart(df).mark_boxplot().encode(
    x=alt.X(f'{x}:O', title=x_title),
    y=alt.Y(f'{y}:Q', title=y_title),
  ).properties(
    title=alt.TitleParams(
      text=title,
      anchor='middle'
    )
  )
  
  st.altair_chart(chart)

  return

def plot_custom_pie_chart(df, color, theta, title):
  base = (
    alt.Chart(df)
      .encode(
        theta=alt.Theta(f'{theta}:Q'),
        color=alt.Color(f'{color}:N'),
        tooltip=[color, theta]
      )
      .properties(
        title=alt.TitleParams(
          text=title,
          anchor='middle',
        )
      )
  )

  pie = base.mark_arc(innerRadius=50, outerRadius=120)

  st.altair_chart(pie)

  return

def plot_custom_stacked_bar_chart(df, x, x_title, y, y_title, color, color_title, title):
  chart = (
    alt.Chart(df).mark_bar().encode(
      x=alt.X(f'{x}:O', title=x_title),
      y=alt.Y(f'{y}:Q', title=y_title, stack='zero'),
      color=alt.Color(f'{color}:N', title=color_title),
      tooltip=[x, color, y]
    ).properties(
      title=alt.TitleParams(
        text=title,
        anchor='middle'
      )
    )
  )

  st.altair_chart(chart)

  return

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
        anchor='middle'
      )
    )
  )

  st.altair_chart(chart)

  return

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
        title=alt.TitleParams(text=title, anchor='middle'),
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

def plot_custom_bubble_chart(df, x, x_title, y, y_title, size, size_title, color, color_title, title, log_x=False):
  base = (
    alt.Chart(df)
      .mark_circle(opacity=0.6)
      .encode(
        x=alt.X(f'{x}:Q', title=x_title, scale=alt.Scale(type='log') if log_x else alt.Undefined),
        y=alt.Y(f'{y}:Q', title=y_title),
        size=alt.Size(f'{size}:Q', title=size_title, scale=alt.Scale(range=[50, 3000])),
        color=alt.Color(f'{color}:N', title=color_title, legend=alt.Legend(title=color_title)),
        tooltip=[x, y, size, color]
      )
      .properties(
        height=420,
        title=alt.TitleParams(
          text=title,
          anchor='middle',
        )
      )
  )

  st.altair_chart(base)

  return

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
      anchor='middle',
    )
  )
  
  st.altair_chart(chart)

  return

# Set page settings
st.set_page_config(layout="wide")

# Load data
data_load_state = st.text('Loading data...')
df_salas_complexos = load_data(DATA_URLS['salas_de_exibicao_e_complexos'])
df_salas_evolucao = load_data(DATA_URLS['salas_evolucao'])
df_complexos_evolucao = load_data(DATA_URLS['complexos_evolucao'])
data_load_state.text('Loading data...done!')

# Display raw data
# st.text('Raw data')
st.write(df_salas_complexos)
st.write(df_salas_evolucao)
st.write(df_complexos_evolucao)

# Charts

# section 1
st.header('1. Evolução temporal de espaços de cinema')
df_salas_sp = df_salas_evolucao[df_salas_evolucao['MUNICIPIO'] == 'SÃO PAULO']
df_serie_salas_sp = df_salas_sp.value_counts('ANO').sort_index().reset_index().rename(columns={
  'ANO': 'Ano',
  'count': 'Qtde'
})

df_salas_status_ano = df_salas_sp.value_counts(['ANO', 'STATUS']).reset_index(name='QUANTIDADE')

with st.container():
  col1, col2 = st.columns([1, 1], gap='large')
  
  with col1:
    with st.container(border=True):
      plot_custom_line_chart(
        df=df_serie_salas_sp,
        x='Ano',
        x_title='Ano',
        y='Qtde',
      y_title='Quantidade de salas registradas',
      title='Quantidade de salas registradas por ano no município de São Paulo'
    )
  
  with col2:
    with st.container(border=True):
      plot_custom_grouped_bar_chart(
        df=df_salas_status_ano,
        x='ANO',
        x_title='Ano',
        y='QUANTIDADE',
        y_title='Quantidade de complexos',
        x_offset='STATUS',
        x_offset_title='Status',
        title='Distribuição de salas por status e ano no município de São Paulo'
      )

df_complexos_sp = df_complexos_evolucao[df_complexos_evolucao['MUNICIPIO'] == 'SÃO PAULO']
df_serie_complexos_sp = df_complexos_sp.value_counts('ANO').sort_index().reset_index().rename(columns={
  'ANO': 'Ano',
  'count': 'Qtde'
})
df_complexos_status_ano = df_complexos_sp.value_counts(['ANO', 'STATUS']).reset_index().rename(columns={ 'count': 'QUANTIDADE' })

with st.container(horizontal=True):
  col1, col2 = st.columns([1, 1], gap='large')
  
  with col1:
    with st.container(border=True): 
      plot_custom_line_chart(
        df=df_serie_complexos_sp,
        x='Ano',
        x_title='Ano',
        y='Qtde',
        y_title='Quantidade de complexos registradas',
        title='Quantidade de complexos registradas por ano no município de São Paulo'
      )

  with col2:
    with st.container(border=True):
      plot_custom_grouped_bar_chart(
        df=df_complexos_status_ano,
        x='ANO',
        x_title='Ano',
        y='QUANTIDADE',
        y_title='Quantidade de complexos',
        x_offset='STATUS',
        x_offset_title='Status',
        title='Distribuição de complexos por status e ano no município de São Paulo'
      )

# section 2
st.header('2. Densidade por complexos')
df_complexos_abertos_2026 = df_complexos_evolucao[
  (df_complexos_evolucao['ANO'] == 2026) &
  (df_complexos_evolucao['STATUS'] == 'ABERTO')
]

df_salas_complexos_aberto_2026 = df_salas_complexos[df_salas_complexos['REGISTRO_COMPLEXO'].isin(df_complexos_abertos_2026['REGISTRO_ANCINE'].unique())]
df_salas_municipio_complexo = df_salas_complexos_aberto_2026.groupby(['MUNICIPIO_COMPLEXO', 'REGISTRO_COMPLEXO', 'CEP_COMPLEXO']).size().reset_index(name='QUANTIDADE_DE_SALAS')
df_salas_municipio_complexo['MEDIA_DE_SALAS'] = df_salas_municipio_complexo['QUANTIDADE_DE_SALAS']
df_media_salas_por_complexo_cidade = df_salas_municipio_complexo.groupby('MUNICIPIO_COMPLEXO').agg(
  {
    'QUANTIDADE_DE_SALAS': 'sum',
    'MEDIA_DE_SALAS': 'mean',
    'REGISTRO_COMPLEXO': 'count',
  })[['QUANTIDADE_DE_SALAS', 'MEDIA_DE_SALAS', 'REGISTRO_COMPLEXO']].sort_values(
    by='MEDIA_DE_SALAS',
    ascending=False
  ).reset_index()

df_media_salas_por_complexo_cidade.rename(
  columns={
    'MUNICIPIO_COMPLEXO': 'Município',
    'MEDIA_DE_SALAS': 'Média de salas por complexo',
    'QUANTIDADE_DE_SALAS': 'Total de salas',
    'REGISTRO_COMPLEXO': 'Número de complexos'
  }, inplace=True)

df_media_salas_por_complexo_cidade['Posição'] = df_media_salas_por_complexo_cidade.index + 1
df_media_salas_por_complexo_cidade['Destaque'] = df_media_salas_por_complexo_cidade['Município'].eq('SÃO PAULO')

with st.container(border=True):
  plot_custom_bubble_chart(
    df=df_media_salas_por_complexo_cidade,
    x='Número de complexos',
    x_title='Número de complexos (escala log)',
    y='Média de salas por complexo',
    y_title='Média de salas por complexo',
    size='Total de salas',
    size_title='Total de salas',
    color='Destaque',
    color_title='São Paulo',
    title='Média de salas por complexo vs número de complexos por município',
    log_x=True,
  )
  
st.subheader('Comparação da média de salas por complexo entre as capitais brasileiras')
with st.container(horizontal=True, vertical_alignment='center', horizontal_alignment='center'):
  col1, col2 = st.columns([1, 1], gap='large')

  with col1:
    with st.container(border=True):
      capitais_brasileiras = [
        'RIO BRANCO', 'MACEIÓ', 'MACAPÁ', 'MANAUS', 'SALVADOR', 'FORTALEZA',
        'BRASÍLIA', 'VITÓRIA', 'GOIÂNIA', 'SÃO LUÍS', 'CUIABÁ', 'CAMPO GRANDE',
        'BELO HORIZONTE', 'BELÉM', 'JOÃO PESSOA', 'CURITIBA', 'RECIFE',
        'TERESINA', 'RIO DE JANEIRO', 'NATAL', 'PORTO ALEGRE', 'PORTO VELHO',
        'BOA VISTA', 'FLORIANÓPOLIS', 'SÃO PAULO', 'ARACAJU', 'PALMAS'
      ]

      df_capitais = df_media_salas_por_complexo_cidade[df_media_salas_por_complexo_cidade['Município'].isin(capitais_brasileiras)].copy()
      df_capitais['É a capital'] = df_capitais['Município'].eq('SÃO PAULO')
      df_capitais = df_capitais.sort_values('Média de salas por complexo')

      # ---------------------------------------------------------------------------
      # Mapa do Brasil: coroplete dos estados ao fundo + bolinhas nas capitais.
      # Tamanho da bolinha  -> Número de complexos
      # Cor da bolinha      -> Média de salas por complexo
      # ---------------------------------------------------------------------------

      # Coordenadas (latitude, longitude) aproximadas de cada capital brasileira.
      coordenadas_capitais = {
        'RIO BRANCO': (-9.974, -67.806),
        'MACEIÓ': (-9.666, -35.735),
        'MACAPÁ': (0.035, -51.071),
        'MANAUS': (-3.116, -60.028),
        'SALVADOR': (-12.966, -38.501),
        'FORTALEZA': (-3.717, -38.543),
        'BRASÍLIA': (-15.794, -47.883),
        'VITÓRIA': (-20.315, -40.313),
        'GOIÂNIA': (-16.682, -49.251),
        'SÃO LUÍS': (-2.539, -44.286),
        'CUIABÁ': (-15.601, -56.098),
        'CAMPO GRANDE': (-20.470, -54.620),
        'BELO HORIZONTE': (-19.917, -43.935),
        'BELÉM': (-1.456, -48.504),
        'JOÃO PESSOA': (-7.115, -34.878),
        'CURITIBA': (-25.428, -49.273),
        'RECIFE': (-8.048, -34.877),
        'TERESINA': (-5.089, -42.802),
        'RIO DE JANEIRO': (-22.907, -43.173),
        'NATAL': (-5.794, -35.195),
        'PORTO ALEGRE': (-30.033, -51.230),
        'PORTO VELHO': (-8.761, -63.873),
        'BOA VISTA': (2.820, -60.673),
        'FLORIANÓPOLIS': (-27.596, -48.548),
        'SÃO PAULO': (-23.556, -46.640),
        'ARACAJU': (-10.947, -37.073),
        'PALMAS': (-10.212, -48.361),
      }

      # Mapeamento capital -> UF (sigla usada pelo GeoJSON para o coroplete).
      uf_das_capitais = {
        'RIO BRANCO': 'AC', 'MACEIÓ': 'AL', 'MACAPÁ': 'AP', 'MANAUS': 'AM',
        'SALVADOR': 'BA', 'FORTALEZA': 'CE', 'BRASÍLIA': 'DF', 'VITÓRIA': 'ES',
        'GOIÂNIA': 'GO', 'SÃO LUÍS': 'MA', 'CUIABÁ': 'MT', 'CAMPO GRANDE': 'MS',
        'BELO HORIZONTE': 'MG', 'BELÉM': 'PA', 'JOÃO PESSOA': 'PB', 'CURITIBA': 'PR',
        'RECIFE': 'PE', 'TERESINA': 'PI', 'RIO DE JANEIRO': 'RJ', 'NATAL': 'RN',
        'PORTO ALEGRE': 'RS', 'PORTO VELHO': 'RO', 'BOA VISTA': 'RR',
        'FLORIANÓPOLIS': 'SC', 'SÃO PAULO': 'SP', 'ARACAJU': 'SE', 'PALMAS': 'TO',
      }

      # Anexa latitude, longitude e UF à tabela das capitais.
      df_capitais['Latitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][0])
      df_capitais['Longitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][1])
      df_capitais['UF'] = df_capitais['Município'].map(uf_das_capitais)

      plot_custom_brazil_map(
        df=df_capitais,
        geojson_path='assets/brazil-states.geojson',
        label='Município',
        size='Número de complexos',
        size_title='Número de complexos',
        color='Média de salas por complexo',
        color_title='Média de salas por complexo',
        title='Capitais brasileiras no mapa: tamanho = nº de complexos, cor = média de salas por complexo (2026)',
      )
    
    with col2:
      st.dataframe(
        df_capitais[['Município', 'Média de salas por complexo', 'Número de complexos', 'Total de salas']],
        hide_index=True,
        width='stretch',
        height='stretch',
      )


st.space(size='medium')
# plot_custom_labeled_scatter_chart(
#   df=df_capitais,
#   x='Número de complexos',
#   x_title='Número de complexos (escala log)',
#   y='Média de salas por complexo',
#   y_title='Média de salas por complexo',
#   size='Total de salas',
#   label='Município',
#   highlight='É a capital',
#   title='Capitais brasileiras: média de salas por complexo vs número de complexos (2026)',
# )

df_salas_por_complexo_sp = df_salas_municipio_complexo[df_salas_municipio_complexo['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
df_salas_por_complexo_sp.sort_values(by='QUANTIDADE_DE_SALAS', ascending=False, inplace=True)

# ---------------------------------------------------------------------------
# Mapa de São Paulo: distribuição da quantidade de salas por complexo.
#
# Abordagem: os dados da ANCINE não trazem coordenadas, apenas endereço/CEP.
# Para priorizar performance (e como não é necessária grande precisão),
# usamos a aproximação pelo CEP: cada complexo recebe as coordenadas do
# centróide do seu CEP, carregadas de um asset local (assets/cep_sp_coordenadas.csv).
# ---------------------------------------------------------------------------

# Lê o asset CEP -> (latitude, longitude) gerado previamente.
df_cep_sp = pd.read_csv('assets/cep_sp_coordenadas.csv', dtype={'cep': str})

# Tabela de complexos de SP com quantidade de salas.
df_complexos_sp_mapa = (
  df_salas_por_complexo_sp
    .reset_index()
    .merge(
      df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
        [['REGISTRO_COMPLEXO', 'NOME_COMPLEXO', 'BAIRRO_COMPLEXO']]
        .drop_duplicates(subset='REGISTRO_COMPLEXO'),
      on='REGISTRO_COMPLEXO',
      how='left',
    )
)

# Normaliza o CEP (remove hífen) e faz o join com as coordenadas.
df_complexos_sp_mapa['CEP'] = df_complexos_sp_mapa['CEP_COMPLEXO'].astype(str).str.replace('-', '', regex=False)
df_complexos_sp_mapa = df_complexos_sp_mapa.merge(df_cep_sp, left_on='CEP', right_on='cep', how='left')

# Fallback: complexos cujo CEP não está na base recebem o centro aproximado
# do município de São Paulo, em vez de ficarem fora do mapa.
n_fallback = df_complexos_sp_mapa['latitude'].isna().sum()
df_complexos_sp_mapa['latitude'] = df_complexos_sp_mapa['latitude'].fillna(-23.5505)
df_complexos_sp_mapa['longitude'] = df_complexos_sp_mapa['longitude'].fillna(-46.6333)
if n_fallback:
  st.caption(f'{n_fallback} complexo(s) sem CEP na base receberam a localização aproximada do centro de São Paulo.')

# plot_custom_brazil_map(
#   df=df_complexos_sp_mapa,
#   geojson_path='assets/sp-municipio.geojson',
#   label='NOME_COMPLEXO',
#   size='QUANTIDADE_DE_SALAS',
#   size_title='Quantidade de salas',
#   color='QUANTIDADE_DE_SALAS',
#   color_title='Quantidade de salas',
#   title='Distribuição da quantidade de salas por complexo no município de São Paulo (2026)',
#   lat_col='latitude',
#   lon_col='longitude',
# )

# ---------------------------------------------------------------------------
# Strip/jitter plot: porte dos complexos de São Paulo.
# Cada complexo é um ponto no eixo Y (quantidade de salas). Como os complexos
# estão concentrados no centro, o mapa sobrepõe as bolinhas; aqui adicionamos
# ruído (jitter) no eixo X para separá-los e destacar megaplex (10+) vs
# complexos pequenos (2-3 salas). A linha tracejada marca a média.
# ---------------------------------------------------------------------------

# Categoriza o porte do complexo pela quantidade de salas.
porte_faixas = [1, 2, 3, 10, 100]  # limites: 1, [2-3], [4-9], [10+]
porte_rotulos = ['1 sala', 'Pequeno (2-3)', 'Médio (4-9)', 'Megaplex (10+)']
df_complexos_sp_mapa['Porte'] = pd.cut(
  df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'],
  bins=porte_faixas,
  labels=porte_rotulos,
  include_lowest=True,
)

with st.container(horizontal=True):
  col1, col2 = st.columns([1, 1], gap='large')
  
  with col2:
    with st.container(border=True):
      portes_selecionados = st.segmented_control(
        "Porte do complexo",
        options=porte_rotulos,
        selection_mode="multi"
      )
      
      if portes_selecionados:
        df_complexos_sp_filtrado = df_complexos_sp_mapa[df_complexos_sp_mapa['Porte'].isin(portes_selecionados)]
      else:
        df_complexos_sp_filtrado = df_complexos_sp_mapa

      plot_custom_brazil_map(
        df=df_complexos_sp_filtrado,
        geojson_path='assets/sp-municipio.geojson',
        label='NOME_COMPLEXO',
        size='QUANTIDADE_DE_SALAS',
        size_title='Quantidade de salas',
        color='QUANTIDADE_DE_SALAS',
        color_title='Quantidade de salas',
        title='Distribuição da quantidade de salas por complexo no município de São Paulo (2026)',
        lat_col='latitude',
        lon_col='longitude',
        # Domínio fixo baseado no máximo de salas (sem filtro) para que a legenda
        # não colapse quando o filtro deixa só um valor de salas.
        color_scale_domain=[0, df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'].max()],
        size_scale_domain=[0, df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'].max()],
      )

  with col1:
    st.dataframe(
      df_complexos_sp_filtrado[[
        'NOME_COMPLEXO',
        'BAIRRO_COMPLEXO',
        'QUANTIDADE_DE_SALAS',
      ]].rename(columns={
        'NOME_COMPLEXO': 'Nome do complexo',
        'BAIRRO_COMPLEXO': 'Bairro',
        'QUANTIDADE_DE_SALAS': 'Quantidade de Salas',
      }),
      hide_index=True,
      width='stretch',
      height='stretch',
    )

st.space(size='medium')
with st.container(horizontal=True):
  col1, col2 = st.columns([1, 1], gap='large')
  
  with col1:
    with st.container(border=True):
      plot_custom_strip_jitter_chart(
        df=df_complexos_sp_mapa,
        y='QUANTIDADE_DE_SALAS',
        y_title='Quantidade de salas',
        x=None,
        x_title=None,
        color='Porte',
        color_title='Porte do complexo',
        title='Distribuição dos complexos de São Paulo por porte e quantidade de salas (2026)',
      )
      st.caption('Pontos com mesmo número de salas foram levemente espalhados no eixo X (jitter) apenas para evitar sobreposição. Passe o mouse para ver o nome, bairro e nº de salas de cada complexo.')
      
  with col2:
    df_contagem_porte = (
      df_complexos_sp_mapa['Porte']
        .value_counts()
        .reindex(porte_rotulos, fill_value=0)
        .reset_index()
        .rename(columns={'index': 'Porte', 'count': 'Quantidade de complexos'})
    )

    bar_chart_portes = (
      alt.Chart(df_contagem_porte)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
          x=alt.X('Porte:N', title='Porte do complexo', sort=None),
          y=alt.Y('Quantidade de complexos:Q', title='Quantidade de complexos'),
          color=alt.Color('Porte:N', title='Porte do complexo'),
          tooltip=['Porte', 'Quantidade de complexos'],
        )
        .properties(
          height=480,
          title=alt.TitleParams(
            text='Quantidade de complexos por porte em São Paulo (2026)',
            anchor='middle',
          ),
        )
    )
    
    with st.container(border=True, height='stretch'):
      st.altair_chart(bar_chart_portes)

# section 3
st.header('3. Operação e situação do exibidor na cidade de São Paulo')

st.subheader('Informações sobre grupos exibidores no município')

df_salas_complexos_sp = df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
df_exibidores_sp = df_salas_complexos['REGISTRO_EXIBIDOR'].unique()
st.write(df_salas_complexos.groupby(['REGISTRO_EXIBIDOR', 'SITUACAO_EXIBIDOR']).size().reset_index(name='SIZE')['REGISTRO_EXIBIDOR'].is_unique)
df_exibidores_situacao = df_salas_complexos.groupby(['REGISTRO_EXIBIDOR', 'SITUACAO_EXIBIDOR']).size().reset_index()
df_exibidores_regulares_sp = df_exibidores_situacao[df_exibidores_situacao['SITUACAO_EXIBIDOR'] == 'REGULAR']
df_exibidores_irregulares_sp = df_exibidores_situacao[df_exibidores_situacao['SITUACAO_EXIBIDOR'] == 'IRREGULAR']
df_salas_complexos_sp_funcionamento_irregular = df_salas_complexos_sp[(df_salas_complexos_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO') & (df_salas_complexos_sp['SITUACAO_EXIBIDOR'] == 'IRREGULAR')]

with st.container(horizontal=True):
  col1, col2 = st.columns([1, 1], gap='large')

  with col1:
    a, b = st.columns(2)
    c, d = st.columns(2)
    a.metric("Número de grupos exibidores", len(df_exibidores_sp), border=True)
    b.metric("Número de exibidores em situação regular", len(df_exibidores_regulares_sp), border=True)

    c.metric("Número de exibidores em situação irregular", len(df_exibidores_irregulares_sp), border=True)
    d.metric("Sala em funcionamento com exibidor em situação irregular", len(df_salas_complexos_sp_funcionamento_irregular), border=True)
  
  with col2:
    st.dataframe(
      df_salas_complexos_sp_funcionamento_irregular[[
        'NOME_SALA',
        'SITUACAO_SALA',
        'OPERACAO_USUAL',
        'NOME_COMPLEXO',
        'NOME_GRUPO_EXIBIDOR',
        'SITUACAO_EXIBIDOR'
      ]].rename(columns={
        'NOME_SALA': 'Sala',
        'SITUACAO_SALA': 'Situação da sala',
        'OPERACAO_USUAL': 'Operação',
        'NOME_COMPLEXO': 'Complexo',
        'NOME_GRUPO_EXIBIDOR': 'Grupo exibidor',
        'SITUACAO_EXIBIDOR': 'Situação do exibidor'
      }),
      hide_index=True
    )
    st.caption('Lista de salas em funcionamento com exibidores em situação irregular', text_alignment='center', width='stretch')

st.subheader('Mapeamento de grupos exibidores por tipo de operação')
df_exibidores_mapa = df_salas_complexos_sp[df_salas_complexos_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'][['NOME_GRUPO_EXIBIDOR', 'OPERACAO_USUAL']].value_counts().reset_index(name='NÚMERO DE SALAS').rename(columns={ 'NOME_GRUPO_EXIBIDOR': 'GRUPO EXIBIDOR', 'OPERACAO_USUAL': 'OPERAÇÃO USUAL'})

st.table(df_exibidores_mapa, hide_index=True)

# Categorização dos grupos exibidores (privado, público, independente, sem grupo)
grupos_exibidores_sp = {
  'CINEMARK': 'Privado',
  'UCI': 'Privado',
  'CINÉPOLIS': 'Privado',
  'CINESYSTEM': 'Privado',
  'KINOPLEX': 'Privado',
  'MOVIECOM': 'Privado',
  'ARAÚJO': 'Privado',
  'CINE A': 'Privado',
  'CINEFLIX': 'Privado',
  'CINE MARQUISE': 'Privado',
  'PLAYARTE': 'Privado',
  'GRUPO CINE': 'Privado',
  'SPCINE': 'Público',
  'ESPAÇO': 'Independente',
  'RESERVA': 'Independente',
  'NÃO PERTENCE A NENHUM GRUPO EXIBIDOR': 'Sem grupo',
}

df_grupos_exibidores = pd.DataFrame(
  [(grupo, categoria) for grupo, categoria in grupos_exibidores_sp.items()],
  columns=['GRUPO EXIBIDOR', 'CATEGORIA']
) 

df_salas_por_categoria = (
  df_exibidores_mapa
    .merge(df_grupos_exibidores, on='GRUPO EXIBIDOR', how='left')
    .fillna({'CATEGORIA': 'Outros'})
)
df_exibidores_operacao_categoria = df_salas_por_categoria
df_salas_por_categoria = df_salas_por_categoria.groupby('CATEGORIA', as_index=False)['NÚMERO DE SALAS'].sum().sort_values(by='NÚMERO DE SALAS', ascending=False)

st.subheader('Distribuição de salas em funcionamento por categoria de grupo exibidor')

with st.container(horizontal=True):
  col1, col2 = st.columns([1, 1], gap='large')
  
  df_salas_por_categoria_operacao = (
  df_exibidores_operacao_categoria
      .groupby(['CATEGORIA', 'OPERAÇÃO USUAL'], as_index=False)['NÚMERO DE SALAS']
      .sum()
      .sort_values(by='NÚMERO DE SALAS', ascending=False)
  )

  df_pivot_operacao = df_salas_por_categoria_operacao.pivot(
    index='CATEGORIA',
    columns='OPERAÇÃO USUAL',
    values='NÚMERO DE SALAS'
  ).fillna(0).reset_index()
  
  with col1:
    with st.container(border=True): 
      st.markdown('''
        - **:blue[Privado]**: rede/empresa privada de capital nacional ou estrangeiro, com fins lucrativos, focada em exibição comercial em larga escala.                                                  
        - **:red[Público]**: estatal, vinculado a governo (municipal, estadual ou federal).                                                                                                               
        - **:green[Independente]**: exibidor menor, focado em cinema autoral/arte, salas únicas ou operação local/cultural, sem ser uma grande rede comercial.       
      ''')
      st.table(df_grupos_exibidores, hide_index=True, border='horizontal')
      
  with col2:
    plot_custom_pie_chart(
      df=df_salas_por_categoria,
      color='CATEGORIA',
      theta='NÚMERO DE SALAS',
      title=''
    )

    plot_custom_heatmap(
      df=df_salas_por_categoria_operacao,
      x='CATEGORIA',
      x_title='Categoria',
      y='OPERAÇÃO USUAL',
      y_title='Operação usual',
      color='NÚMERO DE SALAS',
      color_title='Quantidade de salas',
      title='Concentração de salas por categoria e operação usual'
    )
    
# section 4
st.header('4. Acessibilidade física')

acessibilidade_criterios = [
  'ASSENTOS_SALA',
  'ASSENTOS_CADEIRANTES',
  'ASSENTOS_MOBILIDADE_REDUZIDA',
  'ASSENTOS_OBESIDADE',
  'ACESSO_ASSENTOS_COM_RAMPA',
  'ACESSO_SALA_COM_RAMPA',
  'BANHEIROS_ACESSIVEIS'
]

df_salas_acessibilidade_sp = df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO'][['NOME_SALA', 'REGISTRO_SALA', 'SITUACAO_SALA', 'REGISTRO_COMPLEXO', 'NOME_COMPLEXO', 'BAIRRO_COMPLEXO', *acessibilidade_criterios]]
df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'] = df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'].str.lower()

piores_idh = [
  'jaraguá',
  'sapopemba',
  'capão redondo',
  'vila jacuí',
  'pedreira',
  'anhanguera',
  'perus',
  'brasilândia',
  'guaianases',
  'são rafael',
  'cidade tiradentes',
  'vila curuçá',
  'itaim paulista',
  'grajaú',
  'jardim helena',
  'iguatemi',
  'jardim ângela',
  'lajeado',
  'parelheiros',
  'marsilac',
]

melhores_idh = [
  'campo grande',
  'santana',
  'butantã',
  'santa cecília',
  'campo belo',
  'liberdade',
  'tatuapé',
  'morumbi',
  'bela vista',
  'lapa',
  'saúde',
  'santo amaro',
  'consolação',
  'vila mariana',
  'itaim bibi',
  'alto de pinheiros',
  'jardim paulista',
  'perdizes',
  'pinheiros',
  'moema',
]

# df_salas_acessibilidade_sp[df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'].isin(piores_idh)]
# df_salas_acessibilidade_sp[df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'].isin(melhores_idh)]

# df_salas_acessibilidade = df_salas_complexos[df_salas_complexos['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'][['NOME_SALA', 'REGISTRO_SALA', 'SITUACAO_SALA', 'NOME_COMPLEXO', 'BAIRRO_COMPLEXO', 'MUNICIPIO_COMPLEXO', *acessibilidade_criterios]]
# df_salas_acessibilidade['BAIRRO_COMPLEXO'] = df_salas_acessibilidade['BAIRRO_COMPLEXO'].str.lower()
# df_salas_acessibilidade['MUNICIPIO_COMPLEXO'] = df_salas_acessibilidade['MUNICIPIO_COMPLEXO'].str.title()

# df_salas_acessibilidade_assentos = df_salas_acessibilidade.groupby('MUNICIPIO_COMPLEXO').agg('sum')[['ASSENTOS_SALA', 'ASSENTOS_CADEIRANTES', 'ASSENTOS_MOBILIDADE_REDUZIDA', 'ASSENTOS_OBESIDADE']].sort_values(by='ASSENTOS_SALA', ascending=False)
# df_salas_acessibilidade_assentos['Assentos com acessibilidade'] = (df_salas_acessibilidade_assentos['ASSENTOS_CADEIRANTES'] + df_salas_acessibilidade_assentos['ASSENTOS_MOBILIDADE_REDUZIDA'] + df_salas_acessibilidade_assentos['ASSENTOS_OBESIDADE']).astype(int)
# df_salas_acessibilidade_assentos['Relação de assentos com acessibilidade'] = (df_salas_acessibilidade_assentos['Assentos com acessibilidade'] / df_salas_acessibilidade_assentos['ASSENTOS_SALA']) * 100
# df_salas_acessibilidade_assentos.sort_values(by='Relação de assentos com acessibilidade', ascending=False, inplace=True)
# df_salas_acessibilidade_assentos['Relação de assentos com acessibilidade'] = df_salas_acessibilidade_assentos['Relação de assentos com acessibilidade'].round(2).astype(str) + '%'
# df_salas_acessibilidade_assentos.rename(columns={ 'ASSENTOS_SALA': 'Total de assentos' }, inplace=True)
# df_salas_acessibilidade_assentos.reset_index(names='Município', inplace=True)
# df_salas_acessibilidade_assentos['Posição'] = df_salas_acessibilidade_assentos.index + 1
# df_salas_acessibilidade_assentos['Total de assentos'] = df_salas_acessibilidade_assentos['Total de assentos'].astype(int)

# acessibilidade_cols = ['Posição', 'Município', 'Total de assentos', 'Assentos com acessibilidade', 'Relação de assentos com acessibilidade']

# st.text('Top 10 municípios com maior proporção de assentos com acessibilidade')
# st.table(df_salas_acessibilidade_assentos[acessibilidade_cols].head(10))

# st.text('Ranking das cidades com maior proporção de assentos com acessibilidade e total de assentos maior que 1000')
# df_salas_acessibilidade_assentos_1000 = df_salas_acessibilidade_assentos[df_salas_acessibilidade_assentos['Total de assentos'] > 1000]
# st.table(df_salas_acessibilidade_assentos_1000[acessibilidade_cols].head(10), hide_index=True)

# df_salas_acessibilidade_assentos_sp = df_salas_acessibilidade_assentos[df_salas_acessibilidade_assentos['Município'] == 'São Paulo']
# st.text(f'São Paulo está na {df_salas_acessibilidade_assentos_sp['Posição'].values[0]}ª posição, com {df_salas_acessibilidade_assentos_sp['Relação de assentos com acessibilidade'].values[0]} de assentos com acessibilidade')
# st.table(df_salas_acessibilidade_assentos_sp[acessibilidade_cols])


# st.text('Há apenas uma sala em São Paulo que possui todos os requisitos de acessibilidade')
# df_salas_acessibilidade_sp.info()

# ---------------------------------------------------------------------------
# (1a) Porte da sala x Acessibilidade (São Paulo, em funcionamento)
# ---------------------------------------------------------------------------
st.subheader('Acessibilidade × Porte da sala')

df_acc_sp_func = df_salas_acessibilidade_sp[df_salas_acessibilidade_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'].copy()

porte_faixas_assentos = [0, 50, 100, 200, 400, 1000]
porte_rotulos_assentos = ['Até 50', '50-100', '100-200', '200-400', 'Acima de 400']
df_acc_sp_func['Faixa de assentos'] = pd.cut(
  df_acc_sp_func['ASSENTOS_SALA'],
  bins=porte_faixas_assentos,
  labels=porte_rotulos_assentos,
  include_lowest=True,
)

# Critérios avaliados como "sala com o recurso". Os três primeiros usam >0 assentos;
# os demais são presença (SIM/NÃO).
df_acc_sp_func['Cadeirantes'] = df_acc_sp_func['ASSENTOS_CADEIRANTES'].fillna(0) > 0
df_acc_sp_func['Mobilidade reduzida'] = df_acc_sp_func['ASSENTOS_MOBILIDADE_REDUZIDA'].fillna(0) > 0
df_acc_sp_func['Obesidade'] = df_acc_sp_func['ASSENTOS_OBESIDADE'].fillna(0) > 0
df_acc_sp_func['Rampa nos assentos'] = df_acc_sp_func['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM'
df_acc_sp_func['Rampa de acesso à sala'] = df_acc_sp_func['ACESSO_SALA_COM_RAMPA'] == 'SIM'
df_acc_sp_func['Banheiros acessíveis'] = df_acc_sp_func['BANHEIROS_ACESSIVEIS'] == 'SIM'

criterios_porte = ['Cadeirantes', 'Mobilidade reduzida', 'Obesidade', 'Rampa nos assentos', 'Rampa de acesso à sala', 'Banheiros acessíveis']

# Porcentagem de salas de cada faixa que possui o recurso, em formato longo p/ Altair.
df_porte_acc = (
  df_acc_sp_func.groupby(['Faixa de assentos'], observed=True)[criterios_porte]
    .mean()
    .mul(100)
    .reset_index()
)

df_porte_acc_melt = df_porte_acc.melt(id_vars='Faixa de assentos', var_name='Atributo de acessibilidade', value_name='% das salas')

plot_custom_grouped_bar_chart(
  df=df_porte_acc_melt.dropna(),
  x='Faixa de assentos',
  x_title='Quantidade de assentos na sala',
  y='% das salas',
  y_title='% das salas com o recurso',
  x_offset='Atributo de acessibilidade',
  x_offset_title='Atributo de acessibilidade',
  title='Proporção de salas com acessibilidade por porte da sala (São Paulo, 2026)',
  x_scale_sort=porte_rotulos_assentos,
)
st.caption('Salas pequenas (até 100 lugares) têm proporção muito menor de assentos para mobilidade reduzida e obesidade do que salas médias/grandes. Assentos para cadeirantes são praticamente universais em todos os portes. Rampa de acesso à sala é o critério mais raro, independentemente do porte.')

# ---------------------------------------------------------------------------
# (1b) Categoria de exibidor x Acessibilidade (São Paulo, em funcionamento)
# ---------------------------------------------------------------------------
st.subheader('Acessibilidade × Categoria do exibidor')

df_acc_sp_cat = df_acc_sp_func.merge(
  df_salas_complexos[['REGISTRO_SALA', 'NOME_GRUPO_EXIBIDOR']],
  on='REGISTRO_SALA',
  how='left',
)
df_acc_sp_cat['Categoria do exibidor'] = (
  df_acc_sp_cat['NOME_GRUPO_EXIBIDOR']
    .map(grupos_exibidores_sp)
    .fillna('Outros')
)

ordem_categorias = ['Privado', 'Público', 'Independente', 'Sem grupo', 'Outros']
df_cat_acc = (
  df_acc_sp_cat.groupby(['Categoria do exibidor'], observed=True)[criterios_porte]
    .mean()
    .mul(100)
    .reset_index()
)
df_cat_acc_melt = df_cat_acc.melt(
  id_vars='Categoria do exibidor',
  var_name='Atributo de acessibilidade',
  value_name='% das salas',
)

plot_custom_grouped_bar_chart(
  df=df_cat_acc_melt.dropna(),
  x='Categoria do exibidor',
  x_title='Categoria do exibidor',
  y='% das salas',
  y_title='% das salas com o recurso',
  x_offset='Atributo de acessibilidade',
  x_offset_title='Atributo de acessibilidade',
  title='Proporção de salas com acessibilidade por categoria de exibidor (São Paulo, 2026)',
  x_scale_sort=ordem_categorias,
)
st.caption('Salas de exibidores sem grupo têm os menores percentuais de banheiros acessíveis, assentos para cadeirantes e rampas. Exibidores públicos se destacam pela rampa de acesso à sala, mas têm banheiros acessíveis em menor proporção que os privados.')

# ---------------------------------------------------------------------------
# (3a) Proporção real de assentos acessíveis por categoria (quantitativo)
# ---------------------------------------------------------------------------
st.subheader('Proporção real de assentos acessíveis por categoria de exibidor')

# Diferente do item 1b (presença SIM/NÃO), aqui usa-se as contagens efetivas:
# quantos dos assentos totais da categoria são destinados a PcD (cadeirantes,
# mobilidade reduzida e obesidade).
df_accel_cat = df_acc_sp_cat.groupby('Categoria do exibidor', observed=True).apply(
  lambda g: pd.Series({
    'Assentos acessíveis': (
      g['ASSENTOS_CADEIRANTES'].fillna(0) + g['ASSENTOS_MOBILIDADE_REDUZIDA'].fillna(0) + g['ASSENTOS_OBESIDADE'].fillna(0)
    ).sum(),
    'Total de assentos': g['ASSENTOS_SALA'].sum(),
  }),
  include_groups=False,
).reset_index()
df_accel_cat['Proporção de assentos acessíveis (%)'] = (
  df_accel_cat['Assentos acessíveis'] / df_accel_cat['Total de assentos'] * 100
).round(2)

bar_prop_cat = (
  alt.Chart(df_accel_cat)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
      x=alt.X('Categoria do exibidor:N', title='Categoria do exibidor', sort=ordem_categorias),
      y=alt.Y('Proporção de assentos acessíveis (%):Q', title='% dos assentos destinado a Pessoas com Deficiência'),
      color=alt.Color('Categoria do exibidor:N', title='Categoria do exibidor'),
      tooltip=['Categoria do exibidor', 'Assentos acessíveis', 'Total de assentos', 'Proporção de assentos acessíveis (%)'],
    )
    .properties(
      height=420,
      title=alt.TitleParams(
        text='Proporção real dos assentos acessíveis, por categoria de exibidor (São Paulo, 2026)',
        anchor='middle',
      ),
    )
)
st.altair_chart(bar_prop_cat)
st.caption('Mede a quantidade efetiva de assentos acessíveis em relação ao total, não apenas se a oferta existe. Na proporção real, exibidores públicos destinam a menor fração de seus assentos a esse público, mesmo tendo boa presença de rampas (item 1b).')

criterio_1 = (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'] > 0)
criterio_2 = (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'] > 0)
criterio_3 = (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'] > 0)
criterio_4 = (df_salas_acessibilidade_sp['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM')
criterio_5 = (df_salas_acessibilidade_sp['ACESSO_SALA_COM_RAMPA'] == 'SIM')
criterio_6 = (df_salas_acessibilidade_sp['BANHEIROS_ACESSIVEIS'] == 'SIM')

st.write(df_salas_acessibilidade_sp[criterio_1 & criterio_2 & criterio_3 & criterio_4 & criterio_5 & criterio_6])

# ---------------------------------------------------------------------------
# (3c) Índice composto de acessibilidade por sala (heatmap por categoria)
# ---------------------------------------------------------------------------
st.subheader('Índice composto de acessibilidade por sala')

df_acc_salas = df_acc_sp_cat.copy()
df_acc_salas['Índice (0-6)'] = df_acc_salas[criterios_porte].sum(axis=1)

# Limita aos 4 grupos de interesse para evitar a categoria 'Outros' residual.
df_acc_salas_hm = df_acc_salas[df_acc_salas['Categoria do exibidor'].isin(
  ['Privado', 'Público', 'Independente', 'Sem grupo']
)]

# Conta quantas salas de cada categoria pontuam em cada índice (0-6).
df_indice_heatmap = (
  df_acc_salas_hm.groupby(['Categoria do exibidor', 'Índice (0-6)'])
    .size()
    .reset_index(name='Número de salas')
)
indices_possiveis = list(range(0, 7))
categorias_heatmap = ['Privado', 'Público', 'Independente', 'Sem grupo']
grid_indice = pd.DataFrame(
  [(cat, i) for cat in categorias_heatmap for i in indices_possiveis],
  columns=['Categoria do exibidor', 'Índice (0-6)'],
)
df_indice_heatmap = grid_indice.merge(df_indice_heatmap, on=['Categoria do exibidor', 'Índice (0-6)'], how='left').fillna({'Número de salas': 0})
df_indice_heatmap['Número de salas'] = df_indice_heatmap['Número de salas'].astype(int)

cell_size=70,

heatmap_indice = (
  alt.Chart(df_indice_heatmap)
    .mark_rect(stroke='white', strokeWidth=2)
    .encode(
      x=alt.X('Índice (0-6):O', title='Índice composto (0-6)', scale=alt.Scale(paddingInner=0), axis=alt.Axis(labelAngle=0)),
      y=alt.Y('Categoria do exibidor:O', title='Categoria do exibidor', scale=alt.Scale(paddingInner=0)),
      color=alt.Color('raiz_salas:Q', title='Número de salas', scale=alt.Scale(scheme='turbo')),
      tooltip=['Categoria do exibidor', 'Índice (0-6)', 'Número de salas'],
    )
    .transform_calculate(raiz_salas='sqrt(datum["Número de salas"])')
    .properties(
      width={'step': 70},
      height={'step': 70},
      title=alt.TitleParams(
        text='Distribuição do índice composto de acessibilidade por categoria de exibidor (São Paulo, 2026)',
        anchor='middle',
      ),
    )
)
st.altair_chart(heatmap_indice)
st.caption('Heatmap da contagem de salas por categoria e pontuação do índice (0-6, um ponto por recurso atendido: assentos para cadeirantes, mobilidade reduzida, obesidade, rampas nos assentos, rampa de acesso à sala e banheiros acessíveis). A cor usa escala de raiz quadrada, para que valores pequenos (1, 6, 8, 13) tenham contraste sem que o pico (251) esmague tudo; o número real aparece ao passar o mouse.')

# ---------------------------------------------------------------------------
# (4) Acessibilidade x Vulnerabilidade social (IPVS 2022) por distrito de SP
# ---------------------------------------------------------------------------
st.subheader('Acessibilidade × Vulnerabilidade social por distrito')

# Mapeia o bairro (informal) registrado na ANCINE para o distrito oficial do
# município (recorte do IPVS 2022, SEADE), que é a unidade de referência do índice.
BAIRRO_DISTRITO = {
    'agua branca': 'Lapa',
    'arthur alvim': 'Artur Alvim',
    'bela vista': 'Bela Vista',
    'butanta': 'Butantã',
    'centro': 'Sé',
    'consolacao': 'Consolação',
    'cerqueira cesar': 'Consolação',
    'chacara dona olivia': 'Cidade Ademar',
    'chacara santa clara - capao redondo': 'Capão Redondo',
    'cidade tiradentes': 'Cidade Tiradentes',
    'conj. hab. barro branco ii': 'Jaraguá',
    'freguesia do o': 'Freguesia do Ó',
    'guaianazes': 'Guaianases',
    'heliopolis': 'Sacomã',
    'higienopolis': 'Santa Cecília',
    'ipiranga': 'Ipiranga',
    'ipiranga.': 'Ipiranga',
    'itaim bibi': 'Itaim Bibi',
    'itaim paulista': 'Itaim Paulista',
    'jardim boa vista': 'São Lucas',
    'jardim da saude': 'Saúde',
    'jardim iguatemi': 'Iguatemi',
    'jardim iris': 'Cidade Ademar',
    'jardim paulista': 'Jardim Paulista',
    'jardim paulistano': 'Morumbi',
    'jardim pirituba': 'Pirituba',
    'jd. guedala': 'Mooca',
    'jabaquara': 'Jabaquara',
    'jaragua': 'Jaraguá',
    'jardim esmeralda': 'Itaquera',
    'jardim guapira': 'Jaçanã',
    'jardim noronha': 'Vila Prudente',
    'jardim parana': 'Santana',
    'jardim santa terezinha': 'Vila Formosa',
    'jardim sao pedro': 'Ipiranga',
    'jardim sao vicente': 'Pirituba',
    'lapa': 'Lapa',
    'lauzane paulista': 'Mandaqui',
    'morumbi': 'Morumbi',
    'parada inglesa': 'Casa Verde',
    'paraiso': 'Vila Mariana',
    'penha de franca': 'Penha',
    'perdizes': 'Perdizes',
    'pinheiros': 'Pinheiros',
    'ponte pequena': 'Tremembé',
    'parque casa de pedra': 'Cidade Ademar',
    'parque cisper': 'Cidade Ademar',
    'parque continental': 'Vila Sônia',
    'parque do carmo': 'Parque do Carmo',
    'pirituba': 'Pirituba',
    'republica': 'República',
    'santa cecilia': 'Santa Cecília',
    'santa ifigenia': 'República',
    'santo amaro': 'Santo Amaro',
    'sao joao climaco': 'São Lucas',
    'sao rafael': 'São Rafael',
    'tatuape': 'Tatuapé',
    'vila andrade': 'Vila Andrade',
    'vila buarque': 'República',
    'vila campanela': 'Sacomã',
    'vila cordeiro': 'Vila Medeiros',
    'vila guilherme': 'Vila Guilherme',
    'vila inglesa': 'Vila Mariana',
    'vila mariana': 'Vila Mariana',
    'vila matilde': 'Vila Matilde',
    'vila olimpia': 'Itaim Bibi',
    'vila prel': 'Sé',
    'vila prudente': 'Vila Prudente',
    'vila romana': 'Lapa',
    'vila gertrudes': 'Sacomã',
    'vila maria': 'Vila Maria',
    'vila nova conceicao': 'Itaim Bibi',
    'vila do sol': 'Tremembé',
}

# Cada entrada: (% de moradores em vulnerabilidade alta - grupos 5 e 6 do IPVS,
# % em vulnerabilidade baixa - grupos 1 e 2). Fonte: SEADE, IPVS 2022.
# https://repositorio.seade.gov.br/dataset/ipvs-tabelas/resource/382bcf29-3e79-4c02-90d4-5c3f9c4a4c01?inner_span=True
IPVS_DISTRITOS = {
    'Água Rasa': (0.00, 91.18),
    'Alto de Pinheiros': (0.00, 97.61),
    'Anhanguera': (32.98, 41.42),
    'Aricanduva': (6.92, 74.48),
    'Artur Alvim': (8.19, 76.54),
    'Barra Funda': (6.53, 84.52),
    'Bela Vista': (0.00, 70.73),
    'Belém': (4.76, 68.54),
    'Bom Retiro': (16.47, 58.97),
    'Brás': (13.57, 41.16),
    'Brasilândia': (52.04, 26.61),
    'Butantã': (1.15, 79.07),
    'Cachoeirinha': (28.56, 51.39),
    'Cambuci': (0.16, 67.77),
    'Campo Belo': (7.58, 90.66),
    'Campo Grande': (3.49, 90.36),
    'Campo Limpo': (31.80, 44.73),
    'Cangaiba': (18.12, 68.64),
    'Capão Redondo': (44.04, 29.01),
    'Carrão': (2.30, 94.82),
    'Casa Verde': (1.08, 87.34),
    'Cidade Ademar': (42.30, 34.93),
    'Cidade Dutra': (25.35, 59.02),
    'Cidade Lider': (15.84, 70.51),
    'Cidade Tiradentes': (52.21, 21.06),
    'Consolação': (0.00, 83.51),
    'Cursino': (7.78, 77.70),
    'Ermelino Matarazzo': (24.12, 52.52),
    'Freguesia do Ó': (6.30, 81.74),
    'Grajaú': (60.91, 16.90),
    'Guaianases': (32.64, 35.79),
    'Moema': (0.00, 99.66),
    'Iguatemi': (53.31, 20.48),
    'Ipiranga': (12.61, 76.02),
    'Itaim Bibi': (0.30, 98.40),
    'Itaim Paulista': (30.19, 33.22),
    'Itaquera': (15.15, 59.97),
    'Jabaquara': (20.38, 63.32),
    'Jaçanã': (26.00, 57.96),
    'Jaguara': (4.79, 80.23),
    'Jaguaré': (29.28, 51.89),
    'Jaraguá': (24.16, 52.33),
    'Jardim Ângela': (70.14, 10.96),
    'Jardim Helena': (46.79, 24.10),
    'Jardim Paulista': (0.00, 98.83),
    'Jardim São Luís': (37.74, 39.76),
    'José Bonifácio': (21.67, 57.17),
    'Lapa': (1.22, 95.38),
    'Liberdade': (0.00, 70.52),
    'Limão': (6.72, 79.56),
    'Mandaqui': (2.79, 83.60),
    'Marsilac': (40.55, 10.76),
    'Mooca': (0.18, 88.19),
    'Morumbi': (14.53, 75.65),
    'Parelheiros': (59.30, 11.67),
    'Pari': (9.66, 64.83),
    'Parque do Carmo': (24.93, 48.80),
    'Pedreira': (56.87, 25.31),
    'Penha': (5.69, 77.36),
    'Perdizes': (0.00, 98.47),
    'Perus': (44.59, 42.13),
    'Pinheiros': (0.00, 98.04),
    'Pirituba': (15.60, 62.42),
    'Ponte Rasa': (5.86, 84.66),
    'Raposo Tavares': (25.06, 42.32),
    'República': (3.65, 60.36),
    'Rio Pequeno': (20.59, 58.38),
    'Sacomã': (25.09, 58.08),
    'Santa Cecília': (0.44, 85.13),
    'Santana': (0.91, 98.33),
    'Santo Amaro': (0.00, 96.66),
    'São Lucas': (7.48, 86.31),
    'São Mateus': (14.54, 62.72),
    'São Miguel': (15.02, 69.99),
    'São Rafael': (53.39, 30.87),
    'Sapopemba': (28.80, 46.43),
    'Saúde': (1.00, 95.49),
    'Sé': (6.87, 29.06),
    'Socorro': (5.61, 83.08),
    'Tatuapé': (0.90, 92.64),
    'Tremembé': (44.38, 43.80),
    'Tucuruvi': (0.23, 95.32),
    'Vila Andrade': (40.78, 51.95),
    'Vila Curuçá': (19.74, 51.83),
    'Vila Formosa': (0.59, 92.66),
    'Vila Guilherme': (2.30, 90.78),
    'Vila Jacuí': (33.83, 47.04),
    'Vila Leopoldina': (6.52, 89.94),
    'Vila Maria': (22.21, 54.91),
    'Vila Mariana': (0.98, 96.17),
    'Vila Matilde': (1.52, 85.55),
    'Vila Medeiros': (12.19, 73.45),
    'Vila Prudente': (6.14, 80.74),
    'Vila Sônia': (23.74, 69.07),
    'São Domingos': (21.52, 68.63),
    'Lajeado': (46.90, 18.93),
}
def _sem_acentos(texto):
  texto = unicodedata.normalize('NFD', str(texto))
  return ''.join(c for c in texto if unicodedata.category(c) != 'Mn').lower().strip()

df_vuln = df_acc_sp_func.copy()
df_vuln['Distrito'] = df_vuln['BAIRRO_COMPLEXO'].map(lambda b: BAIRRO_DISTRITO.get(_sem_acentos(b)))
df_vuln = df_vuln.dropna(subset=['Distrito'])
df_vuln['Índice (0-6)'] = df_vuln[criterios_porte].sum(axis=1)

df_vuln_agg = df_vuln.groupby('Distrito').agg(
  Salas=('NOME_SALA', 'size'),
  Indice_medio=('Índice (0-6)', 'mean'),
).reset_index()
df_vuln_agg['Vuln alta (%)'] = df_vuln_agg['Distrito'].map(lambda d: IPVS_DISTRITOS[d][0])
df_vuln_agg['Vuln baixa (%)'] = df_vuln_agg['Distrito'].map(lambda d: IPVS_DISTRITOS[d][1])
df_vuln_agg['Altamente vulnerável'] = df_vuln_agg['Vuln alta (%)'] >= 40

df_vuln_agg = df_vuln_agg.sort_values('Vuln alta (%)', ascending=False)

bubble_vuln = (
  alt.Chart(df_vuln_agg)
    .mark_circle(opacity=0.85)
    .encode(
      x=alt.X('Vuln alta (%):Q', title='População em vulnerabilidade alta (IPVS 2022, %)', scale=alt.Scale(zero=False)),
      y=alt.Y('Indice_medio:Q', title='Índice médio de acessibilidade (0-6)', scale=alt.Scale(zero=False)),
      size=alt.Size('Salas:Q', title='Salas em funcionamento', scale=alt.Scale(range=[40, 900])),
      color=alt.Color('Altamente vulnerável:N', title='≥ 40% em vulnerabilidade alta', scale=alt.Scale(scheme='set1')),
      tooltip=['Distrito', 'Salas', 'Indice_medio', 'Vuln alta (%)', 'Vuln baixa (%)'],
    )
    .properties(
      height=460,
      title=alt.TitleParams(
        text='Oferta acessível de cinema por distrito × vulnerabilidade social (São Paulo, 2026)',
        anchor='middle',
      ),
    )
)
st.altair_chart(bubble_vuln)
st.caption('Cada bolha é um distrito: eixo X é a parcela da população em grupos de alta vulnerabilidade (IPVS 2022, grupos 5-6); eixo Y, o índice médio de acessibilidade das salas em funcionamento; o tamanho, o número de salas. Distritos com alta vulnerabilidade tendem a concentrar poucas salas — e, em geral, de menor acessibilidade. Nove dos distritos mais vulneráveis não têm nenhuma sala de cinema: Jardim Ângela, Grajaú, Parelheiros, Pedreira, Brasilândia, Lajeado, Jardim Helena, Perus e Marsilac.')

distritos_sem_sala = sorted(
  {d for d in IPVS_DISTRITOS if IPVS_DISTRITOS[d][0] >= 40} - set(df_vuln_agg['Distrito'])
)
if distritos_sem_sala:
  st.write('**Distritos com ≥ 40% da população em alta vulnerabilidade e sem nenhuma sala de cinema:** ' + ', '.join(distritos_sem_sala) + '.')

# ---------------------------------------------------------------------------
# (6) Diagnóstico de acessibilidade por UF (ranking)
# ---------------------------------------------------------------------------
st.subheader('Diagnóstico de acessibilidade por estado (UF)')

df_uf = df_salas_complexos[df_salas_complexos['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'].copy()

for col in ['ASSENTOS_CADEIRANTES', 'ASSENTOS_MOBILIDADE_REDUZIDA', 'ASSENTOS_OBESIDADE']:
  df_uf[col] = df_uf[col].fillna(0) > 0

df_uf['Cadeirantes'] = df_uf['ASSENTOS_CADEIRANTES']
df_uf['Mobilidade reduzida'] = df_uf['ASSENTOS_MOBILIDADE_REDUZIDA']
df_uf['Obesidade'] = df_uf['ASSENTOS_OBESIDADE']
df_uf['Rampa nos assentos'] = df_uf['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM'
df_uf['Rampa de acesso à sala'] = df_uf['ACESSO_SALA_COM_RAMPA'] == 'SIM'
df_uf['Banheiros acessíveis'] = df_uf['BANHEIROS_ACESSIVEIS'] == 'SIM'

criterios_uf = ['Cadeirantes', 'Mobilidade reduzida', 'Obesidade', 'Rampa nos assentos', 'Rampa de acesso à sala', 'Banheiros acessíveis']
df_uf['Índice (0-6)'] = df_uf[criterios_uf].sum(axis=1)

df_uf_agg = df_uf.groupby('UF_COMPLEXO').agg({
  'NOME_SALA': 'size',
  'Índice (0-6)': 'mean',
}).rename(columns={'NOME_SALA': 'Salas', 'Índice (0-6)': 'Índice médio'}).reset_index()

# Percentuais de salas com cada recurso por UF, para tooltip e ranking adicional
for crit in criterios_uf:
  df_uf_agg[f'% {crit}'] = df_uf.groupby('UF_COMPLEXO')[crit].mean().mul(100).round(1).values

df_uf_agg = df_uf_agg.sort_values('Índice médio', ascending=False).reset_index(drop=True)
df_uf_agg['Posição'] = df_uf_agg.index + 1

bar_uf = (
  alt.Chart(df_uf_agg)
    .mark_bar(cornerRadiusEnd=3)
    .encode(
      y=alt.Y('UF_COMPLEXO:N', title='Estado', sort='-x', axis=alt.Axis(labelOverlap=False, labelLimit=100, labelPadding=6)),
      x=alt.X('Índice médio:Q', title='Índice médio de acessibilidade (0-6)', scale=alt.Scale(domain=[0, 6])),
      color=alt.Color('Índice médio:Q', title='Índice médio', scale=alt.Scale(scheme='blues')),
      tooltip=['Posição', 'UF_COMPLEXO', 'Salas', 'Índice médio', '% Rampa de acesso à sala', '% Banheiros acessíveis'],
    )
    .properties(
      height={'step': 22},
      title=alt.TitleParams(
        text='Ranking dos estados por índice médio de acessibilidade das salas em funcionamento (2026)',
        anchor='middle',
      ),
    )
)
st.altair_chart(bar_uf)
st.caption('Ranking das UFs pelo índice composto médio (0-6, um ponto por recurso: assentos para cadeirantes, mobilidade reduzida, obesidade, rampa nos assentos, rampa de acesso à sala e banheiros acessíveis), considerando apenas salas em funcionamento. A barra mais clara (menor índice) indica menor acessibilidade média. O líder é Roraima (4,85) e o último, Acre (2,43). A variância é maior nos critérios mais raros: rampa de acesso à sala (de 0% no Acre a 48,5% no Mato Grosso) e banheiros acessíveis (de 37% em Tocantins a 100% no Acre).')
