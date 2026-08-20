import streamlit as st
import pandas as pd
import numpy as np

from charts.line import plot_custom_line_chart
from charts.bar import plot_custom_grouped_bar_chart, plot_custom_ranking_bar_chart
from lib.normalizers import normaliza_cnpj

def section(df_projetos_fsa, df_produtoras_independentes=None):
  st.header('Panorama geral do FSA')

  total_projetos = len(df_projetos_fsa)
  total_contratado = df_projetos_fsa['VALOR_CONTRATO_DOU'].sum()
  total_liberado = df_projetos_fsa['VALOR_TOTAL_LIBERADO'].sum()
  taxa_execucao = (total_liberado / total_contratado * 100) if total_contratado > 0 else 0
  projetos_executados = df_projetos_fsa[df_projetos_fsa['VALOR_TOTAL_LIBERADO'] == df_projetos_fsa['VALOR_CONTRATO_DOU']]
  projetos_sem_liberacao = df_projetos_fsa[df_projetos_fsa['VALOR_TOTAL_LIBERADO'] == 0]

  with st.container(horizontal=True):
    col1, col2, col3 = st.columns([1, 1, 1], gap='large', border=True)
    
    with col1:
      st.metric('Total de projetos', total_projetos)
    with col2:
      st.metric('Total contratado', f'R$ {total_contratado:,.2f}')
    with col3:  
      st.metric('Total liberado', f'R$ {total_liberado:,.2f}')
      
  with st.container(horizontal=True):
    col1, col2, col3 = st.columns([1, 1, 1], gap='large', border=True)
    
    with col1:
      st.metric('Taxa de execução', f'{taxa_execucao:.1f}%')
    with col2:
      st.metric('Projetos com execução total', f'{len(projetos_executados)} ({len(projetos_executados)/total_projetos*100:.1f}%)')
    with col3:  
      st.metric('Projetos sem liberação', f'{len(projetos_sem_liberacao)} ({len(projetos_sem_liberacao)/total_projetos*100:.1f}%)')
      
  with st.container(horizontal=True):
    col1, col2 = st.columns([2, 1], gap='small')
    df_chamadas = df_projetos_fsa.groupby('CHAMADA_PUBLICA').agg({
      'VALOR_CONTRATO_DOU': 'sum',
      'VALOR_TOTAL_LIBERADO': 'sum',
      'TITULO_PROJETO': 'count'
    }).rename(columns={'TITULO_PROJETO': 'QTD_PROJETOS'}).reset_index()

    df_chamadas['TAXA_EXECUCAO'] = (df_chamadas['VALOR_TOTAL_LIBERADO'] / df_chamadas['VALOR_CONTRATO_DOU'] * 100).round(2)
    df_chamadas = df_chamadas.sort_values('VALOR_CONTRATO_DOU', ascending=False)

    anos_editais = np.sort(df_projetos_fsa['ANO_EDITAL'].unique())

    with col1:
      with st.container(border=True):
        st.markdown('**Listagem das chamadas públicas**')
        st.table(
          df_chamadas.rename(columns={
            'CHAMADA_PUBLICA': 'Chamada pública',
            'VALOR_CONTRATO_DOU': 'Total dos contratos (R$)',
            'VALOR_TOTAL_LIBERADO': 'Total liberado (R$)',
            'QTD_PROJETOS': 'Qtde. de projetos',
            'TAXA_EXECUCAO': 'Taxa de execução',
          }),
          width='stretch',
          hide_header=False,
          hide_index=True,
          height=350,
          border='horizontal'
        )
    
    with col2:
      with st.container(border=True):
        st.markdown('**Anos dos editais**')
        with st.container(horizontal=True, gap='xxsmall', horizontal_alignment='left'):
          for ano in anos_editais:
            st.markdown(f'### :blue-background[:blue[{ano}]]')

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], border=True)
    
    with col1:
      df_projetos_por_ano = (
        df_projetos_fsa.groupby('ANO_CONTRATO')
          .agg(QTD_PROJETOS=('TITULO_PROJETO', 'count'))
          .reset_index()
          .dropna()
      )
      df_projetos_por_ano['Todos'] = 'Projetos'
      plot_custom_grouped_bar_chart(
        df=df_projetos_por_ano,
        x='ANO_CONTRATO',
        x_title='Ano do contrato',
        y='QTD_PROJETOS',
        y_title='Quantidade de projetos',
        x_offset='Todos',
        x_offset_title='',
        title='Quantidade de projetos por ano do contrato',
      )
      st.caption(
        'Distribuição do número de projetos de investimento contratados no âmbito do FSA '
        'por ano do contrato (e NÃO do edital).'
      )
    with col2:
      df_contratos_por_ano = (
        df_projetos_fsa.groupby('ANO_CONTRATO')
          .agg(TOTAL_CONTRATO=('VALOR_CONTRATO_DOU', 'sum'))
          .reset_index()
          .dropna()
      )
      plot_custom_line_chart(
        df=df_contratos_por_ano,
        x='ANO_CONTRATO',
        x_title='Ano do contrato',
        y='TOTAL_CONTRATO',
        y_title='Total dos contratos (R$)',
        title='Evolução do total contratado por ano',
        x_nice=False,
      )
  st.caption(
    'Soma dos valores contratados dos projetos de investimento do FSA por ano do contrato '
    '(e NÃO do edital), mostrando a evolução temporal do montante contratado.'
  )

  st.subheader('FSA e produtoras independentes paulistanas')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

    fsa_cnpj = df_projetos_fsa.copy()
    fsa_cnpj['CNPJ_LIMPO'] = fsa_cnpj['CNPJ_PROPONENTE'].apply(normaliza_cnpj)
    pi_cnpj = df_produtoras_independentes.copy()
    pi_cnpj['CNPJ_LIMPO'] = pi_cnpj['CNPJ'].apply(normaliza_cnpj)
    pi_sp = pi_cnpj[pi_cnpj['MUNICIPIO'] == 'SÃO PAULO']

    df_cruz = pd.merge(
      fsa_cnpj,
      pi_sp[['CNPJ_LIMPO', 'CLASSIFICACAO_NIVEL_PRODUTORA']],
      on='CNPJ_LIMPO',
      how='inner',
    )

    df_nivel = (
      df_cruz.groupby('CLASSIFICACAO_NIVEL_PRODUTORA')
        .agg(
          N_PROJETOS=('TITULO_PROJETO', 'count'),
          CONTRATADO=('VALOR_CONTRATO_DOU', 'sum'),
          LIBERADO=('VALOR_TOTAL_LIBERADO', 'sum'),
        )
        .reset_index()
        .sort_values('CONTRATADO', ascending=False)
    )
    df_nivel['TAXA EXECUÇÃO (%)'] = (df_nivel['LIBERADO'] / df_nivel['CONTRATADO'] * 100).round(1)
    df_nivel['MÉDIA POR PROJETO'] = df_nivel['CONTRATADO'] / df_nivel['N_PROJETOS']
    
    with col1:
      with st.container(border=True):
        plot_custom_ranking_bar_chart(
          df=df_nivel,
          x='CONTRATADO',
          x_title='Total contratado (R$)',
          y='CLASSIFICACAO_NIVEL_PRODUTORA',
          y_title='Nível da produtora',
          title='Total contratado via FSA por nível da produtora independente (SP)',
          tooltip=['CLASSIFICACAO_NIVEL_PRODUTORA', 'N_PROJETOS', 'CONTRATADO', 'LIBERADO', 'TAXA EXECUÇÃO (%)'],
          color='CONTRATADO',
          color_scheme='viridis',
          label_limit=60,
          step=26,
        )
        st.caption(
          'Cruzamento dos projetos contratados via FSA com as produtoras independentes sediadas em '
          'São Paulo, pelo nível de classificação da produtora (IN 119 da ANCINE). O objetivo é '
          'avaliar como o fomento direto do FSA se distribui entre produtoras de portes distintos.'
        )
        st.text(
          r'Em São Paulo, produtoras de nível 5 concentram R$ 293 mi (36% do contratado '
          r'paulista) e as de nível 4, R$ 242 mi (30%) — somando 66% do total. As de nível 1 '
          r'respondem por apenas 14%. Apesar disso, a taxa de execução é alta em todos os níveis '
          r'(96%-100%), indicando que as produtoras que conseguem acessar o FSA executam bem os '
          r'recursos. A concentração sugere que políticas municipais poderiam ampliar o acesso de '
          r'produtoras de níveis 1 a 3 (menor porte) ao fomento.'
        )

    with col2:
      with st.container():
        por_prod = (
          df_cruz.groupby('CNPJ_LIMPO')['VALOR_CONTRATO_DOU']
            .sum()
            .sort_values(ascending=False)
        )
        cum = (por_prod.cumsum() / por_prod.sum() * 100)
        n_50 = (cum < 50).sum()
        n_80 = (cum < 80).sum()
        st.metric('Produtoras SP responsáveis por 50% do FSA', f'{n_50} de {len(por_prod)}', border=True)
        st.metric('Produtoras SP responsáveis por 80% do FSA', f'{n_80} de {len(por_prod)}', border=True)

  return