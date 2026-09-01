import streamlit as st

from views.eixo_3.sections.section_1_lancamentos_distribuidoras import section

from data.loaders import load_data, load_obras_brasileiras

DATA_URLS = {
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
  'lancamentos_comerciais': 'https://dados.ancine.gov.br/dados-abertos/lancamentos-comerciais-por-distribuidoras.csv'
}

DATA_PAGE_SOURCE = {
  'Lançamentos por Distribuidoras': 'https://dados.gov.br/dados/conjuntos-dados/lancamentos-comerciais-por-distribuidoras',
  'Obras Não Publicitárias': 'https://dados.gov.br/dados/conjuntos-dados/obras-nao-publicitarias-brasileiras-registradas-na-ancine',
}

st.title('Eixo 3 - Análise de Público e Consumo Cultural')

df_obras = load_obras_brasileiras(DATA_URLS['obras'])
df_lancamentos = load_data(DATA_URLS['lancamentos_comerciais'])

with st.sidebar:
  st.caption('Links para fontes de dados:')
  with st.container(horizontal=False):
    for nome, link in DATA_PAGE_SOURCE.items():
      st.link_button(nome, link, width='stretch')
  with st.container(horizontal=True, horizontal_alignment='center'):
    st.image('assets/logo_spcine-principal.png', width=96, link='https://spcine.com.br/')

section(df_lancamentos, df_obras)
