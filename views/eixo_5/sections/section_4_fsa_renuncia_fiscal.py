import streamlit as st
import pandas as pd

from charts.bar import plot_custom_ranking_bar_chart
from charts.hist import plot_custom_histogram_chart
from lib.normalizers import normaliza_cnpj

def _analise_cruzada(fsa_df, ren_df, titulo):
  fsa_por = fsa_df.groupby('CNPJ_LIMPO')['VALOR_CONTRATO_DOU'].sum()
  ren_por = ren_df.groupby('CNPJ_LIMPO')['TOTAL_CAPTADO'].sum()

  fsa_set = set(fsa_por.index)
  ren_set = set(ren_por.index)

  ambos = sorted(fsa_set & ren_set)
  so_fsa = sorted(fsa_set - ren_set)
  so_ren = sorted(ren_set - fsa_set)

  st.subheader(f'Análise: {titulo}')
  st.markdown(f'#### Sobreposição entre os mecanismos')
  st.caption(
    'Compara as produtoras que acessam o FSA com as que captam via renúncia fiscal '
    '(Lei do Audiovisual e Rouanet). O objetivo é identificar o quanto os dois mecanismos se '
    'sobrepõem e quantas produtoras dependem de apenas um deles.'
  )

  col1, col2, col3 = st.columns([1, 1, 1], gap='large')
  with col1:
    st.metric('Só FSA', f'{len(so_fsa):,}', border=True)
  with col2:
    st.metric('Só renúncia fiscal', f'{len(so_ren):,}', border=True)
  with col3:
    st.metric('Acessam os dois', f'{len(ambos):,}', border=True)

  df_dupla = pd.DataFrame({
    'CNPJ_LIMPO': ambos,
    'FSA': fsa_por.reindex(ambos).fillna(0),
    'RENFISC': ren_por.reindex(ambos).fillna(0),
  })
  df_dupla['TOTAL'] = df_dupla['FSA'] + df_dupla['RENFISC']
  df_dupla['PARTICIPACAO_FSA (%)'] = (df_dupla['FSA'] / df_dupla['TOTAL'] * 100).round(1)
  df_dupla['RAZAO_SOCIAL'] = df_dupla['CNPJ_LIMPO'].map(
    fsa_df.drop_duplicates('CNPJ_LIMPO').set_index('CNPJ_LIMPO')['RAZAO_SOCIAL_PROPONENTE']
  )
  df_dupla = df_dupla.sort_values('TOTAL', ascending=False)
  
  st.markdown(f'#### Distribuição dos mecanismos de captação')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large', border=True)

    with col1:
      top_dupla = df_dupla.head(15).copy()
      top_dupla['Produtora'] = top_dupla['RAZAO_SOCIAL'].fillna(top_dupla['CNPJ_LIMPO'])
      plot_custom_ranking_bar_chart(
        df=top_dupla,
        x='TOTAL',
        x_title='Total captado (R$)',
        y='Produtora',
        y_title=None,
        title=f'{titulo} - Top produtoras no FSA e na renúncia fiscal',
        tooltip=['Produtora', 'FSA', 'RENFISC', 'TOTAL', 'PARTICIPACAO_FSA (%)'],
        color='TOTAL',
        color_scheme='viridis',
        label_limit=300,
        step=24,
      )
      st.caption(
        'Top 15 produtoras que combinam recursos do FSA e da renúncia fiscal, pelo valor '
        'total. A coluna de participação mostra a dependência relativa de cada fonte.'
      )
      
    with col2:
      faixas = [
        'FSA < 20%', 'FSA 20-40%', 'FSA 40-60%', 'FSA 60-80%', 'FSA > 80%',
      ]
      limites = {
        'FSA < 20%': (0, 20),
        'FSA 20-40%': (20, 40),
        'FSA 40-60%': (40, 60),
        'FSA 60-80%': (60, 80),
        'FSA > 80%': (80, 101),
      }
      df_dependencia = pd.DataFrame({
        'Faixa': faixas,
        'Produtoras': [
          ((df_dupla['PARTICIPACAO_FSA (%)'] >= limites[f][0]) & (df_dupla['PARTICIPACAO_FSA (%)'] < limites[f][1])).sum()
          for f in faixas
        ],
      })
      plot_custom_histogram_chart(
        df=df_dependencia,
        x='Faixa',
        x_title=None,
        y='Produtoras',
        y_title='Nº de produtoras',
        faixas=faixas,
        title=f'{titulo} - Dependência de mecanismo (FSA vs renúncia fiscal)',
        color_scale_scheme='viridis',
      )
      st.caption(
        'Distribuição das produtoras que estão nos dois mecanismos conforme a participação do FSA '
        'no total recebido. À esquerda estão as que dependem mais da renúncia fiscal; à direita, '
        'as que dependem mais do FSA. '
        'Das produtoras presentes nos dois mecanismos, muitas dependem fortemente de um '
        'deles. Quem está em "FSA < 20%" depende quase só da renúncia fiscal, e quem está em '
        '"FSA > 80%" depende quase só do FSA — o que sugere oportunidade de políticas que '
        'estimulem a diversificação de fontes de fomento.'
      )
  
  st.markdown(f'#### Comparação de valores captados')
  fsa_total = fsa_por.sum()
  ren_total = ren_por.sum()
  fsa_n = len(fsa_set)
  ren_n = len(ren_set)
  fsa_media = fsa_total / fsa_n if fsa_n else 0
  ren_media = ren_total / ren_n if ren_n else 0

  col1, col2 = st.columns([1, 1], gap='large')
  with col1:
    st.metric('Total FSA', f'R$ {fsa_total:,.0f}', border=True)
    st.metric('Produtoras FSA', f'{fsa_n:,}', border=True)
    st.metric('Média por produtora (FSA)', f'R$ {fsa_media:,.0f}', border=True)
  with col2:
    st.metric('Total renúncia fiscal', f'R$ {ren_total:,.0f}', border=True)
    st.metric('Produtoras renúncia fiscal', f'{ren_n:,}', border=True)
    st.metric('Média por produtora (renúncia)', f'R$ {ren_media:,.0f}', border=True)
    
    
  with st.container(border=True):
    df_comp_valores = pd.DataFrame({
      'Mecanismo': ['FSA', 'Renúncia fiscal'],
      'Total (R$)': [fsa_total, ren_total],
      'Produtoras': [fsa_n, ren_n],
      'Média por produtora (R$)': [fsa_media, ren_media],
    })
    plot_custom_ranking_bar_chart(
      df=df_comp_valores,
      x='Total (R$)',
      x_title='Total (R$)',
      y='Mecanismo',
      y_title=None,
      title=f'Total captado: FSA vs renúncia fiscal',
      tooltip=['Mecanismo', 'Total (R$)', 'Produtoras', 'Média por produtora (R$)'],
      color='Total (R$)',
      color_scheme='viridis',
      label_limit=160,
      step=30,
    )
    if ren_total > 0 and fsa_total > 0:
      st.text(
        f'A renúncia fiscal movimenta cerca de {ren_total/fsa_total:.1f}x mais que o FSA '
        f'no total, e a média por produtora é de R$ {ren_media/1e6:.1f} mi na renúncia contra '
        f'R$ {fsa_media/1e6:.1f} mi no FSA. O FSA atende a {fsa_n:,} produtoras e a renúncia a '
        f'{ren_n:,}, indicando alcances e valores complementares.'
      )

  return df_dupla


def section(df_projetos_fsa, df_projetos_renfisc, df_produtoras_independentes=None):
  st.header('FSA e Renúncia fiscal')
  df_projetos_fsa['CNPJ_LIMPO'] = df_projetos_fsa['CNPJ_PROP_LIMPO']

  recorte = st.segmented_control(
    'Recorte geográfico',
    options=['Nacional', 'São Paulo'],
    selection_mode='single',
    default='Nacional',
  )

  fsa_uso = df_projetos_fsa
  ren_uso = df_projetos_renfisc
  titulo = 'Brasil'

  if recorte == 'São Paulo' and df_produtoras_independentes is not None:
    pi_sp = df_produtoras_independentes.copy()
    pi_sp['CNPJ_LIMPO'] = pi_sp['CNPJ'].apply(normaliza_cnpj)
    pi_sp = pi_sp[pi_sp['MUNICIPIO'] == 'SÃO PAULO']
    cnpj_sp = set(pi_sp['CNPJ_LIMPO'])

    fsa_uso = df_projetos_fsa[df_projetos_fsa['CNPJ_LIMPO'].isin(cnpj_sp)].copy()
    ren_uso = df_projetos_renfisc[df_projetos_renfisc['CNPJ_LIMPO'].isin(cnpj_sp)].copy()
    titulo = 'São Paulo'

  _analise_cruzada(fsa_uso, ren_uso, titulo)

  return