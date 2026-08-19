import pandas as pd
import streamlit as st

from charts.heatmap import plot_custom_heatmap
from charts.bar import plot_custom_layered_bar_chart, plot_custom_ranking_bar_chart
from charts.pie import plot_custom_pie_chart
from charts.line import plot_custom_grouped_line_chart
from charts.bar import plot_custom_stacked_horizontal_bar_echarts

@st.cache_data(scope='session')
def gera_segmento_municipio(df):
  return df.groupby([
      'UF_REQUERENTE',
      'MUNICIPIO_REQUERENTE',
      'SEGMENTO_DESTINACAO_INICIAL'
    ]).agg({
      'CPB': 'count',
    }).rename(columns={'CPB': 'QTD_OBRAS'}).reset_index().sort_values('QTD_OBRAS', ascending=False)

def section(df_obras):
  df_br_ano = df_obras.groupby('ANO').agg(QTD_OBRAS=('CPB', 'count')).reset_index()
  df_br_ano['Escopo'] = 'Brasil'

  top10_cidades_evolucao = (
    df_obras.groupby('MUNICIPIO_REQUERENTE')['CPB']
      .count()
      .sort_values(ascending=False)
      .head(10)
      .index
      .tolist()
  )
  df_cidades_ano = (
    df_obras[df_obras['MUNICIPIO_REQUERENTE'].isin(top10_cidades_evolucao)]
      .groupby(['MUNICIPIO_REQUERENTE', 'ANO'])
      .size()
      .rename('QTD_OBRAS')
      .reset_index()
  )
  df_cidades_ano = df_cidades_ano.rename(columns={'MUNICIPIO_REQUERENTE': 'Escopo'})
  df_evolucao = pd.concat([df_br_ano, df_cidades_ano], ignore_index=True)

  df_segmento_municipio = gera_segmento_municipio(df_obras)
  
  st.header('Evolução e segmentação por localidade das obras')
  with st.container(horizontal=True):
    col1, col2 = st.columns([2, 1], border=True)
    
    with col1:
      plot_custom_grouped_line_chart(
        df=df_evolucao,
        x='ANO',
        x_title='Ano',
        y='QTD_OBRAS',
        y_title='Número de obras (CPBs)',
        group='Escopo',
        group_title='Localidade',
        title='Evolução anual do número de obras',
        color_scheme='dark2',
        height='500px',
        key='grouped_line_evolucao',
      )
      st.caption(
        'Quantidade de obras (CPBs) registradas na ANCINE por ano. A linha "Brasil" mostra o '
        'total nacional; as demais linhas acompanham a evolução das 10 cidades com mais obras. '
        'RIO DE JANEIRO e SÃO PAULO concentram a maior parte da produção e crescem junto com o '
        'total nacional.'
      )
        
    with col2:
      df_top10 = (
        df_segmento_municipio
          .groupby('MUNICIPIO_REQUERENTE')['QTD_OBRAS']
          .sum()
          .sort_values(ascending=False)
          .head(10)
      )
      top10_cidades = df_top10.index.tolist()
    
      plot_custom_ranking_bar_chart(
        df=df_top10.reset_index(),
        x='QTD_OBRAS',
        x_title='Quantidade de obras',
        y='MUNICIPIO_REQUERENTE',
        y_title=None,
        title='As 10 cidades com mais obras',
        tooltip=['MUNICIPIO_REQUERENTE', 'QTD_OBRAS'],
        color='QTD_OBRAS',
        color_scheme='lightmulti',
        label_limit=220,
        step=34,
      )
      st.caption(
        'Ranking das 10 cidades com maior número de obras registradas na ANCINE. RIO DE JANEIRO '
        '(19.641) e SÃO PAULO (18.492) lideram com folga, seguidas por PORTO ALEGRE e BELO '
        'HORIZONTE.'
      )

  with st.container(border=True):
    df_heat = (
      df_segmento_municipio[df_segmento_municipio['MUNICIPIO_REQUERENTE'].isin(top10_cidades)]
        .pivot_table(
          index='MUNICIPIO_REQUERENTE',
          columns='SEGMENTO_DESTINACAO_INICIAL',
          values='QTD_OBRAS',
          aggfunc='sum',
          fill_value=0,
        )
        .stack()
        .rename('QTD_OBRAS')
        .reset_index()
    )
  
    df_heat['QTD_OBRAS'] = df_heat['QTD_OBRAS'].replace(0, None)
  
    plot_custom_heatmap(
      df=df_heat,
      x='SEGMENTO_DESTINACAO_INICIAL',
      x_title=None,
      y='MUNICIPIO_REQUERENTE',
      y_title='Município',
      color='QTD_OBRAS',
      color_title='Nº de obras',
      title='Top 10 cidades: quantidade de obras vs. segmento',
      cell_size=20,
      color_scheme='lightmulti',
      log_color=True,
      invalid_color='#e0e0e0',
    )
    st.caption(
      'Heatmap do número de obras registradas na ANCINE para as 10 cidades com maior produção, '
      'por segmento de destinação inicial. A cor usa escala logarítmica (SP e RJ dominam) e '
      'células em cinza indicam combinações sem obras. RIO DE JANEIRO e SÃO PAULO concentram a '
      'produção em todos os segmentos, sobretudo TV por assinatura, salas de exibição e '
      'segmentos indefinidos.'
    )

  st.header('Distribuição de obras por tipo e segmento')
  df_sp = df_obras[df_obras['MUNICIPIO_REQUERENTE'] == 'SÃO PAULO']

  df_segmentos = df_segmento_municipio.groupby('SEGMENTO_DESTINACAO_INICIAL').agg(QTD_OBRAS=('QTD_OBRAS', 'sum')).reset_index().sort_values('QTD_OBRAS', ascending=False)
  df_sp_segmento = df_segmento_municipio[df_segmento_municipio['MUNICIPIO_REQUERENTE'] == 'SÃO PAULO'].groupby('SEGMENTO_DESTINACAO_INICIAL').agg(QTD_OBRAS=('QTD_OBRAS', 'sum')).reset_index()
  df_sp_segmento['Escopo'] = 'São Paulo'
  df_segmentos['Escopo'] = 'Brasil'
  df_layered = pd.concat([df_segmentos, df_sp_segmento], ignore_index=True)
  df_layered['QTD_OBRAS_BR'] = df_layered['SEGMENTO_DESTINACAO_INICIAL'].map(
    df_segmentos.set_index('SEGMENTO_DESTINACAO_INICIAL')['QTD_OBRAS']
  )
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
      with st.container(border=True):
        plot_custom_layered_bar_chart(
          df=df_layered,
          x='QTD_OBRAS',
          x_title='Quantidade de obras',
          y='SEGMENTO_DESTINACAO_INICIAL',
          y_title=None,
          color='Escopo',
          color_title=None,
          title='Obras por segmento de destinação inicial: Brasil vs São Paulo',
          sort_by='QTD_OBRAS_BR',
          color_scheme='dark2',
          label_limit=220,
        )
        st.caption(
          'Duas barras sobrepostas por segmento: a de fundo (Brasil) mostra o total de obras '
          'registradas na ANCINE e a de frente (São Paulo), quantas tiveram proponente paulistano. '
          'SP responde por cerca de um terço das obras em segmentos como TV por assinatura (33%) e '
          'salas de exibição (28%), e menos nos segmentos menores.'
        )

    with col2:
      df_tipo_sp = (
        df_sp.groupby('TIPO_OBRA')
          .agg(QTD_OBRAS=('CPB', 'count'))
          .reset_index()
          .sort_values('QTD_OBRAS', ascending=False)
        )
      
      with st.container(border=True):
        plot_custom_pie_chart(
          df=df_tipo_sp,
          color='TIPO_OBRA',
          theta='QTD_OBRAS',
          title='Distribuição por tipo de obra (SP)',
          inner_radius=50,
          outer_radius=120,
          color_scheme='category20'
        )
        st.caption(
          'Fatia de cada tipo de obra no total de obras com proponente em São Paulo. FICÇÃO lidera, '
          'seguida de VÍDEOMUSICAL e DOCUMENTÁRIO.'
        )

  with st.container(border=True):
    seg_top = df_sp['SEGMENTO_DESTINACAO_INICIAL'].value_counts().head(8).index.tolist()
    tipo_top = df_sp['TIPO_OBRA'].value_counts().head(6).index.tolist()
    df_seg_tipo = (
      df_sp[
        df_sp['SEGMENTO_DESTINACAO_INICIAL'].isin(seg_top)
        & df_sp['TIPO_OBRA'].isin(tipo_top)
        # Desconsidera obras sem segmento definido ou sem tipo classificado.
        & (df_sp['SEGMENTO_DESTINACAO_INICIAL'] != 'INDEFINIDO')
        & (df_sp['TIPO_OBRA'] != 'NÃO CLASSIFICADA')
      ]
        .groupby(['SEGMENTO_DESTINACAO_INICIAL', 'TIPO_OBRA'])
        .size()
        .rename('QTD_OBRAS')
        .reset_index()
    )

    plot_custom_stacked_horizontal_bar_echarts(
      df=df_seg_tipo,
      y='SEGMENTO_DESTINACAO_INICIAL',
      x='QTD_OBRAS',
      series='TIPO_OBRA',
      series_title='Tipo de obra',
      title='Composição por tipo de obra em cada segmento (SP)',
      color_scheme='category',
      height='520px',
      key='stacked_hbar_seg_tipo_sp',
    )
    st.caption(
      'Barras horizontais empilhadas (normalizadas em 100%) mostrando a composição por tipo de '
      'obra dentro de cada segmento de destinação em São Paulo.'
      'Clique nos itens da legenda para ocultar/exibir séries.'
    )

  return
