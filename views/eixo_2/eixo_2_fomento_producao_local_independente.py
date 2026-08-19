import streamlit as st

from views.eixo_2.sections.section_1_produtoras_independentes_obras import section as section_1
from views.eixo_2.sections.section_2_projetos_renuncia_fiscal_municipios import section as section_2
from views.eixo_2.sections.section_3_segmentacao_de_obras import section as section_3

from data.loaders import load_obras_brasileiras
from data.loaders import load_data

DATA_URL = {
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
  'produtoras_independentes': 'https://dados.ancine.gov.br/dados-abertos/produtoras-independentes.csv',
  'produtores': 'https://dados.ancine.gov.br/dados-abertos/produtores-de-obras-nao-publicitarias-brasileiras.csv',
  'projetos_renuncia_fiscal': 'https://dados.ancine.gov.br/dados-abertos/projetos-com-renuncia-fiscal.csv',
}

st.title('Eixo 2 - Fomento à Produção Local e Independente (Obras Não Publicitárias Brasileiras)')

data_load_state = st.text('Baixando e descompactando dados da ANCINE...')

df_obras = load_obras_brasileiras(DATA_URL['obras'])
df_produtoras_independentes = load_data(DATA_URL['produtoras_independentes'])
df_produtores = load_data(DATA_URL['produtores'])
df_projetos_renfisc = load_data(DATA_URL['projetos_renuncia_fiscal'])

data_load_state.text('Dados carregados com sucesso!')

st.subheader('Visão geral dos dados carregados')
st.write(f'**{len(df_obras):,}** obras registradas entre {int(df_obras["ANO"].min())} e {int(df_obras["ANO"].max())}, '
         f'a partir de **{df_obras["ANO"].nunique()}** arquivos anuais.')

st.subheader('Amostra dos dados')
st.dataframe(df_obras.head(20), hide_index=True)

st.subheader('Produtoras independentes')
st.write(df_produtoras_independentes)
st.subheader('Produtores de obras não publis')
st.write(df_produtores)
st.subheader('Projetos com renúncia fiscal')
st.write(df_projetos_renfisc)

tab1, tab2, tab3 = st.tabs([
  'Produtoras independentes e obras',
  'Projetos com renúncia fiscal',
  'Segmentação de obras',
])

with tab1:
  section_1(df_produtoras_independentes, df_produtores)
with tab2:
  section_2(df_projetos_renfisc, df_produtoras_independentes)
with tab3:
  section_3(df_obras)
