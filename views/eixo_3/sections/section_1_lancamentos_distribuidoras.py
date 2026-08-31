import streamlit as st
import pandas as pd

from lib.normalizers import converte_moeda, normaliza_municipio
from charts.bar import plot_custom_grouped_bar_chart, plot_custom_ranking_bar_chart
from charts.bubble import plot_custom_bubble_chart
from charts.pie import plot_custom_pie_chart


def section(df_lancamentos, df_obras):
  st.header('Panorama de lançamentos comerciais por distribuidoras')

  df_lancamentos['RENDA_TOTAL'] = df_lancamentos['RENDA_TOTAL'].apply(converte_moeda)
  df_lancamentos_br = df_lancamentos[df_lancamentos['PAIS_OBRA'] == 'BRASIL']
  df_lancamentos_es = df_lancamentos[df_lancamentos['PAIS_OBRA'] != 'BRASIL']

  total_obras = df_lancamentos['CPB_ROE'].nunique()
  total_obras_br = df_lancamentos[df_lancamentos['PAIS_OBRA'] == 'BRASIL']['CPB_ROE'].nunique()
  total_obras_es = df_lancamentos[df_lancamentos['PAIS_OBRA'] != 'BRASIL']['CPB_ROE'].nunique()
  total_publico = df_lancamentos['PUBLICO_TOTAL'].sum()
  total_publico_br = df_lancamentos_br['PUBLICO_TOTAL'].sum()
  total_publico_es = df_lancamentos_es['PUBLICO_TOTAL'].sum()
  total_renda = df_lancamentos['RENDA_TOTAL'].sum()
  total_renda_br = df_lancamentos_br['RENDA_TOTAL'].sum()
  total_renda_es = df_lancamentos_es['RENDA_TOTAL'].sum()
  total_distribuidoras = df_lancamentos['REGISTRO_DISTRIBUIDORA'].nunique()

  with st.container(horizontal=True):
    col1, col2 = st.columns(2)
    
    with col1:
      st.metric('Total de obras', f'{total_obras:,}', border=True)
      st.metric('Total de público', f'{total_publico:,}', border=True)
      st.metric('Total de renda', f'R$ {total_renda:,.0f}', border=True)
      st.metric('Total de distribuidoras', f'{total_distribuidoras:,}', border=True)
      
    with col2:
      with st.container(border=True, height='stretch'):
        metrica = st.segmented_control(
          'Métrica por nacionalidade',
          options=['Obras', 'Público', 'Renda'],
          selection_mode='single',
          default='Obras',
        )

        pie_data = {
          'Obras': {'Nacionais': total_obras_br, 'Estrangeiros': total_obras_es},
          'Público': {'Nacionais': total_publico_br, 'Estrangeiros': total_publico_es},
          'Renda': {'Nacionais': total_renda_br, 'Estrangeiros': total_renda_es},
        }[metrica]

        df_pie = pd.DataFrame({
          'Tipo': list(pie_data.keys()),
          'QTD': list(pie_data.values()),
        })
        plot_custom_pie_chart(
          df=df_pie,
          color='Tipo',
          theta='QTD',
          title=f'{metrica} por nacionalidade',
          color_scheme='category10',
        )

  st.subheader('Distribuição por tipo de obra')
  df_tipo = (
    df_lancamentos.groupby('TIPO_OBRA')
      .agg(QTD=('CPB_ROE', 'nunique'), Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
      .reset_index()
      .sort_values('QTD', ascending=False)
  )
  with st.container(border=True):
    plot_custom_bubble_chart(
      df=df_tipo,
      x='QTD',
      x_title='Nº de obras',
      y='Público',
      y_title='Público total',
      size='Renda',
      size_title='Renda total (R$)',
      color='TIPO_OBRA',
      color_title='Tipo de obra',
      title='Lançamentos por tipo de obra',
      tooltip_fields=['TIPO_OBRA', 'QTD', 'Público', 'Renda'],
      log_x=True,
      height=480
    )
    st.caption('Cada bolinha representa um tipo de obra: o eixo X mostra o número de obras lançadas, o eixo Y o público total acumulado e o tamanho da bolinha o total de renda gerada.')

  st.subheader('Filmes com maiores quantidades de público')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], border=True, gap='large')
    
    with col1:
      df_br_filmes = (
        df_lancamentos[df_lancamentos['PAIS_OBRA'] == 'BRASIL']
          .groupby(['CPB_ROE', 'TITULO_ORIGINAL'])
          .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
          .reset_index()
          .sort_values('Público', ascending=False)
      )
      plot_custom_ranking_bar_chart(
        df=df_br_filmes.head(10),
        x='Público',
        x_title='Público total',
        y='TITULO_ORIGINAL',
        y_title=None,
        title='Top 10 filmes brasileiros por público',
        tooltip=['TITULO_ORIGINAL', 'Público', 'Renda'],
        color='Público',
        color_scheme='viridis',
        label_limit=280,
        step=26,
      )

    with col2:
      df_estrangeiros_filmes = (
        df_lancamentos[df_lancamentos['PAIS_OBRA'] != 'BRASIL']
          .groupby(['CPB_ROE', 'TITULO_ORIGINAL', 'PAIS_OBRA'])
          .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
          .reset_index()
          .sort_values('Público', ascending=False)
      )
      plot_custom_ranking_bar_chart(
        df=df_estrangeiros_filmes.head(10),
        x='Público',
        x_title='Público total',
        y='TITULO_ORIGINAL',
        y_title=None,
        title='Top 10 filmes estrangeiros por público',
        tooltip=['TITULO_ORIGINAL', 'PAIS_OBRA', 'Público', 'Renda'],
        color='Público',
        color_scheme='viridis',
        label_limit=280,
        step=26,
      )

  st.subheader('Países e distribuidoras em destaque')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large', border=True)
    
    with col1:
      df_pais_publico = (
        df_lancamentos.groupby('PAIS_OBRA')
          .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
          .reset_index()
          .sort_values('Público', ascending=False)
      )
      plot_custom_ranking_bar_chart(
        df=df_pais_publico.head(10),
        x='Público',
        x_title='Público total',
        y='PAIS_OBRA',
        y_title=None,
        title='Top 10 países por público',
        tooltip=['PAIS_OBRA', 'Público', 'Renda'],
        color='Público',
        color_scheme='viridis',
        label_limit=240,
        step=26,
      )

    with col2: 
      df_dist_publico = (
        df_lancamentos.groupby('RAZAO_SOCIAL_DISTRIBUIDORA')
          .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
          .reset_index()
          .sort_values('Público', ascending=False)
      )
      plot_custom_ranking_bar_chart(
        df=df_dist_publico.head(10),
        x='Público',
        x_title='Público total',
        y='RAZAO_SOCIAL_DISTRIBUIDORA',
        y_title=None,
        title='Top 10 distribuidoras por público',
        tooltip=['RAZAO_SOCIAL_DISTRIBUIDORA', 'Público', 'Renda'],
        color='Público',
        color_scheme='viridis',
        label_limit=280,
        step=26,
      )

  st.subheader('Evolução de obras e público por ano de lançamento')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large', border=True)
    
    with col1:
      df_ano = (
        df_lancamentos.assign(
          ANO_LANCAMENTO=pd.to_datetime(df_lancamentos['DATA_LANCAMENTO_OBRA'], format='%d/%m/%Y', errors='coerce').dt.year,
          NACIONALIDADE=df_lancamentos['PAIS_OBRA'].apply(lambda pais: 'Brasil' if pais == 'BRASIL' else 'Estrangeiro'),
        )
        .groupby(['ANO_LANCAMENTO', 'NACIONALIDADE'])
        .agg(QTD=('CPB_ROE', 'nunique'))
        .reset_index()
        .dropna(subset=['ANO_LANCAMENTO'])
      )
      plot_custom_grouped_bar_chart(
        df=df_ano,
        x='ANO_LANCAMENTO',
        x_title='Ano de lançamento',
        y='QTD',
        y_title='Nº de obras',
        x_offset='NACIONALIDADE',
        x_offset_title='',
        title='Obras lançadas por ano e nacionalidade',
        x_scale_sort=df_ano['ANO_LANCAMENTO'].drop_duplicates().sort_values().astype(str).tolist(),
      )

  with col2:
    df_ano_publico = (
      df_lancamentos.assign(
        ANO_LANCAMENTO=pd.to_datetime(df_lancamentos['DATA_LANCAMENTO_OBRA'], format='%d/%m/%Y', errors='coerce').dt.year,
        NACIONALIDADE=df_lancamentos['PAIS_OBRA'].apply(lambda pais: 'Brasil' if pais == 'BRASIL' else 'Estrangeiro'),
      )
      .groupby(['ANO_LANCAMENTO', 'NACIONALIDADE'])
      .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
      .reset_index()
      .dropna(subset=['ANO_LANCAMENTO'])
    )
    plot_custom_grouped_bar_chart(
      df=df_ano_publico,
      x='ANO_LANCAMENTO',
      x_title='Ano de lançamento',
      y='Público',
      y_title='Público total',
      x_offset='NACIONALIDADE',
      x_offset_title='',
      title='Público por ano de lançamento e nacionalidade',
      x_scale_sort=df_ano_publico['ANO_LANCAMENTO'].drop_duplicates().sort_values().astype(str).tolist(),
      tooltip=['ANO_LANCAMENTO', 'NACIONALIDADE', 'Público', 'Renda'],
    )

  st.header('Análise de lançamentos por localidade')
  df_obras_sp = df_obras.assign(
    CPB=df_obras['CPB'].astype(str).str.strip(),
    MUNICIPIO_REQUERENTE_NORM=df_obras['MUNICIPIO_REQUERENTE'].apply(normaliza_municipio),
    MUN_SP=df_obras['MUNICIPIO_REQUERENTE'].apply(normaliza_municipio) == 'SAO PAULO',
  )
  df_sp = (
    df_lancamentos.assign(CPB=df_lancamentos['CPB_ROE'].astype(str).str.strip())
    .merge(df_obras_sp[['CPB', 'MUN_SP', 'MUNICIPIO_REQUERENTE_NORM']], on='CPB', how='left')
  )
  df_sp['MUN_SP'] = df_sp['MUN_SP'].fillna(False)
  df_sp_br = df_sp[df_sp['PAIS_OBRA'] == 'BRASIL']

  st.subheader('Municípios requerentes: obras, público e renda')
  with st.container(border=True):
    df_municipio = (
      df_sp_br[df_sp_br['MUNICIPIO_REQUERENTE_NORM'].notna()]
        .groupby('MUNICIPIO_REQUERENTE_NORM')
        .agg(QTD=('CPB', 'nunique'), Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
        .reset_index()
        .rename(columns={'MUNICIPIO_REQUERENTE_NORM': 'Município'})
        .sort_values('QTD', ascending=False)
    )
    plot_custom_bubble_chart(
      df=df_municipio,
      x='QTD',
      x_title='Nº de obras',
      y='Público',
      y_title='Público total',
      size='Renda',
      size_title='Renda total (R$)',
      color='Município',
      color_title='Município',
      title='Obras, público e renda por município requerente',
      tooltip_fields=['Município', 'QTD', 'Público', 'Renda'],
      log_x=True,
      show_color_legend=False,
    )
    st.caption('Cada bolinha é um município requerente de obras brasileiras lançadas: o eixo X (escala log) é o número de obras, o eixo Y o público total e o tamanho da bolinha a renda total.')
    
  st.subheader('Participação de São Paulo na produção, renda e público nacionais')
  obras_unicas = df_sp_br.drop_duplicates('CPB')
  obras_sp = obras_unicas['MUN_SP'].sum()
  obras_total = len(obras_unicas)
  participacao_obras = obras_sp / obras_total * 100

  renda_sp = df_sp_br[df_sp_br['MUN_SP']]['RENDA_TOTAL'].sum()
  renda_total = df_sp_br['RENDA_TOTAL'].sum()
  participacao_renda = renda_sp / renda_total * 100

  publico_sp = df_sp_br[df_sp_br['MUN_SP']]['PUBLICO_TOTAL'].sum()
  publico_total = df_sp_br['PUBLICO_TOTAL'].sum()
  participacao_publico = publico_sp / publico_total * 100

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      st.metric('Participação na produção', f'{obras_sp:,} de {obras_total:,} ({participacao_obras:.1f}%)', border=True)
      st.metric('Participação na renda (R$)', f'{renda_sp:,.0f} de {renda_total:,.0f} ({participacao_renda:.1f}%)', border=True)
      st.metric('Participação no público', f'{publico_sp:,} de {publico_total:,} ({participacao_publico:.1f}%)', border=True)

      st.caption('Percentual de obras brasileiras lançadas produzidas por requerente em São Paulo, considerando apenas lançamentos de obras com PAIS_OBRA = BRASIL. A renda e o público somam apenas os lançamentos das obras paulistas sobre o total de lançamentos de obras brasileiras.')

    with col2:
      with st.container(border=True):
        st.markdown('**Top 10 filmes de São Paulo por público**')
        df_sp_top = (
          df_sp_br[df_sp_br['MUN_SP']]
            .groupby(['CPB', 'TITULO_ORIGINAL'])
            .agg(Público=('PUBLICO_TOTAL', 'sum'), Renda=('RENDA_TOTAL', 'sum'))
            .reset_index()
            .sort_values('Público', ascending=False)
            .head(10)[['TITULO_ORIGINAL', 'Público', 'Renda']]
            .assign(Público=lambda d: d['Público'].map('{:,}'.format))
            .assign(Renda=lambda d: d['Renda'].map('R$ {:,.0f}'.format))
            .rename(columns={'TITULO_ORIGINAL': 'Título da obra'})
        )
        st.table(df_sp_top, hide_index=True, border='horizontal')

  return