import streamlit as st
import pandas as pd

from views.eixo_4.sections.section_1_coproducoes import section as section_1
from views.eixo_4.sections.section_2_filmagens import section as section_2

from lib.normalizers import classificar_tipo, normaliza_pais, normaliza_nr_tecnicos
from data.loaders import load_data
from data.loaders import load_obras_brasileiras

DATA_URL = {
  'coproducoes': 'https://dados.ancine.gov.br/dados-abertos/coproducoes-internacionais-participacao-brasileira.csv',
  'filmagens': 'https://dados.ancine.gov.br/dados-abertos/filmagem-estrangeira.csv',
  'agentes': 'https://dados.ancine.gov.br/dados-abertos/agentes-economicos-estrangeiros-regulares.csv',
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
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

# Exibição dos dados para fins de debug
st.subheader('Visão geral dos dados carregados')
st.write(f'**{len(df_obras):,}** obras registradas entre {int(df_obras["ANO"].min())} e {int(df_obras["ANO"].max())}, '
         f'a partir de **{df_obras["ANO"].nunique()}** arquivos anuais.')
st.dataframe(df_obras.head(20))

st.subheader('Coproduções')
st.dataframe(df_coproducoes)
st.subheader('Filmagens')
st.write(df_filmagens)
st.subheader('Agentes internacionais')
st.write(df_agentes)

tab1, tab2, tab3, tab4 = st.tabs([
  'Coproduções internacionais',
  'Filmagens estrangeiras',
  'Agentes econômicos',
  'Cruzamentos',
])

with tab1:
  section_1(df_coproducoes, df_obras)
with tab2:
  section_2(df_filmagens, df_obras)