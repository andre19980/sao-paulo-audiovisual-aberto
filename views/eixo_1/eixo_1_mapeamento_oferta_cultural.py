import streamlit as st

from views.eixo_1.sections.section_1_evolucao_temporal_espacos import section as section_1
from views.eixo_1.sections.section_2_densidade_complexos import section as section_2
from views.eixo_1.sections.section_3_operacao_exibidores import section as section_3
from views.eixo_1.sections.section_4_acessibilidade import section as section_4

from data.loaders import load_data

DATA_URLS = {
  'salas_de_exibicao_e_complexos': 'https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-e-complexos.csv',
  'salas_evolucao': 'https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-evolucao-anual.csv',
  'complexos_evolucao': 'https://dados.ancine.gov.br/dados-abertos/complexos-cinematograficos-evolucao-anual.csv'
}

st.title('Eixo 1 - Mapeamento da Oferta Cultural (Cinemas e Salas de Exibição)')

df_salas_complexos = load_data(DATA_URLS['salas_de_exibicao_e_complexos'])
df_salas_evolucao = load_data(DATA_URLS['salas_evolucao'])
df_complexos_evolucao = load_data(DATA_URLS['complexos_evolucao'])

tab1, tab2, tab3, tab4 = st.tabs([
  'Evolução de espaços',
  'Densidade por complexos',
  'Exibidores e operação',
  'Acessibilidade'
])

with tab1:
  section_1(df_salas_evolucao, df_complexos_evolucao)
with tab2:
  section_2(df_complexos_evolucao, df_salas_complexos)
with tab3:
  section_3(df_salas_complexos)
with tab4:
  section_4(df_salas_complexos)
