import streamlit as st
import pandas as pd
import json
from charts.pie import plot_custom_pie_chart
from charts.heatmap import plot_custom_heatmap

def section(df_salas_complexos):
  st.header('Operação e situação do exibidor na cidade de São Paulo')

  st.subheader('Informações sobre grupos exibidores no município')

  df_salas_complexos_sp = df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO']
  df_salas_complexos_sp_metricas = df_salas_complexos_sp[df_salas_complexos_sp['NOME_GRUPO_EXIBIDOR'] != 'NÃO PERTENCE A NENHUM GRUPO EXIBIDOR']
  df_exibidores_sp = df_salas_complexos_sp_metricas['NOME_GRUPO_EXIBIDOR'].unique()
  situacoes_por_grupo = df_salas_complexos_sp_metricas.groupby('NOME_GRUPO_EXIBIDOR')['SITUACAO_EXIBIDOR'].apply(set)
  df_exibidores_regulares_sp = [g for g, sit in situacoes_por_grupo.items() if sit == {'REGULAR'}]
  df_exibidores_irregulares_sp = [g for g, sit in situacoes_por_grupo.items() if 'IRREGULAR' in sit]
  df_salas_complexos_sp_funcionamento_irregular = df_salas_complexos_sp[(df_salas_complexos_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO') & (df_salas_complexos_sp['SITUACAO_EXIBIDOR'] == 'IRREGULAR')]

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

    with col1:
      a, b = st.columns(2)
      c, d = st.columns(2)
      a.metric("Número de grupos exibidores", len(df_exibidores_sp), border=True)
      b.metric("Número de exibidores em situação regular", len(df_exibidores_regulares_sp), border=True)

      c.metric("Número de exibidores em situação irregular", len(df_exibidores_irregulares_sp), border=True)
      d.metric("Sala em funcionamento com exibidor em situação irregular", len(df_salas_complexos_sp_funcionamento_irregular), border=True)
      st.caption(
        'Os grupos em situação regular e irregular não somam o total: um grupo só é '
        'regular se todas as suas salas estiverem em situação REGULAR e só é irregular '
        'se tiver ao menos uma sala IRREGULAR. Grupos com salas em outras situações '
        '(ex.: INDEFERIDO) ficam fora das duas contagens. Além disso, o grupo residual '
        '"NÃO PERTENCE A NENHUM GRUPO EXIBIDOR" é desconsiderado dessas métricas.'
      )
    
    with col2:
      st.dataframe(
        df_salas_complexos_sp_funcionamento_irregular[[
          'NOME_SALA',
          'SITUACAO_SALA',
          'OPERACAO_USUAL',
          'NOME_COMPLEXO',
          'NOME_GRUPO_EXIBIDOR',
          'SITUACAO_EXIBIDOR'
        ]].rename(columns={
          'NOME_SALA': 'Sala',
          'SITUACAO_SALA': 'Situação da sala',
          'OPERACAO_USUAL': 'Operação',
          'NOME_COMPLEXO': 'Complexo',
          'NOME_GRUPO_EXIBIDOR': 'Grupo exibidor',
          'SITUACAO_EXIBIDOR': 'Situação do exibidor'
        }),
        hide_index=True
      )
      st.caption('Lista de salas em funcionamento com exibidores em situação irregular', text_alignment='center', width='stretch')

  st.subheader('Mapeamento de grupos exibidores por tipo de operação')
  df_exibidores_mapa = df_salas_complexos_sp[df_salas_complexos_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'][['NOME_GRUPO_EXIBIDOR', 'OPERACAO_USUAL']].value_counts().reset_index(name='NÚMERO DE SALAS').rename(columns={ 'NOME_GRUPO_EXIBIDOR': 'GRUPO EXIBIDOR', 'OPERACAO_USUAL': 'OPERAÇÃO USUAL'})

  st.table(df_exibidores_mapa, hide_index=True)
  
  with open("assets/grupos-exibidores-sp.json", "r") as file:
    grupos_exibidores_sp = json.load(file)

  df_grupos_exibidores = pd.DataFrame(
    [(grupo, categoria) for grupo, categoria in grupos_exibidores_sp.items()],
    columns=['GRUPO EXIBIDOR', 'CATEGORIA']
  ) 

  df_salas_por_categoria = (
    df_exibidores_mapa
      .merge(df_grupos_exibidores, on='GRUPO EXIBIDOR', how='left')
      .fillna({'CATEGORIA': 'Outros'})
  )
  df_exibidores_operacao_categoria = df_salas_por_categoria
  df_salas_por_categoria = df_salas_por_categoria.groupby('CATEGORIA', as_index=False)['NÚMERO DE SALAS'].sum().sort_values(by='NÚMERO DE SALAS', ascending=False)

  st.subheader('Distribuição de salas em funcionamento por categoria de grupo exibidor')

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    
    df_salas_por_categoria_operacao = (
    df_exibidores_operacao_categoria
        .groupby(['CATEGORIA', 'OPERAÇÃO USUAL'], as_index=False)['NÚMERO DE SALAS']
        .sum()
        .sort_values(by='NÚMERO DE SALAS', ascending=False)
    )

    with col1:
      with st.container(border=True): 
        st.markdown('''
          - **:blue[Privado]**: rede/empresa privada de capital nacional ou estrangeiro, com fins lucrativos, focada em exibição comercial em larga escala.                                                  
          - **:red[Público]**: estatal, vinculado a governo (municipal, estadual ou federal).                                                                                                               
          - **:green[Independente]**: exibidor menor, focado em cinema autoral/arte, salas únicas ou operação local/cultural, sem ser uma grande rede comercial.       
        ''')
        st.table(df_grupos_exibidores, hide_index=True, border='horizontal')
        
    with col2:
      with st.container(border=True):
        plot_custom_pie_chart(
          df=df_salas_por_categoria,
          color='CATEGORIA',
          theta='NÚMERO DE SALAS',
          title='Distribuição de salas por categoria (2026)'
        )

      with st.container(border=True):
        plot_custom_heatmap(
          df=df_salas_por_categoria_operacao,
          x='CATEGORIA',
          x_title='Categoria',
          y='OPERAÇÃO USUAL',
          y_title='Operação usual',
          color='NÚMERO DE SALAS',
          color_title='Quantidade de salas',
          title='Concentração de salas por categoria e operação usual (2026)'
        )
