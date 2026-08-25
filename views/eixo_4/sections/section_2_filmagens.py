import streamlit as st
import pandas as pd
import numpy as np

from charts.pie import plot_custom_pie_chart
from charts.bar import plot_custom_ranking_bar_chart

def section(df_filmagens, df_obras):
  st.header('Panorama geral de filmagens estrangeiras no Brasil')
  
  total_filmagens = len(df_filmagens)
  total_paises = len(df_filmagens[(df_filmagens['PAIS'] != 'Sem informação') & (df_filmagens['PAIS'] != 'Não é país')]['PAIS'].unique())
  total_tecnicos_artistas = pd.to_numeric(df_filmagens['NR_TECNICOS_ARTISTAS_ESTRANGEIROS'], errors='coerce').sum()
  
  with st.container(horizontal=True):
    st.metric('Total de filmagens', total_filmagens, border=True)
    st.metric('Total de países', total_paises, border=True)
    st.metric('Total de técnicos/artistas estrangeiros', f'{total_tecnicos_artistas:.0f}', border=True)
  
  
  st.subheader('Distribuição das filmagens por tipo')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1], gap='large', border=True)
    
    df_tipo_filmagem = df_filmagens['TIPO_OBRA'].value_counts().reset_index().rename(columns={
      'TIPO_OBRA': 'Tipo de obra',
      'count': 'Quantidade'
    })

    with col1:
      st.markdown('**Tabela de quantidade de filmagens estrangeiras por tipo**')
      st.table(df_tipo_filmagem, border='horizontal', height=380, hide_index=True)
      
    with col2:
      top9 = df_tipo_filmagem.head(9).copy()
      resto = df_tipo_filmagem.iloc[9:]['Quantidade'].sum()
      if resto > 0:
        top9 = pd.concat([
          top9,
          pd.DataFrame([{'Tipo de obra': 'Outros', 'Quantidade': resto}]),
        ], ignore_index=True)
      plot_custom_pie_chart(
        df=top9,
        color='Tipo de obra',
        theta='Quantidade',
        title='Quantidade de filmagens estrangeiras por tipo',
        color_scheme='category10',
      )
      st.caption(
        'Fatia de cada tipo de obra estrangeira filmada. Os 9 tipos mais frequentes aparecem '
        'individualizados; os demais são agrupados em "Outros".'
      )
    
  st.subheader('Distribuição das filmagens por países')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1], gap='large', border=True)

    df_pais_filmagem = df_filmagens['PAIS'].value_counts().reset_index().rename(columns={
      'PAIS': 'País',
      'count': 'Quantidade'
    })
      
    with col1:
      st.markdown('**Tabela de quantidade de filmagens por país**')
      st.table(df_pais_filmagem, border='horizontal', height=520, hide_index=True)
      
    with col2:
      plot_custom_ranking_bar_chart(
        df=df_pais_filmagem.head(15),
        x='Quantidade',
        x_title='Número de filmagens',
        y='País',
        y_title=None,
        title='Top 15 países por número de filmagens',
        tooltip=['País', 'Quantidade'],
        color='Quantidade',
        color_scheme='viridis',
        label_limit=200,
        step=26,
      )
      st.caption(
        'Ranking dos 15 países com maior número de filmagens estrangeiras registradas no '
        'Brasil.'
      )

  st.subheader('Técnicos e artistas estrangeiros')
  df_filmagens['TEC'] = pd.to_numeric(df_filmagens['NR_TECNICOS_ARTISTAS_ESTRANGEIROS'], errors='coerce')
  media_tec = df_filmagens['TEC'].mean()
  max_tec = df_filmagens['TEC'].max()

  with st.container(horizontal=True):
    st.metric('Média de técnicos/artistas por filmagem', f'{media_tec:.1f}', border=True)
    st.metric('Máximo de técnicos/artistas em uma filmagem', f'{max_tec:.0f}', border=True)

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1])

    df_pais_tec = (
      df_filmagens.groupby('PAIS')['TEC']
        .sum()
        .reset_index()
        .rename(columns={'PAIS': 'País', 'TEC': 'Total de técnicos'})
        .sort_values('Total de técnicos', ascending=False)
    )

    with col1:
      with st.container(border=True):
        plot_custom_ranking_bar_chart(
          df=df_pais_tec.head(10),
          x='Total de técnicos',
          x_title='Total de técnicos/artistas',
          y='País',
          y_title=None,
          title='Top 10 países por total de técnicos/artistas',
          tooltip=['País', 'Total de técnicos'],
          color='Total de técnicos',
          color_scheme='viridis',
          label_limit=200,
          step=26,
        )
        st.caption(
          'Países de origem que mais enviaram técnicos e artistas para filmagens no Brasil.'
        )

    df_top_obras_tec = (
      df_filmagens.nlargest(5, 'TEC')[['TITULO_OBRA', 'PAIS', 'TEC']]
        .copy()
        .rename(columns={'TITULO_OBRA': 'Obra', 'PAIS': 'País', 'TEC': 'Técnicos/artistas'})
    )
    df_top_obras_tec['Técnicos/artistas'] = df_top_obras_tec['Técnicos/artistas'].astype(int)

    with col2:
      with st.container(border=True):
        st.markdown('**As 5 obras com mais técnicos/artistas estrangeiros**')
        st.table(df_top_obras_tec, hide_index=True, border='horizontal')

  return