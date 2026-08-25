import streamlit as st
import pandas as pd

from charts.bar import plot_custom_ranking_bar_chart
from charts.line import plot_custom_line_chart

def section(df_agentes):
  st.header('Panorama geral dos agentes econômicos estrangeiros')

  total_agentes = df_agentes['REGISTRO_ANCINE'].nunique()
  total_representantes = df_agentes['REGISTRO_REPRESENTANTE'].nunique()

  with st.container(horizontal=True):
    st.metric('Total de agentes estrangeiros', f'{total_agentes:,}', border=True)
    st.metric('Total de representantes', f'{total_representantes:,}', border=True)

  st.subheader('Distribuição por atividade principal')
  df_atividade = (
    df_agentes.groupby('ATIVIDADE_PRINCIPAL')
      .agg(QTD=('REGISTRO_ANCINE', 'nunique'))
      .reset_index()
      .sort_values('QTD', ascending=False)
  )
  with st.container(border=True):
    plot_custom_ranking_bar_chart(
      df=df_atividade,
      x='QTD',
      x_title='Nº de agentes',
      y='ATIVIDADE_PRINCIPAL',
      y_title=None,
      title='Agentes estrangeiros por atividade principal',
      tooltip=['ATIVIDADE_PRINCIPAL', 'QTD'],
      color='QTD',
      color_scheme='viridis',
      label_limit=240,
      step=26,
    )

  st.subheader('Representantes com mais agentes estrangeiros')
  df_representantes = (
    df_agentes.groupby('REPRESENTANTE')
      .agg(QTD=('REGISTRO_ANCINE', 'nunique'))
      .reset_index()
      .sort_values('QTD', ascending=False)
  )
  with st.container(border=True):
    plot_custom_ranking_bar_chart(
      df=df_representantes.head(10),
      x='QTD',
      x_title='Nº de agentes representados',
      y='REPRESENTANTE',
      y_title=None,
      title='Top representantes por nº de agentes estrangeiros',
      tooltip=['REPRESENTANTE', 'QTD'],
      color='QTD',
      color_scheme='viridis',
      label_limit=260,
      step=26,
    )

  st.subheader('Evolução temporal dos registros de agentes')
  df_ano_registro = (
    df_agentes.groupby('ANO_REGISTRO')
      .agg(QTD=('REGISTRO_ANCINE', 'nunique'))
      .reset_index()
      .dropna()
      .sort_values('ANO_REGISTRO')
  )
  with st.container(border=True):
    plot_custom_line_chart(
      df=df_ano_registro,
      x='ANO_REGISTRO',
      x_title='Ano do registro',
      y='QTD',
      y_title='Nº de registros',
      title='Evolução dos registros de agentes estrangeiros por ano',
      x_nice=False,
    )

  return