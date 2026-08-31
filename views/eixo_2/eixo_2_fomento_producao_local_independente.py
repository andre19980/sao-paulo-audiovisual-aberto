import streamlit as st

from views.eixo_2.sections.section_1_produtoras_independentes_obras import section as section_1
from views.eixo_2.sections.section_2_projetos_renuncia_fiscal_municipios import section as section_2
from views.eixo_2.sections.section_3_segmentacao_de_obras import section as section_3

from data.loaders import load_obras_brasileiras
from data.loaders import load_data
from lib.checkers import checa_municipio
from lib.normalizers import normaliza_municipio, converte_moeda, normaliza_cnpj

DATA_URL = {
  'obras': 'https://dados.ancine.gov.br/dados-abertos/obras-nao-pub-brasileiras-csv.zip',
  'produtoras_independentes': 'https://dados.ancine.gov.br/dados-abertos/produtoras-independentes.csv',
  'produtores': 'https://dados.ancine.gov.br/dados-abertos/produtores-de-obras-nao-publicitarias-brasileiras.csv',
  'projetos_renuncia_fiscal': 'https://dados.ancine.gov.br/dados-abertos/projetos-com-renuncia-fiscal.csv',
}

st.title('Eixo 2 - Fomento à Produção Local e Independente (Obras Não Publicitárias Brasileiras)')

df_obras = load_obras_brasileiras(DATA_URL['obras'])
df_produtoras_independentes = load_data(DATA_URL['produtoras_independentes'])
df_produtores = load_data(DATA_URL['produtores'])
df_projetos_renfisc = load_data(DATA_URL['projetos_renuncia_fiscal'])

# Preparação dos dados
municipios_conflitantes = checa_municipio(df_produtoras_independentes['MUNICIPIO'])
for normalizado, original in municipios_conflitantes.items():
  df_produtoras_independentes['MUNICIPIO'] = df_produtoras_independentes['MUNICIPIO'].replace(original, normalizado)

df_projetos_renfisc['MUNICIPIO_PROPONENTE'] = (
  df_projetos_renfisc['MUNICIPIO_PROPONENTE'].map(normaliza_municipio)
)

colunas_monetarias = [
  'CAPTADO_ART1', 'CAPTADO_ART1A', 'CAPTADO_ART3', 'CAPTADO_ART3A',
  'CAPTADO_ART18', 'CAPTADO_ART25', 'CAPTADO_ART39', 'CAPTADO_FUNCINES',
  'CAPTADO_EDITAL_ANCINE', 'CAPTADO_PAR', 'CAPTADO_PAQ', 'CAPTADO_OUTROS_EDITAIS',
  'CAPTADO_LEI_ESTADUAL', 'CAPTADO_LEI_MUNICIPAL', 'CAPTADO_OUTRAS_FONTES',
  'CAPTADO_CONTRAPARTIDA', 'CAPTADO_CONVERSAO', 'TOTAL_CAPTADO'
]

for col in colunas_monetarias:
  df_projetos_renfisc[col] = df_projetos_renfisc[col].apply(converte_moeda)
  
df_produtoras_independentes['CNPJ_LIMPO'] = df_produtoras_independentes['CNPJ'].apply(normaliza_cnpj)
df_produtores['CNPJ_LIMPO'] = df_produtores['CNPJ_PRODUTOR'].apply(normaliza_cnpj)
df_projetos_renfisc['CNPJ_LIMPO'] = df_projetos_renfisc['CNPJ_PROPONENTE'].apply(normaliza_cnpj)

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
