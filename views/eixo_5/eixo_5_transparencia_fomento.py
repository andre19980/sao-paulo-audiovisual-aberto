import streamlit as st
import pandas as pd

from views.eixo_5.sections.section_1_projetos_fsa import section as section_1
from views.eixo_5.sections.section_2_prestacao_contas import section as section_2
from views.eixo_5.sections.section_3_fsa_renuncia_fiscal import section as section_3

from lib.normalizers import converte_moeda, normaliza_cnpj, normaliza_municipio
from data.loaders import load_data

DATA_URL = {
  'projetos_fsa': 'https://dados.ancine.gov.br/dados-abertos/projetos-fsa.csv',
  'processos_prest': 'https://dados.ancine.gov.br/dados-abertos/processos-em-prestacao-de-contas.csv',
  'contribuintes_renfisc': 'https://dados.ancine.gov.br/dados-abertos/contribuintes-em-projetos-com-renuncia-fiscal.csv',
  'produtoras_independentes': 'https://dados.ancine.gov.br/dados-abertos/produtoras-independentes.csv',
  'projetos_renuncia_fiscal': 'https://dados.ancine.gov.br/dados-abertos/projetos-com-renuncia-fiscal.csv',
}

st.title('Eixo 5 - Transparência e Eficiência do Fomento Público')

data_load_state = st.text('Baixando e descompactando dados da ANCINE...')

df_projetos_fsa = load_data(DATA_URL['projetos_fsa'])
df_processos_prest = load_data(DATA_URL['processos_prest'])
df_contribuintes_renfisc = load_data(DATA_URL['contribuintes_renfisc'])
df_produtoras_independentes = load_data(DATA_URL['produtoras_independentes'])
df_projetos_renfisc = load_data(DATA_URL['projetos_renuncia_fiscal'])

data_load_state.text('Dados carregados com sucesso!')

# Preparação dos dados
df_projetos_fsa['VALOR_CONTRATO_DOU'] = df_projetos_fsa['VALOR_CONTRATO_DOU'].apply(converte_moeda)
df_projetos_fsa['VALOR_TOTAL_LIBERADO'] = df_projetos_fsa['VALOR_TOTAL_LIBERADO'].apply(converte_moeda)

# Renúncia fiscal: converte moeda e normaliza município
for col in [c for c in df_projetos_renfisc.columns if c.startswith('CAPTADO')] + ['TOTAL_CAPTADO']:
  df_projetos_renfisc[col] = df_projetos_renfisc[col].apply(converte_moeda)
df_projetos_renfisc['MUNICIPIO_PROPONENTE'] = df_projetos_renfisc['MUNICIPIO_PROPONENTE'].map(normaliza_municipio)
df_projetos_renfisc['CNPJ_LIMPO'] = df_projetos_renfisc['CNPJ_PROPONENTE'].apply(normaliza_cnpj)
df_projetos_fsa['CNPJ_LIMPO'] = df_projetos_fsa['CNPJ_PROPONENTE'].apply(normaliza_cnpj)
    
# Converter datas
df_projetos_fsa['DATA_CONTRATO'] = pd.to_datetime(
  df_projetos_fsa['DATA_EXTRATO_CONTRATO_DOU'], 
  errors='coerce',
  dayfirst=True
)
df_projetos_fsa['ANO_CONTRATO'] = df_projetos_fsa['DATA_CONTRATO'].dt.year

df_projetos_fsa['DATA_DESEMBOLSO'] = pd.to_datetime(
  df_projetos_fsa['DATA_PRIMEIRO_DESEMBOLSO'], 
  errors='coerce',
  dayfirst=True
)


# Exibição dos dados para fins de debug
st.subheader('Visão geral dos dados carregados')
# st.write(f'**{len(df_obras):,}** obras registradas entre {int(df_obras["ANO"].min())} e {int(df_obras["ANO"].max())}, '
#          f'a partir de **{df_obras["ANO"].nunique()}** arquivos anuais.')

# st.subheader('Amostra das obras')
# st.dataframe(df_obras.head(20), hide_index=True)
st.subheader('Projetos de investimento contratados no âmbito do FSA')
st.write(df_projetos_fsa)
st.subheader('Relação de processos em fase de prestação de contas')
st.write(df_processos_prest)
st.subheader('Relação de contribuintes que aplicaram em projetos com renúncia fiscal')
st.write(df_contribuintes_renfisc)

tab1, tab2, tab3 = st.tabs([
  'Projetos contratados via FSA',
  'Prestação de contas',
  'Projetos com renúncia fiscal',
])

# print("\n📌 df_contribuintes:")
# print(f"  - Total de contribuintes: {len(df_contribuintes)}")
# print(f"  - Pessoas físicas: {len(df_contribuintes[df_contribuintes['CNPJ_CONTRIBUINTE'] == 'PESSOA FÍSICA'])}")
# print(f"  - Pessoas jurídicas: {len(df_contribuintes[df_contribuintes['CNPJ_CONTRIBUINTE'] != 'PESSOA FÍSICA'])}")

with tab1:
  section_1(df_projetos_fsa, df_produtoras_independentes)
with tab2:
  section_2(df_processos_prest)
with tab3:
  section_3(df_projetos_fsa, df_projetos_renfisc)
