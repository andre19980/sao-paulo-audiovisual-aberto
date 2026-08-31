import streamlit as st
import pandas as pd
import numpy as np
import json as _json

from charts.pie import plot_custom_pie_chart
from charts.bar import plot_custom_ranking_bar_chart
from charts.heatmap import plot_custom_heatmap
from charts.brazil_map import plot_custom_choropleth_brazil_map
from charts.line import plot_custom_grouped_line_chart

def section(df_coproducoes, df_obras):  
  total_coproducoes = len(df_coproducoes)
  acordos_validos = df_coproducoes[df_coproducoes['ACORDO_COPRODUCAO'].notna() & (df_coproducoes['ACORDO_COPRODUCAO'] != '')]
  acordos_vazios = df_coproducoes[df_coproducoes['ACORDO_COPRODUCAO'].isna() | (df_coproducoes['ACORDO_COPRODUCAO'] == '')]
  
  st.header('Panorama geral de coproduções internacionais')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(horizontal=False):
        st.metric('Total de coproduções', total_coproducoes, border=True)
        st.metric('Coproduções com acordo formal' , f'{len(acordos_validos)} ({len(acordos_validos)/total_coproducoes*100:.1f}%)', border=True)
        st.metric('Coproduções sem acordo formal' , f'{len(acordos_vazios)} ({len(acordos_vazios)/total_coproducoes*100:.1f}%)', border=True)
        if (np.all([df_coproducoes['SITUACAO_OBRA'] == 'DEFERIDO'])):
          st.badge('Todas as obras deferidas', color='green', icon=':material/check:')
        else:
          indeferidos = df_coproducoes[df_coproducoes['SITUACAO_OBRA'] != 'DEFERIDO']
          st.badge(f'Há {len(indeferidos)} obras com situação `INDEFERIDO`', color='orange', icon=':material/warning:')
          st.dataframe(indeferidos)

    with col2:
      with st.container(border=True):
        df_participacao = (
          df_coproducoes.groupby('PART_PATRIMONIAL_BRASILEIRA')
            .agg(QTD=('CPB', 'count'))
            .reset_index()
        )
        plot_custom_pie_chart(
          df=df_participacao,
          color='PART_PATRIMONIAL_BRASILEIRA',
          theta='QTD',
          title='Distribuição da participação patrimonial brasileira',
        )
        st.caption(
          'Fatia de cada tipo de participação patrimonial brasileira nas coproduções: '
          'MAJORITÁRIA (273), MINORITÁRIA (237) e IGUALITÁRIA (47).'
        )
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large', border=True)
    
    with col1:
      df_acordos = (
        df_coproducoes.groupby('ACORDO_COPRODUCAO')
          .agg(
            QTD=('CPB', 'count'),
          )
          .reset_index()
          .sort_values('QTD', ascending=False)
      )
      df_acordos['PCT'] = (df_acordos['QTD'] * 100 / df_acordos['QTD'].sum()).map('{:.2f}'.format)
      
      df_acordos.rename(columns={
        'ACORDO_COPRODUCAO': 'Acordo de coprodução',
        'QTD': 'Quantidade',
        'PCT': 'Percentual (%)',
      }, inplace=True)
      
      plot_custom_ranking_bar_chart(
        df=df_acordos,
        x='Quantidade',
        x_title='Quantidade de obras',
        y='Acordo de coprodução',
        y_title=None,
        title='Obras por tipo de acordo de coprodução',
        tooltip=['Acordo de coprodução', 'Quantidade', 'Percentual (%)'],
        color='Quantidade',
        color_scheme='viridis',
        label_limit=260,
        step=30,
      )
      st.caption(
        'Ranking dos acordos de coprodução pelo número de obras cosiderando as que **possuem acordo formal**. O Acordo Latino-Americano lidera '
        '(144 obras, 41,5%), seguido do acordo com Portugal (77) e com a França (40).'
      )

    with col2:
      df_heat_acordo = (
        df_coproducoes.groupby(['PART_PATRIMONIAL_BRASILEIRA', 'ACORDO_COPRODUCAO'])
          .size()
          .rename('QTD')
          .reset_index()
      )
      plot_custom_heatmap(
        df=df_heat_acordo,
        x='ACORDO_COPRODUCAO',
        x_title=None,
        y='PART_PATRIMONIAL_BRASILEIRA',
        y_title='Participação brasileira',
        color='QTD',
        color_title='Nº de obras',
        title='Obras por participação patrimonial e acordo',
        color_scheme='viridis',
        log_color=True,
        tooltip=['PART_PATRIMONIAL_BRASILEIRA', 'ACORDO_COPRODUCAO', 'QTD'],
      )
      st.caption(
        'Heatmap do número de obras por participação patrimonial brasileira e **acordo formal** de '
        'coprodução. A cor usa escala logarítmica, já que poucos pares concentram muitos títulos '
        'e a maioria tem poucas obras. Combinações sem obras ficam em cinza.'
      )
  
  df_obras_coprod = pd.merge(
    df_coproducoes,
    df_obras,
    on='CPB',
    how='left'
  )

  st.subheader('Distribuição geográfica das obras em coprodução')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(border=True):
        df_uf_coprod = (
          df_obras_coprod.groupby('UF_REQUERENTE')['CPB']
            .count()
            .rename('QTD_OBRAS')
            .reset_index()
            .sort_values('QTD_OBRAS', ascending=False)
        )

        # Garante que todas as 27 UFs estejam presentes (estados sem coprodução ficam com 0),
        # evitando que o choropleth deixe estados em branco.
        with open("assets/brazil-states.geojson", "r") as _file:
          _ufs = [f['properties']['sigla'] for f in _json.load(_file)['features']]
        for _uf in _ufs:
          if _uf not in set(df_uf_coprod['UF_REQUERENTE']):
            df_uf_coprod = pd.concat([
              df_uf_coprod,
              pd.DataFrame([{'UF_REQUERENTE': _uf, 'QTD_OBRAS': 0}]),
            ], ignore_index=True)

        plot_custom_choropleth_brazil_map(
          df=df_uf_coprod,
          geojson_path='assets/brazil-states.geojson',
          uf_col='UF_REQUERENTE',
          value_col='QTD_OBRAS',
          value_title='Obras em coprodução',
          title='Obras em coprodução por estado',
          color_scheme='viridis',
        )

    with col2:
      with st.container(border=True):
        df_top10_mun = (
          df_obras_coprod.groupby('MUNICIPIO_REQUERENTE')['CPB']
            .count()                                                                    
            .rename('QTD_OBRAS')
            .reset_index()
            .sort_values('QTD_OBRAS', ascending=False)
            .head(10)
        )
        plot_custom_ranking_bar_chart(
          df=df_top10_mun,
          x='QTD_OBRAS',
          x_title='CPBs emitidos',
          y='MUNICIPIO_REQUERENTE',
          y_title=None,
          title='Top 10 municípios por CPBs emitidos em coprodução',
          tooltip=['MUNICIPIO_REQUERENTE', 'QTD_OBRAS'],
          color='QTD_OBRAS',
          color_scheme='viridis',
          label_limit=200,
          step=26,
        )

  with st.container(border=True):
    df_evolucao_coprod = (
      df_obras_coprod[df_obras_coprod['MUNICIPIO_REQUERENTE'].isin(df_top10_mun['MUNICIPIO_REQUERENTE'])]
        .groupby(['MUNICIPIO_REQUERENTE', 'ANO'])
        .size()
        .rename('QTD_OBRAS')
        .reset_index()
        .rename(columns={'MUNICIPIO_REQUERENTE': 'Município'})
    )
    plot_custom_grouped_line_chart(
      df=df_evolucao_coprod,
      x='ANO',
      x_title='Ano',
      y='QTD_OBRAS',
      y_title='CPBs emitidos',
      group='Município',
      group_title='Município',
      title='Evolução anual de CPBs emitidos (top 10 municípios)',
      color_scheme='dark2',
      height='520px',
      key='grouped_line_coprod_top10',
    )
    st.caption(
      'Obras em coprodução concentradas em São Paulo (240) e Rio de Janeiro (194). Os 10 '
      'principais municípios lideram a emissão de CPBs, e a evolução anual mostra o ritmo de '
      'formalização das coproduções ao longo do tempo.'
    )


  df_obras_coprod_sp = df_obras_coprod[df_obras_coprod['MUNICIPIO_REQUERENTE'] == 'SÃO PAULO']
  total_coproducoes_sp = len(df_obras_coprod_sp)
  acordos_validos_sp = df_obras_coprod_sp[df_obras_coprod_sp['ACORDO_COPRODUCAO'].notna() & (df_obras_coprod_sp['ACORDO_COPRODUCAO'] != '')]
  acordos_vazios_sp = df_obras_coprod_sp[df_obras_coprod_sp['ACORDO_COPRODUCAO'].isna() | (df_obras_coprod_sp['ACORDO_COPRODUCAO'] == '')]

  st.subheader('Distribuições das coproduções do município de São Paulo')
  with st.container(horizontal=True):
    st.metric('Total de coproduções', total_coproducoes_sp, border=True)
    st.metric('Coproduções com acordo formal' , f'{len(acordos_validos_sp)} ({len(acordos_validos_sp)/total_coproducoes_sp*100:.1f}%)', border=True)
    st.metric('Coproduções sem acordo formal' , f'{len(acordos_vazios_sp)} ({len(acordos_vazios_sp)/total_coproducoes_sp*100:.1f}%)', border=True)
    
  if (np.all([df_obras_coprod_sp['SITUACAO_OBRA_x'] == 'DEFERIDO'])):
    with st.container(horizontal=True, horizontal_alignment='right'):
      st.badge('Todas as obras deferidas', color='green', icon=':material/check:')
  else:
    with st.container(horizontal=True):  
      indeferidos = df_obras_coprod_sp[df_obras_coprod_sp['SITUACAO_OBRA_x'] != 'DEFERIDO']
      st.badge(f'Há {len(indeferidos)} obras com situação `INDEFERIDO`', color='orange', icon=':material/warning:')
      st.dataframe(indeferidos)

  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1], gap='large', border=True)
    
    with col1:
      df_heat_sp = (
        df_obras_coprod_sp
          .groupby(['PART_PATRIMONIAL_BRASILEIRA', 'ACORDO_COPRODUCAO'])
          .size()
          .rename('QTD')
          .reset_index()
      )
      plot_custom_heatmap(
        df=df_heat_sp,
        x='ACORDO_COPRODUCAO',
        x_title=None,
        y='PART_PATRIMONIAL_BRASILEIRA',
        y_title='Participação brasileira',
        color='QTD',
        color_title='Nº de obras',
        title='Obras por participação patrimonial e acordo (SP)',
        cell_size=30,
        color_scheme='viridis',
        log_color=True,
        tooltip=['PART_PATRIMONIAL_BRASILEIRA', 'ACORDO_COPRODUCAO', 'QTD'],
      )
      st.caption(
        'Heatmap do número de obras em coprodução com município requerente São Paulo, por '
        'participação patrimonial brasileira e tipo de acordo. A cor usa escala logarítmica, já '
        'que poucos pares concentram muitos títulos e a maioria tem poucas obras; combinações '
        'sem obras ficam em cinza.'
      )
    
    with col2:
      df_segmento_sp = (
        df_obras_coprod_sp
          .groupby('SEGMENTO_DESTINACAO_INICIAL')
          .agg(QTD=('CPB', 'count'))
          .reset_index()
          .sort_values('QTD', ascending=False)
      )
      plot_custom_ranking_bar_chart(
        df=df_segmento_sp,
        x='QTD',
        x_title='Quantidade de obras',
        y='SEGMENTO_DESTINACAO_INICIAL',
        y_title=None,
        title='Segmento de destinação inicial (SP)',
        tooltip=['SEGMENTO_DESTINACAO_INICIAL', 'QTD'],
        color='QTD',
        color_scheme='viridis',
        label_limit=260,
        step=24,
      )
      st.caption(
        'Ranking dos segmentos de destinação inicial das obras em coprodução com município '
        'requerente São Paulo, pelo número de obras.'
      )

  return