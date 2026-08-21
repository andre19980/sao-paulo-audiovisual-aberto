import streamlit as st
import pandas as pd

from lib.normalizers import converte_moeda, normaliza_cnpj
from charts.pie import plot_custom_pie_chart
from charts.bubble import plot_custom_bubble_chart
from charts.bar import plot_custom_ranking_bar_chart

def section(df_contribuintes, df_produtoras_independentes):
  st.header('Panorama geral dos contribuintes')

  total_contribuintes = len(df_contribuintes)
  total_aplicado = df_contribuintes['TOTAL_APLICADO'].sum()
  media_aplicado = total_aplicado / total_contribuintes if total_contribuintes > 0 else 0

  df_pf = df_contribuintes[df_contribuintes['CNPJ_CONTRIBUINTE'] == 'PESSOA FÍSICA']
  df_pj = df_contribuintes[df_contribuintes['CNPJ_CONTRIBUINTE'] != 'PESSOA FÍSICA']
  
  with st.container(horizontal=True):
    st.metric('Quantidade de contribuintes', total_contribuintes, border=True)
    st.metric('Total aplicado', f'R$ {total_aplicado:,.2f}', border=True)
    st.metric('Média aplicada por contribuinte', f'R$ {media_aplicado:,.2f}', border=True)
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
      st.metric('Contribuintes Pessoas Físicas', len(df_pf), border=True)
      st.metric('Valor para Pessoas Físicas', f'R$ {df_pf['TOTAL_APLICADO'].sum():,.2f}', border=True)
      
    with col2:
      st.metric('Contribuintes Pessoas Jurídicas', len(df_pj), border=True)
      st.metric('Valor para Pessoas Jurídicas', f'R$ {df_pj['TOTAL_APLICADO'].sum():,.2f}', border=True)

  st.subheader('Distribuição do total aplicado por artigo')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 2], gap='large', border=True)

    with col1:
      artigos = {
        'Art. 1º': 'TOTAL_APLICADO_ART1',
        'Art. 1º-A': 'TOTAL_APLICADO_ART1A',
        'Art. 3º': 'TOTAL_APLICADO_ART3',
        'Art. 3º-A': 'TOTAL_APLICADO_ART3A',
        'Art. 18': 'TOTAL_APLICADO_ART18',
        'Art. 25': 'TOTAL_APLICADO_ART25',
        'Art. 39': 'TOTAL_APLICADO_ART39',
        'Art. 41': 'TOTAL_APLICADO_ART41',
      }
      df_artigos = pd.DataFrame({
        'Artigo': list(artigos.keys()),
        'Total aplicado': [df_contribuintes[col].sum() for col in artigos.values()],
      }).sort_values('Total aplicado', ascending=False)

      plot_custom_pie_chart(
        df=df_artigos,
        color='Artigo',
        theta='Total aplicado',
        title='Total aplicado por artigo (renúncia fiscal)',
        color_scheme='category10',
      )
      st.caption(
        'Soma dos valores aplicados pelos contribuintes em cada artigo da Lei do Audiovisual '
        '(mecanismo de renúncia fiscal). O Art. 1º-A lidera, seguido do Art. 1º e do Art. 3º.'
        'Os artigos 1º-A e 1º concentram mais da metade dos valores aplicados '
        '(34,9% + 30,5%). O Art. 41 (Funcines) e o Art. 18 têm participação pequena. Isso indica '
        'onde o incentivo fiscal se concentra e que mecanismos poderiam ser mais difundidos.'
      )

    with col2:
      df_contrib_artigo = pd.DataFrame({
        'Artigo': list(artigos.keys()),
        'Contribuintes': [(df_contribuintes[col] > 0).sum() for col in artigos.values()],
        'Total aplicado': [df_contribuintes[col].sum() for col in artigos.values()],
      })
      df_contrib_artigo['Média por contribuinte'] = (
        df_contrib_artigo['Total aplicado'] / df_contrib_artigo['Contribuintes']
      )
      plot_custom_bubble_chart(
        df=df_contrib_artigo,
        x='Contribuintes',
        x_title='Nº de contribuintes',
        y='Total aplicado',
        y_title='Total aplicado (R$)',
        size='Total aplicado',
        size_title='Total aplicado (R$)',
        color='Artigo',
        color_title='Artigo',
        title='Contribuintes vs total aplicado por artigo',
        log_x=True,
        tooltip_fields=['Artigo', 'Contribuintes', 'Total aplicado', 'Média por contribuinte'],
      )
      st.caption(
        'Cada bolha é um artigo: eixo X é o número de contribuintes que aplicaram recursos e eixo '
        'Y, o total aplicado. Artigos com poucos contribuintes e bolhas grandes (alto valor) '
        'indicam forte concentração — poucos investidores respondem por muito do incentivo.'
        'Insight: Art. 1º e Art. 1º-A têm milhares de contribuintes (2.158 e 2.803) e valores '
        'altos. Já os Art. 39, 3º e 3º-A concentram valores expressivos em pouquíssimos '
        'contribuintes (18, 39 e 28), com média por contribuinte acima de R$ 9 mi — ou seja, '
        'poucos grandes investidores dominam esses mecanismos.'
      )

  df_contribuintes['CNPJ_LIMPO'] = df_contribuintes['CNPJ_CONTRIBUINTE'].apply(normaliza_cnpj)
  df_produtoras_independentes['CNPJ_LIMPO'] = df_produtoras_independentes['CNPJ'].apply(normaliza_cnpj)
  df_pi_sp = df_produtoras_independentes[df_produtoras_independentes['MUNICIPIO'] == 'SÃO PAULO'].copy()

  df = pd.merge(df_contribuintes, df_pi_sp, on='CNPJ_LIMPO')

  st.markdown('### :orange-background[⚠️:orange[Produtoras independentes paulistanas que também são contribuintes]]')
  st.text(
    'Cruzamento do dataset de contribuintes (renúncia fiscal) com as produtoras independentes '
    'de São Paulo via CNPJ. Estas produtoras, além de captarem recursos por mecanismos de '
    'incentivo, também aparecem como incentivadoras (contribuintes) — ou seja, investem '
    'recursos próprios em projetos com renúncia fiscal.'
  )
  
  with st.container():
    col1, col2 = st.columns([1, 1], gap='large')
    
    with col1:
      st.metric('Produtoras SP que também são contribuintes', f'{df["RAZAO_SOCIAL"].nunique():,}', border=True)
      st.metric('Total aplicado por essas produtoras', f"R$ {df['TOTAL_APLICADO'].sum():,.2f}", border=True)
      
    with col2:
      with st.container(border=True):
        df_prod_contrib = (
          df.groupby(['RAZAO_SOCIAL', 'CLASSIFICACAO_NIVEL_PRODUTORA'])
            .agg(TOTAL_APLICADO=('TOTAL_APLICADO', 'sum'))
            .reset_index()
            .sort_values('TOTAL_APLICADO', ascending=False)
        )

        plot_custom_ranking_bar_chart(
          df=df_prod_contrib,
          x='TOTAL_APLICADO',
          x_title='Total aplicado (R$)',
          y='RAZAO_SOCIAL',
          y_title=None,
          title='Produtoras paulistanas contribuintes por total aplicado',
          tooltip=['RAZAO_SOCIAL', 'CLASSIFICACAO_NIVEL_PRODUTORA', 'TOTAL_APLICADO'],
          color='TOTAL_APLICADO',
          color_scheme='viridis',
          label_limit=320,
          step=24,
        )
        st.text(
          'O cruzamento por CNPJ mostra que algumas produtoras independentes de SP atuam '
          'simultaneamente como captadoras e como incentivadoras. Isso indica que parte dos recursos '
          'do incentivo fiscal volta para o próprio setor — produtoras (em geral de maior nível, '
          'como as de nível 5) investem em projetos com renúncia fiscal. A fronteira entre quem '
          'produz e quem investe é porosa no audiovisual.'
        )

  return
