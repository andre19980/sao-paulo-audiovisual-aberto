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

DATA_PAGE_SOURCE = {
  'Salas de Exibição e Complexos': 'https://dados.gov.br/dados/conjuntos-dados/salas-de-exibicao-e-complexos-registrados-na-ancine',
  'Salas de Exibição - Evolução Anual': 'https://dados.gov.br/dados/conjuntos-dados/salas-de-exibicao---evolucao-anual',
  'Complexos - Evolução Anual': 'https://dados.gov.br/dados/conjuntos-dados/complexos-cinematograficos---evolucao-anual',
}

st.title('Eixo 1 - Mapeamento da Oferta Cultural (Cinemas e Salas de Exibição)')

df_salas_complexos = load_data(DATA_URLS['salas_de_exibicao_e_complexos'])
df_salas_evolucao = load_data(DATA_URLS['salas_evolucao'])
df_complexos_evolucao = load_data(DATA_URLS['complexos_evolucao'])

with st.sidebar:
  st.caption('Links para fontes de dados:')
  with st.container(horizontal=False):
    for nome, link in DATA_PAGE_SOURCE.items():
      st.link_button(nome, link, width='stretch')
  with st.container(horizontal=True, horizontal_alignment='center'):
    st.image('assets/logo_spcine-principal.png', width=96, link='https://spcine.com.br/')

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
