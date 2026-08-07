import streamlit as st
import pandas as pd
import numpy as np
from charts.line import plot_custom_line_chart
from charts.bar import plot_custom_grouped_bar_chart

def section(df_salas_evolucao, df_complexos_evolucao):
  st.header('1. Evolução temporal de espaços de cinema')
  df_salas_sp = df_salas_evolucao[df_salas_evolucao['MUNICIPIO'] == 'SÃO PAULO']
  df_serie_salas_sp = df_salas_sp.value_counts('ANO').sort_index().reset_index().rename(columns={
    'ANO': 'Ano',
    'count': 'Qtde'
  })

  df_salas_status_ano = df_salas_sp.value_counts(['ANO', 'STATUS']).reset_index(name='QUANTIDADE')

  with st.container():
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(border=True):
        plot_custom_line_chart(
          df=df_serie_salas_sp,
          x='Ano',
          x_title='Ano',
          y='Qtde',
        y_title='Quantidade de salas registradas',
        title='Quantidade de salas registradas por ano no município de São Paulo'
      )
    
    with col2:
      with st.container(border=True):
        plot_custom_grouped_bar_chart(
          df=df_salas_status_ano,
          x='ANO',
          x_title='Ano',
          y='QUANTIDADE',
          y_title='Quantidade de complexos',
          x_offset='STATUS',
          x_offset_title='Status',
          title='Distribuição de salas por status e ano no município de São Paulo',
          x_scale_sort=np.sort(df_salas_status_ano['ANO'].unique())
        )

  df_complexos_sp = df_complexos_evolucao[df_complexos_evolucao['MUNICIPIO'] == 'SÃO PAULO']
  df_serie_complexos_sp = df_complexos_sp.value_counts('ANO').sort_index().reset_index().rename(columns={
    'ANO': 'Ano',
    'count': 'Qtde'
  })
  df_complexos_status_ano = df_complexos_sp.value_counts(['ANO', 'STATUS']).reset_index().rename(columns={ 'count': 'QUANTIDADE' })

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(border=True): 
        plot_custom_line_chart(
          df=df_serie_complexos_sp,
          x='Ano',
          x_title='Ano',
          y='Qtde',
          y_title='Quantidade de complexos registradas',
          title='Quantidade de complexos registradas por ano no município de São Paulo'
        )

    with col2:
      with st.container(border=True):
        plot_custom_grouped_bar_chart(
          df=df_complexos_status_ano,
          x='ANO',
          x_title='Ano',
          y='QUANTIDADE',
          y_title='Quantidade de complexos',
          x_offset='STATUS',
          x_offset_title='Status',
          title='Distribuição de complexos por status e ano no município de São Paulo',
          x_scale_sort=np.sort(df_complexos_status_ano['ANO'].unique())
        )
