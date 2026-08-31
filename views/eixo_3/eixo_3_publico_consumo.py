import streamlit as st

from views.eixo_3.sections.section_1_lancamentos_distribuidoras import section

from data.loaders import load_data, load_obras_brasileiras

DATA_URLS = {
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
  'lancamentos_comerciais': 'https://dados.ancine.gov.br/dados-abertos/lancamentos-comerciais-por-distribuidoras.csv'
}

st.title('Eixo 3 - Análise de Público e Consumo Cultural')

df_obras = load_obras_brasileiras(DATA_URLS['obras'])
df_lancamentos = load_data(DATA_URLS['lancamentos_comerciais'])

section(df_lancamentos, df_obras)
