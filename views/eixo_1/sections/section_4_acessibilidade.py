import streamlit as st
import altair as alt
import pandas as pd
import json
import unicodedata

from charts.bar import plot_custom_grouped_bar_chart
from charts.brazil_map import plot_custom_choropleth_brazil_map


def section(df_salas_complexos):
  st.header('Acessibilidade física')

  acessibilidade_criterios = [
    'ASSENTOS_SALA',
    'ASSENTOS_CADEIRANTES',
    'ASSENTOS_MOBILIDADE_REDUZIDA',
    'ASSENTOS_OBESIDADE',
    'ACESSO_ASSENTOS_COM_RAMPA',
    'ACESSO_SALA_COM_RAMPA',
    'BANHEIROS_ACESSIVEIS'
  ]  
  
  df_salas_acessibilidade_sp = df_salas_complexos[df_salas_complexos['MUNICIPIO_COMPLEXO'] == 'SÃO PAULO'][['NOME_SALA', 'REGISTRO_SALA', 'SITUACAO_SALA', 'REGISTRO_COMPLEXO', 'NOME_COMPLEXO', 'BAIRRO_COMPLEXO', *acessibilidade_criterios]]
  df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'] = df_salas_acessibilidade_sp['BAIRRO_COMPLEXO'].str.lower()
  
  df_acc_sp_func = df_salas_acessibilidade_sp[df_salas_acessibilidade_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'].copy()
  
  # Critérios avaliados como "sala com o recurso"
  df_acc_sp_func['Cadeirantes'] = df_acc_sp_func['ASSENTOS_CADEIRANTES'].fillna(0) > 0
  df_acc_sp_func['Mobilidade reduzida'] = df_acc_sp_func['ASSENTOS_MOBILIDADE_REDUZIDA'].fillna(0) > 0
  df_acc_sp_func['Obesidade'] = df_acc_sp_func['ASSENTOS_OBESIDADE'].fillna(0) > 0
  df_acc_sp_func['Rampa nos assentos'] = df_acc_sp_func['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM'
  df_acc_sp_func['Rampa de acesso à sala'] = df_acc_sp_func['ACESSO_SALA_COM_RAMPA'] == 'SIM'
  df_acc_sp_func['Banheiros acessíveis'] = df_acc_sp_func['BANHEIROS_ACESSIVEIS'] == 'SIM'
  
  porte_faixas_assentos = [0, 50, 100, 200, 400, 1000]
  porte_rotulos_assentos = ['Até 50', '50-100', '100-200', '200-400', 'Acima de 400']
  
  df_acc_sp_func['Faixa de assentos'] = pd.cut(
    df_acc_sp_func['ASSENTOS_SALA'],
    bins=porte_faixas_assentos,
    labels=porte_rotulos_assentos,
    include_lowest=True,
  )
  
  with open("assets/grupos-exibidores-sp.json", "r") as file:
    grupos_exibidores_sp = json.load(file)

  df_acc_sp_cat = df_acc_sp_func.merge(
    df_salas_complexos[['REGISTRO_SALA', 'NOME_GRUPO_EXIBIDOR']],
    on='REGISTRO_SALA',
    how='left',
  )
  df_acc_sp_cat['Categoria do exibidor'] = (
    df_acc_sp_cat['NOME_GRUPO_EXIBIDOR']
      .map(grupos_exibidores_sp)
      .fillna('Outros')
  )
  
  ordem_categorias = ['Privado', 'Público', 'Independente', 'Sem grupo', 'Outros']
  criterios_porte = ['Cadeirantes', 'Mobilidade reduzida', 'Obesidade', 'Rampa nos assentos', 'Rampa de acesso à sala', 'Banheiros acessíveis']
  
  df_cat_acc = (
    df_acc_sp_cat.groupby(['Categoria do exibidor'], observed=True)[criterios_porte]
      .mean()
      .mul(100)
      .reset_index()
  )
  df_cat_acc_melt = df_cat_acc.melt(
    id_vars='Categoria do exibidor',
    var_name='Atributo de acessibilidade',
    value_name='% das salas',
  )
  
  st.subheader('Proporção de salas com acessibilidade física no município de São Paulo')
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

    with col1:
      with st.container(border=True):
        # Porcentagem de salas de cada faixa que possui o recurso, em formato longo p/ Altair.
        df_porte_acc = (
          df_acc_sp_func.groupby(['Faixa de assentos'], observed=True)[criterios_porte]
            .mean()
            .mul(100)
            .reset_index()
        )
    
        df_porte_acc_melt = df_porte_acc.melt(id_vars='Faixa de assentos', var_name='Atributo de acessibilidade', value_name='% das salas')

        plot_custom_grouped_bar_chart(
          df=df_porte_acc_melt.dropna(),
          x='Faixa de assentos',
          x_title='Quantidade de assentos na sala',
          y='% das salas',
          y_title='% das salas com o recurso',
          x_offset='Atributo de acessibilidade',
          x_offset_title='Atributo de acessibilidade',
          title='Proporção de salas com acessibilidade por porte da sala (2026)',
          x_scale_sort=porte_rotulos_assentos,
        )
        st.text('Salas pequenas (até 100 lugares) têm proporção muito menor de assentos para mobilidade reduzida e obesidade do que salas médias/grandes. Assentos para cadeirantes são praticamente universais em todos os portes. Rampa de acesso à sala é o critério mais raro, independentemente do porte.')


    with col2:
      with st.container(border=True):        
        plot_custom_grouped_bar_chart(
          df=df_cat_acc_melt.dropna(),
          x='Categoria do exibidor',
          x_title='Categoria do exibidor',
          y='% das salas',
          y_title='% das salas com o recurso',
          x_offset='Atributo de acessibilidade',
          x_offset_title='Atributo de acessibilidade',
          title='Proporção de salas com acessibilidade por categoria de exibidor (2026)',
          x_scale_sort=ordem_categorias,
        )
        st.text('Salas de exibidores sem grupo têm os menores percentuais de banheiros acessíveis, assentos para cadeirantes e rampas. Exibidores públicos se destacam pela rampa de acesso à sala, mas têm banheiros acessíveis, assentos de mobilidade reduzida e obesidade em menor proporção que os privados.')

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')
    with col1:
      with st.container(border=True):
        df_accel_cat = df_acc_sp_cat.groupby('Categoria do exibidor', observed=True).apply(
          lambda g: pd.Series({
            'Assentos acessíveis': (
              g['ASSENTOS_CADEIRANTES'].fillna(0) + g['ASSENTOS_MOBILIDADE_REDUZIDA'].fillna(0) + g['ASSENTOS_OBESIDADE'].fillna(0)
            ).sum(),
            'Total de assentos': g['ASSENTOS_SALA'].sum(),
          }),
          include_groups=False,
        ).reset_index()
        df_accel_cat['Proporção de assentos acessíveis (%)'] = (
          df_accel_cat['Assentos acessíveis'] / df_accel_cat['Total de assentos'] * 100
        ).round(2)

        bar_prop_cat = (
          alt.Chart(df_accel_cat)
            .mark_bar(cornerRadiusEnd=3)
            .encode(
              x=alt.X('Categoria do exibidor:N', title='Categoria do exibidor', sort=ordem_categorias),
              y=alt.Y('Proporção de assentos acessíveis (%):Q', title='% dos assentos destinado a Pessoas com Deficiência'),
              color=alt.Color('Categoria do exibidor:N', title='Categoria do exibidor'),
              tooltip=['Categoria do exibidor', 'Assentos acessíveis', 'Total de assentos', 'Proporção de assentos acessíveis (%)'],
            )
            .properties(
              height=500,
              title=alt.TitleParams(
                text='Proporção real dos assentos acessíveis por categoria de exibidor (2026)',
                anchor='start',
              ),
            )
        )
        st.altair_chart(bar_prop_cat)
        st.caption('Mede a quantidade efetiva de assentos acessíveis em relação ao total, não apenas se a oferta existe. Na proporção real, exibidores públicos destinam a menor fração de seus assentos a esse público, mesmo tendo boa presença de rampas.')

    with col2:
      with st.container(border=True):      
        df_acc_salas = df_acc_sp_cat.copy()
        df_acc_salas['Índice (0-6)'] = df_acc_salas[criterios_porte].sum(axis=1)
      
        # Limita aos 4 grupos de interesse para evitar a categoria 'Outros' residual.
        df_acc_salas_hm = df_acc_salas[df_acc_salas['Categoria do exibidor'].isin(
          ['Privado', 'Público', 'Independente', 'Sem grupo']
        )]
      
        df_indice_heatmap = (
          df_acc_salas_hm.groupby(['Categoria do exibidor', 'Índice (0-6)'])
            .size()
            .reset_index(name='Número de salas')
        )
        indices_possiveis = list(range(0, 7))
        categorias_heatmap = ['Privado', 'Público', 'Independente', 'Sem grupo']
        grid_indice = pd.DataFrame(
          [(cat, i) for cat in categorias_heatmap for i in indices_possiveis],
          columns=['Categoria do exibidor', 'Índice (0-6)'],
        )
        df_indice_heatmap = grid_indice.merge(df_indice_heatmap, on=['Categoria do exibidor', 'Índice (0-6)'], how='left').fillna({'Número de salas': 0})
        df_indice_heatmap['Número de salas'] = df_indice_heatmap['Número de salas'].astype(int)
      
        heatmap_indice = (
          alt.Chart(df_indice_heatmap)
            .mark_rect(stroke='white', strokeWidth=2)
            .encode(
              x=alt.X('Índice (0-6):O', title='Índice composto (0-6)', scale=alt.Scale(paddingInner=0), axis=alt.Axis(labelAngle=0)),
              y=alt.Y('Categoria do exibidor:O', title='Categoria do exibidor', scale=alt.Scale(paddingInner=0)),
              color=alt.Color('raiz_salas:Q', title='Número de salas', scale=alt.Scale(scheme='turbo')),
              tooltip=['Categoria do exibidor', 'Índice (0-6)', 'Número de salas'],
            )
            .transform_calculate(raiz_salas='sqrt(datum["Número de salas"])')
            .properties(
              width={'step': 70},
              height={'step': 70},
              title=alt.TitleParams(
                text='Distribuição do índice composto de acessibilidade por categoria de exibidor (2026)',
                anchor='start',
              ),
            )
        )
        st.altair_chart(heatmap_indice)
        st.caption('Heatmap da contagem de salas por categoria e pontuação do índice (0-6, um ponto por recurso atendido: assentos para cadeirantes, mobilidade reduzida, obesidade, rampas nos assentos, rampa de acesso à sala e banheiros acessíveis). A cor usa escala de raiz quadrada, para que valores pequenos (1, 6, 8, 13) tenham contraste sem que o pico (251) esmague tudo; o número real aparece ao passar o mouse.')
      
        criterio_1 = (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'] > 0)
        criterio_2 = (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'] > 0)
        criterio_3 = (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'] > 0)
        criterio_4 = (df_salas_acessibilidade_sp['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM')
        criterio_5 = (df_salas_acessibilidade_sp['ACESSO_SALA_COM_RAMPA'] == 'SIM')
        criterio_6 = (df_salas_acessibilidade_sp['BANHEIROS_ACESSIVEIS'] == 'SIM')

        st.text('Há apenas uma sala em São Paulo que possui todos os requisitos de acessibilidade')
        st.dataframe(df_salas_acessibilidade_sp[criterio_1 & criterio_2 & criterio_3 & criterio_4 & criterio_5 & criterio_6], hide_index=True)

  st.subheader('Acessibilidade e vulnerabilidade social por distrito no município de São Paulo')
  with st.container(border=True):

    # Mapeia o bairro (informal) registrado na ANCINE para o distrito oficial do
    # município (recorte do IPVS 2022, SEADE), que é a unidade de referência do índice.
    with open("assets/bairros-distritos.json", "r") as file:
      BAIRRO_DISTRITO = json.load(file)

    # Cada entrada: (% de moradores em vulnerabilidade alta - grupos 5 e 6 do IPVS,
    # % em vulnerabilidade baixa - grupos 1 e 2). Fonte: SEADE, IPVS 2022.
    # https://repositorio.seade.gov.br/dataset/ipvs-tabelas/resource/382bcf29-3e79-4c02-90d4-5c3f9c4a4c01?inner_span=True
    with open("assets/ipvs-distritos.json", "r") as file:
      IPVS_DISTRITOS = json.load(file)

    def _sem_acentos(texto):
      texto = unicodedata.normalize('NFD', str(texto))
      return ''.join(c for c in texto if unicodedata.category(c) != 'Mn').lower().strip()

    df_vuln = df_acc_sp_func.copy()
    df_vuln['Distrito'] = df_vuln['BAIRRO_COMPLEXO'].map(lambda b: BAIRRO_DISTRITO.get(_sem_acentos(b)))
    df_vuln = df_vuln.dropna(subset=['Distrito'])
    df_vuln['Índice (0-6)'] = df_vuln[criterios_porte].sum(axis=1)

    df_vuln_agg = df_vuln.groupby('Distrito').agg(
      Salas=('NOME_SALA', 'size'),
      Indice_medio=('Índice (0-6)', 'mean'),
    ).reset_index()
    df_vuln_agg['Vuln alta (%)'] = df_vuln_agg['Distrito'].map(lambda d: IPVS_DISTRITOS[d][0])
    df_vuln_agg['Vuln baixa (%)'] = df_vuln_agg['Distrito'].map(lambda d: IPVS_DISTRITOS[d][1])
    df_vuln_agg['Altamente vulnerável'] = df_vuln_agg['Vuln alta (%)'] >= 40

    df_vuln_agg = df_vuln_agg.sort_values('Vuln alta (%)', ascending=False)

    bubble_vuln = (
      alt.Chart(df_vuln_agg)
        .mark_circle(opacity=0.85)
        .encode(
          x=alt.X('Vuln alta (%):Q', title='População em vulnerabilidade alta (IPVS 2022, %)', scale=alt.Scale(zero=False)),
          y=alt.Y('Indice_medio:Q', title='Índice médio de acessibilidade (0-6)', scale=alt.Scale(zero=False)),
          size=alt.Size('Salas:Q', title='Salas em funcionamento', scale=alt.Scale(range=[40, 900])),
          color=alt.Color('Altamente vulnerável:N', title='≥ 40% em vulnerabilidade alta', scale=alt.Scale(scheme='set1')),
          tooltip=['Distrito', 'Salas', 'Indice_medio', 'Vuln alta (%)', 'Vuln baixa (%)'],
        )
        .properties(
          height=460,
          title=alt.TitleParams(
            text='Oferta acessível de cinema por distrito por vulnerabilidade social (2026)',
            anchor='start',
          ),
        )
    )
    st.altair_chart(bubble_vuln)
    st.caption('Cada bolha é um distrito: eixo X é a parcela da população em grupos de alta vulnerabilidade (IPVS 2022, grupos 5-6); eixo Y, o índice médio de acessibilidade das salas em funcionamento; o tamanho, o número de salas. Distritos com alta vulnerabilidade tendem a concentrar poucas salas — e, em geral, de menor acessibilidade.')

    distritos_sem_sala = sorted(
      {d for d in IPVS_DISTRITOS if IPVS_DISTRITOS[d][0] >= 40} - set(df_vuln_agg['Distrito'])
    )
    if distritos_sem_sala:
      st.write('**Distritos com ≥ 40% da população em alta vulnerabilidade e sem nenhuma sala de cinema:** ' + ', '.join(distritos_sem_sala) + '.')

  
  st.subheader('Diagnóstico de acessibilidade por estado (UF)')

  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

    df_uf = df_salas_complexos[df_salas_complexos['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'].copy()

    for col in ['ASSENTOS_CADEIRANTES', 'ASSENTOS_MOBILIDADE_REDUZIDA', 'ASSENTOS_OBESIDADE']:
      df_uf[col] = df_uf[col].fillna(0) > 0

    df_uf['Cadeirantes'] = df_uf['ASSENTOS_CADEIRANTES']
    df_uf['Mobilidade reduzida'] = df_uf['ASSENTOS_MOBILIDADE_REDUZIDA']
    df_uf['Obesidade'] = df_uf['ASSENTOS_OBESIDADE']
    df_uf['Rampa nos assentos'] = df_uf['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM'
    df_uf['Rampa de acesso à sala'] = df_uf['ACESSO_SALA_COM_RAMPA'] == 'SIM'
    df_uf['Banheiros acessíveis'] = df_uf['BANHEIROS_ACESSIVEIS'] == 'SIM'

    criterios_uf = ['Cadeirantes', 'Mobilidade reduzida', 'Obesidade', 'Rampa nos assentos', 'Rampa de acesso à sala', 'Banheiros acessíveis']
    df_uf['Índice (0-6)'] = df_uf[criterios_uf].sum(axis=1)

    df_uf_agg = df_uf.groupby('UF_COMPLEXO').agg({
      'NOME_SALA': 'size',
      'Índice (0-6)': 'mean',
    }).rename(columns={'NOME_SALA': 'Salas', 'Índice (0-6)': 'Índice médio'}).reset_index()

    # Percentuais de salas com cada recurso por UF, para tooltip e ranking adicional
    for crit in criterios_uf:
      df_uf_agg[f'% {crit}'] = df_uf.groupby('UF_COMPLEXO')[crit].mean().mul(100).round(1).values

    df_uf_agg = df_uf_agg.sort_values('Índice médio', ascending=False).reset_index(drop=True)
    df_uf_agg['Posição'] = df_uf_agg.index + 1

    df_uf_heat = df_uf_agg.melt(
      id_vars=['UF_COMPLEXO'],
      value_vars=[f'% {c}' for c in criterios_uf],
      var_name='Critério',
      value_name='% de salas',
    )
    df_uf_heat['Critério'] = df_uf_heat['Critério'].str.replace('% ', '', regex=False)

    heatmap_uf = (
      alt.Chart(df_uf_heat)
        .mark_rect()
        .encode(
          x=alt.X('Critério:N', title=None, axis=alt.Axis(labelAngle=70, labelLimit=180, labelPadding=8, labelOverlap=True)),
          y=alt.Y('UF_COMPLEXO:N', title='Estado (ordenado pelo índice médio)', sort=df_uf_agg['UF_COMPLEXO'].tolist()),
          color=alt.Color('% de salas:Q', title='% de salas com o recurso', scale=alt.Scale(scheme='inferno', domain=[0, 100])),
          tooltip=['UF_COMPLEXO', 'Critério', '% de salas'],
        )
        .properties(
          width='container',
          height={ 'step': 22 },
          title=alt.TitleParams(
            text='Ranking dos estados por índice médio de acessibilidade das salas em funcionamento (2026)',
            anchor='start',
          ),
        )
    )

    
    with col1:
      with st.container(border=True):
        df_uf_agg_map = df_uf_agg.rename(columns={'UF_COMPLEXO': 'UF'})
        plot_custom_choropleth_brazil_map(
          df=df_uf_agg_map,
          geojson_path='assets/brazil-states.geojson',
          uf_col='UF',
          value_col='Índice médio',
          value_title='Índice médio (0-6)',
          title='Média de acessibilidade de salas em funcionamento por estado (2026)',
          color_domain=[0, 6],
          tooltip_extra={'Salas': 'Salas em funcionamento'},
        )
        st.caption(
          'Mapa do Brasil colorido pela média de acessibilidade das salas em funcionamento '
          'de cada estado (índice composto 0-6, um ponto por recurso: assentos para cadeirantes, '
          'mobilidade reduzida, obesidade, rampa nos assentos, rampa de acesso à sala e banheiros '
          'acessíveis). Tons mais quentes indicam estados com cobertura média maior; estados sem '
          'sala em funcionamento ou sem dado ficam sem preenchimento. Roraima lidera (4,85) e '
          'o Acre tem a menor média (2,43).'
        )

    with col2:
      with st.container(border=True):
        st.altair_chart(heatmap_uf)
        st.caption('Ranking das UFs pelo índice composto médio (0-6, um ponto por recurso: assentos para cadeirantes, mobilidade reduzida, obesidade, rampa nos assentos, rampa de acesso à sala e banheiros acessíveis), considerando apenas salas em funcionamento. Cada célula é o percentual de salas da UF que atende ao critério; quanto mais quente, maior a cobertura. As UFs estão ordenadas pelo índice composto médio — no topo Roraima (4,85) e no fim Acre (2,43). O líder é Roraima (4,85) e o último, Acre (2,43). A variância é maior nos critérios mais raros: rampa de acesso à sala (de 0% no Acre a 48,5% no Mato Grosso) e banheiros acessíveis (de 37% em Tocantins a 100% no Acre).')
