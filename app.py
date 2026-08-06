import streamlit as st

import streamlit as st

eixo_1_page = st.Page(
  "eixo_1_mapeamento_oferta_cultural.py",
  title="Eixo 1: Mapeamento da Oferta Cultural",
  icon=":material/add_circle:"
)
eixo_2_page = st.Page(
  "eixo_2.py",
  title="Eixo 2: Análise da Demografia",
  icon=":material/add_circle:"
)

pg = st.navigation([eixo_1_page, eixo_2_page])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()
