import streamlit as st

eixo_1_page = st.Page(
  "views/eixo_1/eixo_1_mapeamento_oferta_cultural.py",
  title="Eixo 1: Mapeamento da Oferta Cultural",
  icon=":material/map:"
)
eixo_2_page = st.Page(
  "views/eixo_2/eixo_2_fomento_producao_local_independente.py",
  title="Eixo 2: Fomento à Produção Local e Independente",
  icon=":material/monitoring:"
)

eixo_4_page = st.Page(
  "views/eixo_4/eixo_4_coproducoes_internacionais.py",
  title="Eixo 4: Coproduções Internacionais e Filmagens Estrangeiras",
  icon=":material/partner_exchange:"
)

eixo_5_page = st.Page(
  "views/eixo_5/eixo_5_transparencia_fomento.py",
  title="Eixo 5: Transparência e Eficiência do Fomento Público",
  icon=":material/query_stats:"
)

pg = st.navigation([eixo_1_page, eixo_2_page, eixo_4_page, eixo_5_page])
st.set_page_config(page_title="Audiovisual SP Aberto", page_icon=":material/animated_images:", layout="wide")
pg.run()
