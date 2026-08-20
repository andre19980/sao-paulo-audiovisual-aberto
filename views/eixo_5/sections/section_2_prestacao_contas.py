import streamlit as st

def section(df_processos_prest):
  total_processos = len(df_processos_prest)
  df_responsaveis = df_processos_prest.groupby('RESPONSAVEL_PRESTACAO').agg({
    'NUMERO_PROCESSO': 'count',
    'NUMERO_SALIC': 'nunique'
  }).rename(columns={'NUMERO_PROCESSO': 'QTD_PROCESSOS', 'NUMERO_SALIC': 'QTD_PROJETOS'}).reset_index()
  df_responsaveis = df_responsaveis.sort_values('QTD_PROCESSOS', ascending=False)
  media_processos = df_responsaveis['QTD_PROCESSOS'].mean()
  
  with st.container(horizontal=True):
    col1, col2, col3 = st.columns([1, 1, 1], gap='large')

    with col1:
      st.metric('Processos em prestação de contas', f'{total_processos}', border=True)
    with col2:
      st.metric('Média de processos por responsável', f'{media_processos:.1f}', border=True)
    with col3:
      st.metric('Responsáveis únicos', f'{df_processos_prest['RESPONSAVEL_PRESTACAO'].nunique()}', border=True)

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

    with col1:
      with st.container(border=True):
        st.markdown("**Top 10 responsáveis por processos**")
        st.table(df_responsaveis.head(10).rename(columns={
          'RESPONSAVEL_PRESTACAO': 'Responsável',
          'QTD_PROCESSOS': 'Processos',
          'QTD_PROJETOS': 'Projetos'
        }), hide_index=True, border='horizontal')
        st.caption(
          'A coluna `Processos` é relativa à quantidade de números de processo, '
          'enquanto `Projetos` refere-se ao número SALIC.'
        )
        
    with col2:
      df_salic_duplicados = df_processos_prest.groupby('NUMERO_SALIC').agg({
        'NUMERO_PROCESSO': 'count',
        'TITULO_PROJETO': 'first'
      }).rename(columns={'NUMERO_PROCESSO': 'QTD_PROCESSOS'}).reset_index()

      df_multiplos = df_salic_duplicados[df_salic_duplicados['QTD_PROCESSOS'] > 1]

      if len(df_multiplos) > 0:
        st.markdown(f":orange-badge[⚠️ Projetos com múltiplos processos em prestação de contas: {len(df_multiplos)}]")
        st.table(
          df_multiplos[['NUMERO_SALIC', 'TITULO_PROJETO', 'QTD_PROCESSOS']].rename(columns={
            'NUMERO_SALIC': 'Nº SALIC',
            'TITULO_PROJETO': 'Projeto',
            'QTD_PROCESSOS': 'Quantidade de processos',
          }),
          hide_index=True
        )
      else:
        st.badge("Nenhum projeto com múltiplos processos identificado.", icon=":material/check:", color="green")
  return