import streamlit as st
import pandas as pd

from views.eixo_4.sections.section_1_coproducoes import section as section_1
from views.eixo_4.sections.section_2_filmagens import section as section_2
from views.eixo_4.sections.section_3_agentes_economicos import section as section_3

from lib.normalizers import classificar_tipo, normaliza_pais, normaliza_nr_tecnicos
from data.loaders import load_data
from data.loaders import load_obras_brasileiras

DATA_URL = {
  'coproducoes': 'https://dados.ancine.gov.br/dados-abertos/coproducoes-internacionais-participacao-brasileira.csv',
  'filmagens': 'https://dados.ancine.gov.br/dados-abertos/filmagem-estrangeira.csv',
  'agentes': 'https://dados.ancine.gov.br/dados-abertos/agentes-economicos-estrangeiros-regulares.csv',
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
}

DATA_PAGE_SOURCE = {
  'Coproduções Internacionais': 'https://dados.gov.br/dados/conjuntos-dados/coproducoes-internacionais---participacao-brasileira',
  'Filmagens Estrangeiras': 'https://dados.gov.br/dados/conjuntos-dados/filmagem-estrangeira-relacao-de-producao-de-obras-audiovisuais-estrangeiras-em-territorio-nacional',
  'Agentes Econômicos Estrangeiros': 'https://dados.gov.br/dados/conjuntos-dados/agentes-economicos-estrangeiros',
  'Obras Não Publicitárias': 'https://dados.gov.br/dados/conjuntos-dados/obras-nao-publicitarias-brasileiras-registradas-na-ancine',
}

st.title('Eixo 4 - Coproduções internacionais e filmagens estrangeiras')

df_coproducoes = load_data(DATA_URL['coproducoes'])
df_filmagens = load_data(DATA_URL['filmagens'])
df_agentes = load_data(DATA_URL['agentes'])
df_obras = load_obras_brasileiras(DATA_URL['obras'])

# Preparação dos dados
df_filmagens.drop_duplicates(inplace=True)
df_filmagens['TIPO_OBRA'] = df_filmagens['TIPO_OBRA'].map(classificar_tipo)
df_filmagens['PAIS'] = df_filmagens['PAIS'].map(normaliza_pais)
df_filmagens['NR_TECNICOS_ARTISTAS_ESTRANGEIROS'] = df_filmagens['NR_TECNICOS_ARTISTAS_ESTRANGEIROS'].map(normaliza_nr_tecnicos)

df_agentes['DATA_REGISTRO'] = pd.to_datetime(df_agentes['DATA_REGISTRO'], errors='coerce', dayfirst=True)
df_agentes['ANO_REGISTRO'] = df_agentes['DATA_REGISTRO'].dt.year

with st.sidebar:
  st.caption('Links para fontes de dados:')
  with st.container(horizontal=False):
    for nome, link in DATA_PAGE_SOURCE.items():
      st.link_button(nome, link, width='stretch')
  with st.container(horizontal=True, horizontal_alignment='center'):
    st.image('assets/logo_spcine-principal.png', width=96, link='https://spcine.com.br/')

tab1, tab2, tab3 = st.tabs([
  'Coproduções internacionais',
  'Filmagens estrangeiras',
  'Agentes econômicos',
])

with tab1:
  section_1(df_coproducoes, df_obras)
with tab2:
  section_2(df_filmagens)
with tab3:
  section_3(df_agentes)