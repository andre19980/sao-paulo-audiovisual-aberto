import streamlit as st
import altair as alt
import pandas as pd
import json

from lib.getters import uf_capitais_brasileiras
from lib.getters import capitais_brasileiras

from charts.bubble import plot_custom_bubble_chart
from charts.brazil_map import plot_custom_brazil_map
from charts.strip_jitter import plot_custom_strip_jitter_chart

def section(df_complexos_evolucao, df_salas_complexos):
  st.header('Densidade por complexos')

  df_complexos_abertos_2026 = df_complexos_evolucao[
    (df_complexos_evolucao['ANO'] == 2026) &
    (df_complexos_evolucao['STATUS'] == 'ABERTO')
  ]

  df_salas_complexos_aberto_2026 = df_salas_complexos[df_salas_complexos['REGISTRO_COMPLEXO'].isin(df_complexos_abertos_2026['REGISTRO_ANCINE'].unique())]
  df_salas_municipio_complexo = df_salas_complexos_aberto_2026.groupby(['MUNICIPIO_COMPLEXO', 'REGISTRO_COMPLEXO', 'CEP_COMPLEXO']).size().reset_index(name='QUANTIDADE_DE_SALAS')
  df_salas_municipio_complexo['MEDIA_DE_SALAS'] = df_salas_municipio_complexo['QUANTIDADE_DE_SALAS']
  df_media_salas_por_complexo_cidade = df_salas_municipio_complexo.groupby('MUNICIPIO_COMPLEXO').agg(
    {
      'QUANTIDADE_DE_SALAS': 'sum',
      'MEDIA_DE_SALAS': 'mean',
      'REGISTRO_COMPLEXO': 'count',
    })[['QUANTIDADE_DE_SALAS', 'MEDIA_DE_SALAS', 'REGISTRO_COMPLEXO']].sort_values(
      by='MEDIA_DE_SALAS',
      ascending=False
    ).reset_index()

  df_media_salas_por_complexo_cidade.rename(
    columns={
      'MUNICIPIO_COMPLEXO': 'Município',
      'MEDIA_DE_SALAS': 'Média de salas por complexo',
      'QUANTIDADE_DE_SALAS': 'Total de salas',
      'REGISTRO_COMPLEXO': 'Número de complexos'
    }, inplace=True)

  df_media_salas_por_complexo_cidade['Posição'] = df_media_salas_por_complexo_cidade.index + 1
  df_media_salas_por_complexo_cidade['Destaque'] = df_media_salas_por_complexo_cidade['Município'].eq('SÃO PAULO')

  st.subheader('Distribuição de salas e complexos por município')
  
  with st.container(border=True):
    plot_custom_bubble_chart(
      df=df_media_salas_por_complexo_cidade,
      x='Número de complexos',
      x_title='Número de complexos (escala log)',
      y='Média de salas por complexo',
      y_title='Média de salas por complexo',
      size='Total de salas',
      size_title='Total de salas',
      color='Destaque',
      color_title='São Paulo',
      title='Média de salas por complexo vs número de complexos por município',
      log_x=True,
      tooltip_fields=['Município', 'Número de complexos', 'Média de salas por complexo', 'Total de salas'],
    )
    st.caption(
      'Cada bolha é um município: o eixo X mostra quantos complexos existem (escala logarítmica), '
      'o eixo Y, a média de salas por complexo, e o tamanho da bolha, o total de salas do município. '
      'Um ponto no canto superior direito indica um município com muitos complexos e, em média, '
      'grandes multiprogramas por complexo; no canto inferior esquerdo, poucos complexos e salas '
      'menores. São Paulo é destacado em cor.'
    )
    
  st.subheader('Comparação da média de salas por complexo entre as capitais brasileiras')
  with st.container(horizontal=True, vertical_alignment='center', horizontal_alignment='center'):
    col1, col2 = st.columns([1, 1], gap='large')

    with col1:
      with st.container(border=True):
        lista_capitais = capitais_brasileiras()
        df_capitais = df_media_salas_por_complexo_cidade[df_media_salas_por_complexo_cidade['Município'].isin(lista_capitais)].copy()
        df_capitais['É a capital'] = df_capitais['Município'].eq('SÃO PAULO')
        df_capitais = df_capitais.sort_values('Média de salas por complexo')

        # Coordenadas (latitude, longitude) aproximadas de cada capital brasileira.
        with open("assets/coordenadas-capitais.json", "r") as file:
          coordenadas_capitais = json.load(file)

        dict_uf_capitais = uf_capitais_brasileiras()

        # Anexa latitude, longitude e UF à tabela das capitais.
        df_capitais['Latitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][0])
        df_capitais['Longitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][1])
        df_capitais['UF'] = df_capitais['Município'].map(dict_uf_capitais)

        plot_custom_brazil_map(
          df=df_capitais,
          geojson_path='assets/brazil-states.geojson',
          label='Município',
          size='Número de complexos',
          size_title='Número de complexos',
          color='Média de salas por complexo',
          color_title='Média de salas por complexo',
          title='Média de salas por complexo e número de complexos nas capitais brasileiras (2026)',
          tooltip_fields=['Município', 'UF', 'Média de salas por complexo', 'Número de complexos'],
        )
        st.caption(
          'Cada bolha é uma capital: o tamanho representa o número de complexos de cinema '
          'e a cor, a média de salas por complexo da cidade. São Paulo se destaca pelo volume '
          'de complexos, mas capitais com médias altas (bolhas escuras) concentram a maior '
          'parte das salas em poucos complexos.'
        )
      
      with col2:
        st.dataframe(
          df_capitais[['Município', 'Média de salas por complexo', 'Número de complexos', 'Total de salas']],
          hide_index=True,
          width='stretch',
          height='stretch',
        )


  st.space(size='medium')

  df_salas_por_complexo_sp = df_salas_municipio_complexo[df_salas_municipio_complexo['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
  df_salas_por_complexo_sp.sort_values(by='QUANTIDADE_DE_SALAS', ascending=False, inplace=True)

  # ---------------------------------------------------------------------------
  # Mapa de São Paulo: distribuição da quantidade de salas por complexo.
  #
  # Abordagem: os dados da ANCINE não trazem coordenadas, apenas endereço/CEP.
  # Para priorizar performance (e como não é necessária grande precisão),
  # usamos a aproximação pelo CEP: cada complexo recebe as coordenadas do
  # centróide do seu CEP, carregadas de um asset local (assets/cep_sp_coordenadas.csv).
  # ---------------------------------------------------------------------------
  df_cep_sp = pd.read_csv('assets/cep_sp_coordenadas.csv', dtype={'cep': str})

  df_complexos_sp_mapa = (
    df_salas_por_complexo_sp
      .reset_index()
      .merge(
        df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
          [['REGISTRO_COMPLEXO', 'NOME_COMPLEXO', 'BAIRRO_COMPLEXO']]
          .drop_duplicates(subset='REGISTRO_COMPLEXO'),
        on='REGISTRO_COMPLEXO',
        how='left',
      )
  )

  # Normaliza o CEP (remove hífen) e faz o join com as coordenadas.
  df_complexos_sp_mapa['CEP'] = df_complexos_sp_mapa['CEP_COMPLEXO'].astype(str).str.replace('-', '', regex=False)
  df_complexos_sp_mapa = df_complexos_sp_mapa.merge(df_cep_sp, left_on='CEP', right_on='cep', how='left')

  # Complexos cujo CEP não está na base ficam de fora do mapa.
  n_sem_cep = df_complexos_sp_mapa['latitude'].isna().sum()
  df_complexos_sp_mapa = df_complexos_sp_mapa.dropna(subset=['latitude', 'longitude'])

  # Marca os complexos que são unidades do circuito Spcine, para destaque no mapa.
  with open('assets/spcine-unidades.json', 'r', encoding='utf-8') as file:
    spcine_unidades = json.load(file)
  spcine_complexos = {u['complexo_ancine'] for u in spcine_unidades}
  df_complexos_sp_mapa['Rede Spcine'] = df_complexos_sp_mapa['NOME_COMPLEXO'].map(
    lambda nome: 'Spcine' if nome in spcine_complexos else 'Demais'
  )
  # Unidades Spcine opacas; demais com transparência.
  df_complexos_sp_mapa['Opacidade'] = df_complexos_sp_mapa['Rede Spcine'].map(
    {'Spcine': 1.0, 'Demais': 0.4}
  )

  porte_faixas = [1, 2, 3, 10, 100]  # limites: 1, [2-3], [4-9], [10+]
  porte_rotulos = ['1 sala', 'Pequeno (2-3)', 'Médio (4-9)', 'Megaplex (10+)']
  df_complexos_sp_mapa['Porte'] = pd.cut(
    df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'],
    bins=porte_faixas,
    labels=porte_rotulos,
    include_lowest=True,
  )

  st.subheader('Distribuição de complexos por porte no município de São Paulo')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col2:
      with st.container(border=True):
        portes_selecionados = st.segmented_control(
          "Porte do complexo",
          options=porte_rotulos,
          selection_mode="multi"
        )
        
        if portes_selecionados:
          df_complexos_sp_filtrado = df_complexos_sp_mapa[df_complexos_sp_mapa['Porte'].isin(portes_selecionados)]
        else:
          df_complexos_sp_filtrado = df_complexos_sp_mapa

        plot_custom_brazil_map(
          df=df_complexos_sp_filtrado,
          geojson_path='assets/sp-municipio.geojson',
          label='NOME_COMPLEXO',
          size='QUANTIDADE_DE_SALAS',
          size_title='Quantidade de salas',
          color='Rede Spcine',
          color_title='Rede',
          title='Distribuição da quantidade de salas por complexo no município de São Paulo (2026)',
          lat_col='latitude',
          lon_col='longitude',
          color_type='N',
          color_scheme=['#3b82f6', '#f59e0b'],
          opacity_col='Opacidade',
          size_scale_domain=[0, df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'].max()],
          tooltip_fields=['NOME_COMPLEXO', 'Rede Spcine', 'QUANTIDADE_DE_SALAS'],
        )
        st.caption(
          'Cada círculo é um complexo de cinema, posicionado pelas coordenadas aproximadas '
          'do seu CEP. O tamanho indica o número de salas do complexo e a cor identifica se a '
          'unidade faz parte do circuito Spcine (laranja, opaco) ou não (azul, translúcido). '
          'Concentrações de círculos grandes mostram onde estão os cinemas multiprograma do '
          'município; o filtro "Porte do complexo" restringe o mapa às faixas escolhidas.'
        )
        if n_sem_cep:
          st.caption(f'{n_sem_cep} complexo(s) sem CEP na base não aparecem no mapa.')

    with col1:
      st.dataframe(
        df_complexos_sp_filtrado[[
          'NOME_COMPLEXO',
          'BAIRRO_COMPLEXO',
          'QUANTIDADE_DE_SALAS',
        ]].rename(columns={
          'NOME_COMPLEXO': 'Nome do complexo',
          'BAIRRO_COMPLEXO': 'Bairro',
          'QUANTIDADE_DE_SALAS': 'Quantidade de Salas',
        }),
        hide_index=True,
        width='stretch',
        height='stretch',
      )

  st.space(size='medium')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(border=True):
        plot_custom_strip_jitter_chart(
          df=df_complexos_sp_mapa,
          y='QUANTIDADE_DE_SALAS',
          y_title='Quantidade de salas',
          x=None,
          x_title=None,
          color='Porte',
          color_title='Porte do complexo',
          title='Distribuição dos complexos por porte e quantidade de salas no município de São Paulo (2026)',
          tooltip_fields=['NOME_COMPLEXO', 'BAIRRO_COMPLEXO', 'QUANTIDADE_DE_SALAS']
        )
        st.caption('Pontos com mesmo número de salas foram levemente espalhados no eixo X (jitter) apenas para evitar sobreposição. Passe o mouse para ver o nome, bairro e nº de salas de cada complexo.')
        
    with col2:
      df_contagem_porte = (
        df_complexos_sp_mapa['Porte']
          .value_counts()
          .reindex(porte_rotulos, fill_value=0)
          .reset_index()
          .rename(columns={'index': 'Porte', 'count': 'Quantidade de complexos'})
      )

      bar_chart_portes = (
        alt.Chart(df_contagem_porte)
          .mark_bar(cornerRadiusEnd=3)
          .encode(
            x=alt.X('Porte:N', title='Porte do complexo', sort=None),
            y=alt.Y('Quantidade de complexos:Q', title='Quantidade de complexos'),
            color=alt.Color('Porte:N', title='Porte do complexo'),
            tooltip=['Porte', 'Quantidade de complexos'],
          )
          .properties(
            height=480,
            title=alt.TitleParams(
              text='Quantidade de complexos por porte no município de São Paulo (2026)',
              anchor='start',
            ),
          )
      )
      
      with st.container(border=True, height='stretch'):
        st.altair_chart(bar_chart_portes)
