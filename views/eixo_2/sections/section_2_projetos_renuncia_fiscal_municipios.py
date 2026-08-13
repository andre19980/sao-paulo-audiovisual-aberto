import pandas as pd
import streamlit as st
import altair as alt

from lib.normalizers import converte_moeda

def section(df_projetos_renfisc):
  colunas_monetarias = [
    'CAPTADO_ART1', 'CAPTADO_ART1A', 'CAPTADO_ART3', 'CAPTADO_ART3A',
    'CAPTADO_ART18', 'CAPTADO_ART25', 'CAPTADO_ART39', 'CAPTADO_FUNCINES',
    'CAPTADO_EDITAL_ANCINE', 'CAPTADO_PAR', 'CAPTADO_PAQ', 'CAPTADO_OUTROS_EDITAIS',
    'CAPTADO_LEI_ESTADUAL', 'CAPTADO_LEI_MUNICIPAL', 'CAPTADO_OUTRAS_FONTES',
    'CAPTADO_CONTRAPARTIDA', 'CAPTADO_CONVERSAO', 'TOTAL_CAPTADO'
  ]

  for col in colunas_monetarias:
    df_projetos_renfisc[col] = df_projetos_renfisc[col].apply(converte_moeda)

  st.subheader('Renúncia fiscal e captação por município')
  col_metric1, col_metric2, col_metric3 = st.columns([1, 1, 1], gap='large')
  with col_metric1:
    st.metric("Total captado", f"R$ {df_projetos_renfisc['TOTAL_CAPTADO'].sum():,.0f}", border=True)
  with col_metric2:
    st.metric("Média por projeto", f"R$ {df_projetos_renfisc['TOTAL_CAPTADO'].mean():,.0f}", border=True)
  with col_metric3:
    st.metric("Projetos", f"{df_projetos_renfisc.shape[0]:,}", border=True)

  # Ranking de municípios por total captado (barra horizontal).
  df_municipios = df_projetos_renfisc.groupby(['MUNICIPIO_PROPONENTE', 'UF_PROPONENTE']).agg(
    TOTAL_CAPTADO=('TOTAL_CAPTADO', 'sum'),
    N_PROJETOS=('TITULO_PROJETO', 'count'),
  ).reset_index().sort_values('TOTAL_CAPTADO', ascending=False)

  st.subheader('Top municípios por total captado')
  st.caption(
    'Valor total captado por projetos de renúncia fiscal segundo o município do proponente. '
    'RIO DE JANEIRO e SÃO PAULO dominam com folga; o eixo é logarítmico para acomodar a grande '
    'disparidade de escala entre as duas capitais e os demais municípios.'
  )
  top_municipios = df_municipios.head(15)
  top_mun_chart = (
    alt.Chart(top_municipios)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        x=alt.X('TOTAL_CAPTADO:Q', title='Total captado (R$)', scale=alt.Scale(type='log')),
        y=alt.Y('MUNICIPIO_PROPONENTE:N', title=None, sort='-x', axis=alt.Axis(labelLimit=240)),
        color=alt.Color('TOTAL_CAPTADO:Q', legend=None, scale=alt.Scale(scheme='blues')),
        tooltip=['MUNICIPIO_PROPONENTE', 'UF_PROPONENTE', 'N_PROJETOS', 'TOTAL_CAPTADO'],
      )
      .properties(
        height={'step': 22},
        title=alt.TitleParams(text='Top 15 municípios por captação via renúncia fiscal (2026)', anchor='start'),
      )
  )
  st.altair_chart(top_mun_chart)

  # Comparativo entre capitais.
  capitais = ['SÃO PAULO', 'RIO DE JANEIRO', 'BRASÍLIA', 'BELO HORIZONTE', 'CURITIBA',
              'PORTO ALEGRE', 'SALVADOR', 'RECIFE', 'FORTALEZA']
  df_capitais = df_municipios[df_municipios['MUNICIPIO_PROPONENTE'].isin(capitais)].copy()
  df_capitais['MEDIA_POR_PROJETO'] = df_capitais['TOTAL_CAPTADO'] / df_capitais['N_PROJETOS']
  df_capitais = df_capitais.sort_values('TOTAL_CAPTADO', ascending=False)

  st.subheader('Comparativo entre capitais')
  st.caption(
    'Total captado e valor médio por projeto para as principais capitais. RIO DE JANEIRO e '
    'SÃO PAULO concentram o grosso da captação; FORTALEZA e BRASÍLIA aparecem com as maiores '
    'médias por projeto entre as capitais de menor porte.'
  )
  cap_chart = (
    alt.Chart(df_capitais)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        x=alt.X('TOTAL_CAPTADO:Q', title='Total captado (R$)'),
        y=alt.Y('MUNICIPIO_PROPONENTE:N', title=None, sort='-x', axis=alt.Axis(labelLimit=200)),
        color=alt.Color('MEDIA_POR_PROJETO:Q', title='Média por projeto (R$)', scale=alt.Scale(scheme='tealblues')),
        tooltip=['MUNICIPIO_PROPONENTE', 'N_PROJETOS', 'TOTAL_CAPTADO', 'MEDIA_POR_PROJETO'],
      )
      .properties(
        height={'step': 26},
        title=alt.TitleParams(text='Captação por capital (renúncia fiscal, 2026)', anchor='start'),
      )
  )
  st.altair_chart(cap_chart)

  # Participação de cada mecanismo de captação.
  mecanismos = {
    'Art. 1º': 'CAPTADO_ART1',
    'Art. 1º-A': 'CAPTADO_ART1A',
    'Art. 3º': 'CAPTADO_ART3',
    'Art. 3º-A': 'CAPTADO_ART3A',
    'Art. 18': 'CAPTADO_ART18',
    'Art. 25': 'CAPTADO_ART25',
    'Art. 39': 'CAPTADO_ART39',
    'Funcines': 'CAPTADO_FUNCINES',
    'Edital ANCINE': 'CAPTADO_EDITAL_ANCINE',
    'Lei estadual': 'CAPTADO_LEI_ESTADUAL',
    'Lei municipal': 'CAPTADO_LEI_MUNICIPAL',
    'Outras fontes': 'CAPTADO_OUTRAS_FONTES',
  }
  df_mec = pd.DataFrame({
    'Mecanismo': list(mecanismos.keys()),
    'Total captado': [df_projetos_renfisc[col].sum() for col in mecanismos.values()],
  }).sort_values('Total captado', ascending=False)

  st.subheader('Captação por mecanismo de incentivo')
  st.caption(
    'Distribuição do total captado entre os mecanismos de fomento. Os artigos 3º-A e 3º da Lei '
    'do Audiovisual lideram, seguidos do 1º-A e do 39 — ou seja, a produção local independente '
    'depende fortemente de poucos mecanismos federais de incentivo indireto.'
  )
  mec_chart = (
    alt.Chart(df_mec)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        x=alt.X('Total captado:Q', title='Total captado (R$)', scale=alt.Scale(type='log')),
        y=alt.Y('Mecanismo:N', title=None, sort='-x', axis=alt.Axis(labelLimit=180)),
        color=alt.Color('Total captado:Q', legend=None, scale=alt.Scale(scheme='viridis')),
        tooltip=['Mecanismo', 'Total captado'],
      )
      .properties(
        height={'step': 24},
        title=alt.TitleParams(text='Captação por mecanismo de fomento (2026)', anchor='start'),
      )
  )
  st.altair_chart(mec_chart)

  return
