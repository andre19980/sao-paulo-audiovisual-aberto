import streamlit as st
import altair as alt
import pandas as pd
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
        capitais_brasileiras = [
          'RIO BRANCO', 'MACEIÓ', 'MACAPÁ', 'MANAUS', 'SALVADOR', 'FORTALEZA',
          'BRASÍLIA', 'VITÓRIA', 'GOIÂNIA', 'SÃO LUÍS', 'CUIABÁ', 'CAMPO GRANDE',
          'BELO HORIZONTE', 'BELÉM', 'JOÃO PESSOA', 'CURITIBA', 'RECIFE',
          'TERESINA', 'RIO DE JANEIRO', 'NATAL', 'PORTO ALEGRE', 'PORTO VELHO',
          'BOA VISTA', 'FLORIANÓPOLIS', 'SÃO PAULO', 'ARACAJU', 'PALMAS'
        ]

        df_capitais = df_media_salas_por_complexo_cidade[df_media_salas_por_complexo_cidade['Município'].isin(capitais_brasileiras)].copy()
        df_capitais['É a capital'] = df_capitais['Município'].eq('SÃO PAULO')
        df_capitais = df_capitais.sort_values('Média de salas por complexo')

        # Coordenadas (latitude, longitude) aproximadas de cada capital brasileira.
        coordenadas_capitais = {
          'RIO BRANCO': (-9.974, -67.806),
          'MACEIÓ': (-9.666, -35.735),
          'MACAPÁ': (0.035, -51.071),
          'MANAUS': (-3.116, -60.028),
          'SALVADOR': (-12.966, -38.501),
          'FORTALEZA': (-3.717, -38.543),
          'BRASÍLIA': (-15.794, -47.883),
          'VITÓRIA': (-20.315, -40.313),
          'GOIÂNIA': (-16.682, -49.251),
          'SÃO LUÍS': (-2.539, -44.286),
          'CUIABÁ': (-15.601, -56.098),
          'CAMPO GRANDE': (-20.470, -54.620),
          'BELO HORIZONTE': (-19.917, -43.935),
          'BELÉM': (-1.456, -48.504),
          'JOÃO PESSOA': (-7.115, -34.878),
          'CURITIBA': (-25.428, -49.273),
          'RECIFE': (-8.048, -34.877),
          'TERESINA': (-5.089, -42.802),
          'RIO DE JANEIRO': (-22.907, -43.173),
          'NATAL': (-5.794, -35.195),
          'PORTO ALEGRE': (-30.033, -51.230),
          'PORTO VELHO': (-8.761, -63.873),
          'BOA VISTA': (2.820, -60.673),
          'FLORIANÓPOLIS': (-27.596, -48.548),
          'SÃO PAULO': (-23.556, -46.640),
          'ARACAJU': (-10.947, -37.073),
          'PALMAS': (-10.212, -48.361),
        }

        uf_das_capitais = {
          'RIO BRANCO': 'AC', 'MACEIÓ': 'AL', 'MACAPÁ': 'AP', 'MANAUS': 'AM',
          'SALVADOR': 'BA', 'FORTALEZA': 'CE', 'BRASÍLIA': 'DF', 'VITÓRIA': 'ES',
          'GOIÂNIA': 'GO', 'SÃO LUÍS': 'MA', 'CUIABÁ': 'MT', 'CAMPO GRANDE': 'MS',
          'BELO HORIZONTE': 'MG', 'BELÉM': 'PA', 'JOÃO PESSOA': 'PB', 'CURITIBA': 'PR',
          'RECIFE': 'PE', 'TERESINA': 'PI', 'RIO DE JANEIRO': 'RJ', 'NATAL': 'RN',
          'PORTO ALEGRE': 'RS', 'PORTO VELHO': 'RO', 'BOA VISTA': 'RR',
          'FLORIANÓPOLIS': 'SC', 'SÃO PAULO': 'SP', 'ARACAJU': 'SE', 'PALMAS': 'TO',
        }

        # Anexa latitude, longitude e UF à tabela das capitais.
        df_capitais['Latitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][0])
        df_capitais['Longitude'] = df_capitais['Município'].map(lambda m: coordenadas_capitais[m][1])
        df_capitais['UF'] = df_capitais['Município'].map(uf_das_capitais)

        plot_custom_brazil_map(
          df=df_capitais,
          geojson_path='assets/brazil-states.geojson',
          label='Município',
          size='Número de complexos',
          size_title='Número de complexos',
          color='Média de salas por complexo',
          color_title='Média de salas por complexo',
          title='Média de salas por complexo e número de complexos nas capitais brasileiras (2026)',
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

  # Tabela de complexos de SP com quantidade de salas.
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

  # Fallback: complexos cujo CEP não está na base recebem o centro aproximado
  # do município de São Paulo, em vez de ficarem fora do mapa.
  n_fallback = df_complexos_sp_mapa['latitude'].isna().sum()
  df_complexos_sp_mapa['latitude'] = df_complexos_sp_mapa['latitude'].fillna(-23.5505)
  df_complexos_sp_mapa['longitude'] = df_complexos_sp_mapa['longitude'].fillna(-46.6333)
  if n_fallback:
    st.caption(f'{n_fallback} complexo(s) sem CEP na base receberam a localização aproximada do centro de São Paulo.')

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
          color='QUANTIDADE_DE_SALAS',
          color_title='Quantidade de salas',
          title='Distribuição da quantidade de salas por complexo no município de São Paulo (2026)',
          lat_col='latitude',
          lon_col='longitude',
          # Domínio fixo baseado no máximo de salas (sem filtro) para que a legenda
          # não colapse quando o filtro deixa só um valor de salas.
          color_scale_domain=[0, df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'].max()],
          size_scale_domain=[0, df_complexos_sp_mapa['QUANTIDADE_DE_SALAS'].max()],
        )
        st.caption(
          'Cada círculo é um complexo de cinema, posicionado pelas coordenadas aproximadas '
          'do seu CEP. O tamanho e a cor indicam o número de salas do complexo. Concentrações '
          'de círculos grandes mostram onde estão os cinemas multiprograma do município; '
          'o filtro "Porte do complexo" restringe o mapa às faixas escolhidas.'
        )

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
