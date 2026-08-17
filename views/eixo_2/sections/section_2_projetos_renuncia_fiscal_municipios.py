import pandas as pd
import streamlit as st

from lib.normalizers import converte_moeda, normaliza_cnpj, normaliza_municipio

from charts.bar import plot_custom_layered_bar_chart, plot_custom_ranking_bar_chart
from charts.brazil_map import plot_custom_choropleth_brazil_map
from charts.bubble import plot_custom_bubble_chart
from charts.heatmap import plot_custom_heatmap
from charts.pie import plot_custom_pie_chart

def section(df_projetos_renfisc, df_produtoras_independentes):
  # Normaliza o município do proponente
  df_projetos_renfisc['MUNICIPIO_PROPONENTE'] = (
    df_projetos_renfisc['MUNICIPIO_PROPONENTE'].map(normaliza_municipio)
  )

  colunas_monetarias = [
    'CAPTADO_ART1', 'CAPTADO_ART1A', 'CAPTADO_ART3', 'CAPTADO_ART3A',
    'CAPTADO_ART18', 'CAPTADO_ART25', 'CAPTADO_ART39', 'CAPTADO_FUNCINES',
    'CAPTADO_EDITAL_ANCINE', 'CAPTADO_PAR', 'CAPTADO_PAQ', 'CAPTADO_OUTROS_EDITAIS',
    'CAPTADO_LEI_ESTADUAL', 'CAPTADO_LEI_MUNICIPAL', 'CAPTADO_OUTRAS_FONTES',
    'CAPTADO_CONTRAPARTIDA', 'CAPTADO_CONVERSAO', 'TOTAL_CAPTADO'
  ]

  for col in colunas_monetarias:
    df_projetos_renfisc[col] = df_projetos_renfisc[col].apply(converte_moeda)

  st.header('Renúncia fiscal e captação por localidade')
  col_metric1, col_metric2, col_metric3 = st.columns([1, 1, 1], gap='large')
  with col_metric1:
    st.metric("Projetos", f"{df_projetos_renfisc.shape[0]:,}", border=True)
  with col_metric2:
    st.metric("Total captado", f"R$ {df_projetos_renfisc['TOTAL_CAPTADO'].sum():,.0f}", border=True)
  with col_metric3:
    st.metric("Média por projeto", f"R$ {df_projetos_renfisc['TOTAL_CAPTADO'].mean():,.0f}", border=True)

  df_municipios = df_projetos_renfisc.groupby(['MUNICIPIO_PROPONENTE', 'UF_PROPONENTE']).agg(
    TOTAL_CAPTADO=('TOTAL_CAPTADO', 'sum'),
    N_PROJETOS=('TITULO_PROJETO', 'count'),
  ).reset_index().sort_values('TOTAL_CAPTADO', ascending=False)
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      with st.container(border=True, height='stretch'):
        top_municipios = df_municipios.head(15)
        plot_custom_ranking_bar_chart(
          df=top_municipios,
          x='TOTAL_CAPTADO',
          x_title='Total captado (R$)',
          y='MUNICIPIO_PROPONENTE',
          y_title=None,
          title='Top 15 municípios por captação via renúncia fiscal',
          tooltip=['MUNICIPIO_PROPONENTE', 'UF_PROPONENTE', 'N_PROJETOS', 'TOTAL_CAPTADO'],
          color='TOTAL_CAPTADO',
          label_limit=240,
          color_scheme='bluepurple',
          step=28
        )
        st.caption(
          'Valor total captado por projetos de renúncia fiscal segundo o município do proponente. '
          'RIO DE JANEIRO e SÃO PAULO dominam com folga o total captado.'
        )

    with col2:
      with st.container(border=True):
        top_municipios_bubble = top_municipios.copy()
        top_municipios_bubble['MEDIA_POR_PROJETO'] = (
          top_municipios_bubble['TOTAL_CAPTADO'] / top_municipios_bubble['N_PROJETOS']
        )
        plot_custom_bubble_chart(
          df=top_municipios_bubble,
          x='N_PROJETOS',
          x_title='Número de projetos',
          y='MEDIA_POR_PROJETO',
          y_title='Média captada por projeto (R$)',
          size='TOTAL_CAPTADO',
          size_title='Total captado (R$)',
          color='MEDIA_POR_PROJETO',
          color_title='Média por projeto (R$)',
          title='Top 15 municípios: total captado vs média por projeto',
          color_type='Q',
          color_scheme='bluepurple',
          tooltip_fields=['MUNICIPIO_PROPONENTE', 'N_PROJETOS', 'TOTAL_CAPTADO', 'MEDIA_POR_PROJETO'],
          height=540,
          size_range=[50, 1500],
        )
        st.caption(
          'Bubble chart dos mesmos 15 municípios: o tamanho da bolinha é o total captado e a '
          'intensidade da cor, a média captada por projeto. Municípios com bolhas grandes e '
          'escuras combinam alto volume e alto valor médio por projeto.'
        )

  df_uf_captado = (
    df_projetos_renfisc.groupby('UF_PROPONENTE')['TOTAL_CAPTADO']
      .sum()
      .rename('TOTAL_CAPTADO')
      .reset_index()
      .sort_values('TOTAL_CAPTADO', ascending=False)
  )
  with st.container(horizontal=True, border=True, width='content'):
    plot_custom_choropleth_brazil_map(
      df=df_uf_captado,
      geojson_path='assets/brazil-states.geojson',
      uf_col='UF_PROPONENTE',
      value_col='TOTAL_CAPTADO',
      value_title='Total captado (R$)',
      title='Total captado por estado do proponente (renúncia fiscal)',
      color_scheme='bluepurple',
      log_color=True,
    )
    st.caption(
      'Mapa do Brasil colorido pelo total captado via renúncia fiscal segundo o estado do '
      'proponente. A escala logarítmica de cor cria nuances entre estados de portes muito '
      'diferentes (SP e RJ captam bilhões, os demais milhões).'
    )
    
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
    'Outros editais': 'CAPTADO_OUTROS_EDITAIS',
    'PAR': 'CAPTADO_PAR',
    'PAQ': 'CAPTADO_PAQ',
    'Lei estadual': 'CAPTADO_LEI_ESTADUAL',
    'Lei municipal': 'CAPTADO_LEI_MUNICIPAL',
    'Outras fontes': 'CAPTADO_OUTRAS_FONTES',
    'Contrapartida': 'CAPTADO_CONTRAPARTIDA',
    'Conversão': 'CAPTADO_CONVERSAO',
  }
  df_mec = pd.DataFrame({
    'Mecanismo': list(mecanismos.keys()),
    'Total captado': [df_projetos_renfisc[col].sum() for col in mecanismos.values()],
  }).sort_values('Total captado', ascending=False)

  st.header('Captação por mecanismo de incentivo no Brasil')
  with st.container(horizontal=True, border=True):
    plot_custom_ranking_bar_chart(
      df=df_mec,
      x='Total captado',
      x_title='Total captado (R$)',
      y='Mecanismo',
      y_title=None,
      title='Captação por mecanismo de fomento',
      tooltip=['Mecanismo', 'Total captado'],
      color='Total captado',
      color_scheme='viridis',
      label_limit=180,
      step=24,
    )
    st.caption(
      'Distribuição do total captado entre todos os mecanismos de fomento. Os artigos 3º-A e 3º da '
      'Lei do Audiovisual lideram, seguidos do 1º-A e do 39. '
      'Mecanismos como PAR, PAQ, contrapartida e conversão têm captação quase nula.'
    )

  df_ranking_mec = pd.DataFrame({
    'Mecanismo': list(mecanismos.keys()),
    'Total captado': [df_projetos_renfisc[col].sum() for col in mecanismos.values()],
  }).sort_values('Total captado', ascending=False)
  top7_mec = df_ranking_mec.head(7)['Mecanismo'].tolist()
  cols_top7 = [mecanismos[m] for m in top7_mec]
  df_mec_uf = (
    df_projetos_renfisc
      .melt(id_vars=['UF_PROPONENTE'], value_vars=cols_top7, var_name='COL_MEC', value_name='Total captado')
  )
  df_mec_uf['Mecanismo'] = df_mec_uf['COL_MEC'].map({v: k for k, v in mecanismos.items()})
  df_mec_uf = df_mec_uf.groupby(['UF_PROPONENTE', 'Mecanismo'], as_index=False)['Total captado'].sum()
  # Estados sem captação no mecanismo ficam como NaN (sem preenchimento). Isso é necessário
  # porque a escala logarítmica não aceita valor 0 (log(0) = -∞), o que colapsa o domínio
  # e pinta todas as células da mesma cor.
  df_mec_uf.loc[df_mec_uf['Total captado'] == 0, 'Total captado'] = None

  st.subheader('Top mecanismos de fomento por estado')
  st.caption(
    'Heatmap do total captado por estado do proponente para os 7 mecanismos de maior captação '
    'nacional (Art. 3º-A, 3º, 1º-A, 39, 1º, 25 e Funcines). A cor usa escala logarítmica, pois '
    'SP e RJ captam ordens de grandeza acima dos demais estados; estados sem captação no '
    'mecanismo ficam sem preenchimento.'
  )
  plot_custom_heatmap(
    df=df_mec_uf,
    x='Mecanismo',
    x_title=None,
    y='UF_PROPONENTE',
    y_title='Estado',
    color='Total captado',
    color_title='Total captado (R$)',
    title='Top 7 mecanismos de fomento por estado (2026)',
    cell_size=20,
    color_scheme='yelloworangered',
    log_color=True,
    invalid_color="#fdde99",
  )

  st.header('Captação por mecanismo de incentivo no município de São Paulo')
  df_sp = df_projetos_renfisc[df_projetos_renfisc['MUNICIPIO_PROPONENTE'] == 'SAO PAULO']
  df_mec_sp = pd.DataFrame({
    'Mecanismo': list(mecanismos.keys()),
    'Total captado SP': [df_sp[col].sum() for col in mecanismos.values()],
    'Total captado BR': [df_projetos_renfisc[col].sum() for col in mecanismos.values()],
  })
  df_mec_sp['Participação SP (%)'] = (
    df_mec_sp['Total captado SP'] / df_mec_sp['Total captado BR'] * 100
  ).round(1)
  df_mec_sp = df_mec_sp.sort_values('Total captado SP', ascending=False)

  st.subheader('Mecanismos mais usados por proponentes paulistanos')
  with st.container(horizontal=True):
    col1, col2 = st.columns([2, 1], gap='large')
    
    with col1:
      df_mec_sp_long = df_mec_sp.melt(
        id_vars=['Mecanismo'],
        value_vars=['Total captado BR', 'Total captado SP'],
        var_name='Escopo',
        value_name='Total captado',
      )
      df_mec_sp_long['Escopo'] = df_mec_sp_long['Escopo'].map({
        'Total captado BR': 'Brasil',
        'Total captado SP': 'São Paulo',
      })
      ordem_mec = df_mec_sp.sort_values('Total captado BR', ascending=False)['Mecanismo'].tolist()
      
      with st.container(border=True):
        plot_custom_layered_bar_chart(
          df=df_mec_sp_long,
          x='Total captado',
          x_title='Total captado (R$)',
          y='Mecanismo',
          y_title=None,
          color='Escopo',
          color_title=None,
          title='Parcela de São Paulo no total de cada mecanismo',
          sort_by='Total captado',
          label_limit=180,
        )
        st.caption(
          'Duas barras sobrepostas por mecanismo: a de fundo (Brasil) mostra o total captado '
          'nacional e a de frente (São Paulo), quanto desse total veio de proponentes paulistanos. '
          'Quanto mais próximos os comprimentos, maior a participação de SP — o Art. 39, por '
          'exemplo, tem cerca de 50% do captado vindo de proponentes paulistanos.'
        )

    with col2:
      df_mec_sp_pie = df_mec_sp[df_mec_sp['Total captado SP'] >= 50_000_000].copy()
      restante = df_mec_sp[df_mec_sp['Total captado SP'] < 50_000_000]['Total captado SP'].sum()
      if restante > 0:
        df_mec_sp_pie = pd.concat([
          df_mec_sp_pie,
          pd.DataFrame([{'Mecanismo': 'Outros (abaixo de R$ 50 mi)', 'Total captado SP': restante}]),
        ], ignore_index=True)

      with st.container(border=True):
        plot_custom_pie_chart(
          df=df_mec_sp_pie,
          color='Mecanismo',
          theta='Total captado SP',
          title='Distribuição dos mecanismos no captado paulista',
          inner_radius=35,
          outer_radius=90,
        )
        st.caption(
          'Fatia de cada mecanismo no total captado por proponentes paulistanos. Mecanismos com '
          'captação de pelo menos R$ 50 milhões aparecem individualizados; os demais são agrupados '
          'na fatia "Outros". O Art. 3º-A responde pela maior fatia, seguido do 1º-A e do 39.'
        )
      
  df_produtoras_ind_sp = df_produtoras_independentes[df_produtoras_independentes['MUNICIPIO'] == 'SÃO PAULO']
  df_produtoras_ind_sp['CNPJ_LIMPO'] = df_produtoras_ind_sp['CNPJ'].apply(normaliza_cnpj)
  df_projetos_renfisc['CNPJ_LIMPO'] = df_projetos_renfisc['CNPJ_PROPONENTE'].apply(normaliza_cnpj)
  df_produtoras_sp_captacao = pd.merge(
    df_produtoras_ind_sp,
    df_projetos_renfisc,
    on='CNPJ_LIMPO',
    how='inner',
  )

  st.subheader('Captação das produtoras independentes paulistanas')
  col_m1, col_m2, col_m3 = st.columns([1, 1, 1], gap='large')
  with col_m1:
    st.metric('Produtoras beneficiadas', f"{df_produtoras_sp_captacao['CNPJ'].nunique():,}", border=True)
  with col_m2:
    st.metric('Projetos com captação', f"{df_produtoras_sp_captacao.shape[0]:,}", border=True)
  with col_m3:
    st.metric('Total captado', f"R$ {df_produtoras_sp_captacao['TOTAL_CAPTADO'].sum():,.0f}", border=True)

  df_captacao_por_produtora = (
    df_produtoras_sp_captacao
      .groupby(['CNPJ', 'RAZAO_SOCIAL'])
      .agg(TOTAL_CAPTADO=('TOTAL_CAPTADO', 'sum'), N_PROJETOS=('TITULO_PROJETO', 'count'))
      .reset_index()
      .sort_values('TOTAL_CAPTADO', ascending=False)
  )

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large', border=True)

    with col1:
      plot_custom_ranking_bar_chart(
        df=df_captacao_por_produtora.head(15),
        x='TOTAL_CAPTADO',
        x_title='Total captado (R$)',
        y='RAZAO_SOCIAL',
        y_title=None,
        title='Top 15 produtoras independentes de SP por captação',
        tooltip=['RAZAO_SOCIAL', 'N_PROJETOS', 'TOTAL_CAPTADO'],
        color='TOTAL_CAPTADO',
        color_scheme='purpleblue',
        label_limit=280,
        step=24,
      )
      st.caption(
        'Ranking das produtoras independentes paulistanas pelo total captado via renúncia '
        'fiscal. Poucas produtoras concentram a maior parte do captado.'
      )

    with col2:
      # Faixas de captação por produtora
      faixas_capt = ['Até R$ 1 mi', 'R$ 1-5 mi', 'R$ 5-10 mi', 'R$ 10-20 mi', 'Mais de R$ 20 mi']
      limites_capt = {
        'Até R$ 1 mi': (0, 1_000_000),
        'R$ 1-5 mi': (1_000_000, 5_000_000),
        'R$ 5-10 mi': (5_000_000, 10_000_000),
        'R$ 10-20 mi': (10_000_000, 20_000_000),
        'Mais de R$ 20 mi': (20_000_000, float('inf')),
      }
      df_faixas_capt = pd.DataFrame({
        'Faixa': faixas_capt,
        'Produtoras': [
          ((df_captacao_por_produtora['TOTAL_CAPTADO'] >= limites_capt[f][0]) & (df_captacao_por_produtora['TOTAL_CAPTADO'] < limites_capt[f][1])).sum()
          for f in faixas_capt
        ],
      })
      from charts.hist import plot_custom_histogram_chart
      plot_custom_histogram_chart(
        df=df_faixas_capt,
        x='Faixa',
        x_title=None,
        y='Produtoras',
        y_title='Nº de produtoras',
        faixas=faixas_capt,
        title='Distribuição das produtoras de SP por faixa de captação',
        color_scale_scheme='tableau10',
      )
      st.caption(
        r'Quantas produtoras independentes paulistanas captaram cada faixa de valor. A maioria '
        r'fica abaixo de R\$ 1 milhão, mas há uma cauda de grandes captadores acima de R\$ 20 mi.'
      )

  df_mec_prod_ind_sp = pd.DataFrame({
    'Mecanismo': list(mecanismos.keys()),
    'Total captado': [df_produtoras_sp_captacao[col].sum() for col in mecanismos.values()],
  })
  
  with st.container(border=True):
    plot_custom_ranking_bar_chart(
      df=df_mec_prod_ind_sp,
      x='Total captado',
      x_title='Total captado (R$)',
      y='Mecanismo',
      y_title=None,
      title='Captação das produtoras independentes paulistanas por mecanismo de fomento',
      tooltip=['Mecanismo', 'Total captado'],
      color='Total captado',
      color_scheme='viridis',
      label_limit=180,
      step=24,
    )

  return
