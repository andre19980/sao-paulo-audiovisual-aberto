import streamlit as st
import altair as alt
import pandas as pd
import json
import unicodedata
from charts.bar import plot_custom_grouped_bar_chart

def section(df_salas_complexos):
  st.header('4. Acessibilidade física')
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1, 1], gap='large')

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

    # ---------------------------------------------------------------------------
    # (1a) Porte da sala x Acessibilidade (São Paulo, em funcionamento)
    # ---------------------------------------------------------------------------
    df_acc_sp_func = df_salas_acessibilidade_sp[df_salas_acessibilidade_sp['SITUACAO_SALA'] == 'EM FUNCIONAMENTO'].copy()

    porte_faixas_assentos = [0, 50, 100, 200, 400, 1000]
    porte_rotulos_assentos = ['Até 50', '50-100', '100-200', '200-400', 'Acima de 400']
    df_acc_sp_func['Faixa de assentos'] = pd.cut(
      df_acc_sp_func['ASSENTOS_SALA'],
      bins=porte_faixas_assentos,
      labels=porte_rotulos_assentos,
      include_lowest=True,
    )

    # Critérios avaliados como "sala com o recurso". Os três primeiros usam >0 assentos;
    # os demais são presença (SIM/NÃO).
    df_acc_sp_func['Cadeirantes'] = df_acc_sp_func['ASSENTOS_CADEIRANTES'].fillna(0) > 0
    df_acc_sp_func['Mobilidade reduzida'] = df_acc_sp_func['ASSENTOS_MOBILIDADE_REDUZIDA'].fillna(0) > 0
    df_acc_sp_func['Obesidade'] = df_acc_sp_func['ASSENTOS_OBESIDADE'].fillna(0) > 0
    df_acc_sp_func['Rampa nos assentos'] = df_acc_sp_func['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM'
    df_acc_sp_func['Rampa de acesso à sala'] = df_acc_sp_func['ACESSO_SALA_COM_RAMPA'] == 'SIM'
    df_acc_sp_func['Banheiros acessíveis'] = df_acc_sp_func['BANHEIROS_ACESSIVEIS'] == 'SIM'

    criterios_porte = ['Cadeirantes', 'Mobilidade reduzida', 'Obesidade', 'Rampa nos assentos', 'Rampa de acesso à sala', 'Banheiros acessíveis']

    # Porcentagem de salas de cada faixa que possui o recurso, em formato longo p/ Altair.
    df_porte_acc = (
      df_acc_sp_func.groupby(['Faixa de assentos'], observed=True)[criterios_porte]
        .mean()
        .mul(100)
        .reset_index()
    )

    df_porte_acc_melt = df_porte_acc.melt(id_vars='Faixa de assentos', var_name='Atributo de acessibilidade', value_name='% das salas')

    with col1:
      with st.container(border=True):
        st.subheader('Acessibilidade × Porte da sala')
        
        plot_custom_grouped_bar_chart(
          df=df_porte_acc_melt.dropna(),
          x='Faixa de assentos',
          x_title='Quantidade de assentos na sala',
          y='% das salas',
          y_title='% das salas com o recurso',
          x_offset='Atributo de acessibilidade',
          x_offset_title='Atributo de acessibilidade',
          title='Proporção de salas com acessibilidade por porte da sala (São Paulo, 2026)',
          x_scale_sort=porte_rotulos_assentos,
        )
        st.caption('Salas pequenas (até 100 lugares) têm proporção muito menor de assentos para mobilidade reduzida e obesidade do que salas médias/grandes. Assentos para cadeirantes são praticamente universais em todos os portes. Rampa de acesso à sala é o critério mais raro, independentemente do porte.')

    # ---------------------------------------------------------------------------
    # (1b) Categoria de exibidor x Acessibilidade (São Paulo, em funcionamento)
    # ---------------------------------------------------------------------------
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

    with col2:
      with st.container(border=True):
        st.subheader('Acessibilidade × Categoria do exibidor')

        plot_custom_grouped_bar_chart(
          df=df_cat_acc_melt.dropna(),
          x='Categoria do exibidor',
          x_title='Categoria do exibidor',
          y='% das salas',
          y_title='% das salas com o recurso',
          x_offset='Atributo de acessibilidade',
          x_offset_title='Atributo de acessibilidade',
          title='Proporção de salas com acessibilidade por categoria de exibidor (São Paulo, 2026)',
          x_scale_sort=ordem_categorias,
        )
        st.caption('Salas de exibidores sem grupo têm os menores percentuais de banheiros acessíveis, assentos para cadeirantes e rampas. Exibidores públicos se destacam pela rampa de acesso à sala, mas têm banheiros acessíveis em menor proporção que os privados.')

  # ---------------------------------------------------------------------------
  # (3a) Proporção real de assentos acessíveis por categoria (quantitativo)
  # ---------------------------------------------------------------------------
  st.subheader('Proporção real de assentos acessíveis por categoria de exibidor')

  # Diferente do item 1b (presença SIM/NÃO), aqui usa-se as contagens efetivas:
  # quantos dos assentos totais da categoria são destinados a PcD (cadeirantes,
  # mobilidade reduzida e obesidade).
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
        height=420,
        title=alt.TitleParams(
          text='Proporção real dos assentos acessíveis, por categoria de exibidor (São Paulo, 2026)',
          anchor='middle',
        ),
      )
  )
  st.altair_chart(bar_prop_cat)
  st.caption('Mede a quantidade efetiva de assentos acessíveis em relação ao total, não apenas se a oferta existe. Na proporção real, exibidores públicos destinam a menor fração de seus assentos a esse público, mesmo tendo boa presença de rampas (item 1b).')

  criterio_1 = (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_CADEIRANTES'] > 0)
  criterio_2 = (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_MOBILIDADE_REDUZIDA'] > 0)
  criterio_3 = (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'].notna()) & (df_salas_acessibilidade_sp['ASSENTOS_OBESIDADE'] > 0)
  criterio_4 = (df_salas_acessibilidade_sp['ACESSO_ASSENTOS_COM_RAMPA'] == 'SIM')
  criterio_5 = (df_salas_acessibilidade_sp['ACESSO_SALA_COM_RAMPA'] == 'SIM')
  criterio_6 = (df_salas_acessibilidade_sp['BANHEIROS_ACESSIVEIS'] == 'SIM')

  st.text('Há apenas uma sala em São Paulo que possui todos os requisitos de acessibilidade')
  st.write(df_salas_acessibilidade_sp[criterio_1 & criterio_2 & criterio_3 & criterio_4 & criterio_5 & criterio_6])

  # ---------------------------------------------------------------------------
  # (3c) Índice composto de acessibilidade por sala (heatmap por categoria)
  # ---------------------------------------------------------------------------
  st.subheader('Índice composto de acessibilidade por sala')

  df_acc_salas = df_acc_sp_cat.copy()
  df_acc_salas['Índice (0-6)'] = df_acc_salas[criterios_porte].sum(axis=1)

  # Limita aos 4 grupos de interesse para evitar a categoria 'Outros' residual.
  df_acc_salas_hm = df_acc_salas[df_acc_salas['Categoria do exibidor'].isin(
    ['Privado', 'Público', 'Independente', 'Sem grupo']
  )]

  # Conta quantas salas de cada categoria pontuam em cada índice (0-6).
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

  cell_size=70,

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
          text='Distribuição do índice composto de acessibilidade por categoria de exibidor (São Paulo, 2026)',
          anchor='middle',
        ),
      )
  )
  st.altair_chart(heatmap_indice)
  st.caption('Heatmap da contagem de salas por categoria e pontuação do índice (0-6, um ponto por recurso atendido: assentos para cadeirantes, mobilidade reduzida, obesidade, rampas nos assentos, rampa de acesso à sala e banheiros acessíveis). A cor usa escala de raiz quadrada, para que valores pequenos (1, 6, 8, 13) tenham contraste sem que o pico (251) esmague tudo; o número real aparece ao passar o mouse.')

  # ---------------------------------------------------------------------------
  # (4) Acessibilidade x Vulnerabilidade social (IPVS 2022) por distrito de SP
  # ---------------------------------------------------------------------------
  st.subheader('Acessibilidade × Vulnerabilidade social por distrito')

  # Mapeia o bairro (informal) registrado na ANCINE para o distrito oficial do
  # município (recorte do IPVS 2022, SEADE), que é a unidade de referência do índice.
  BAIRRO_DISTRITO = {
      'agua branca': 'Lapa',
      'arthur alvim': 'Artur Alvim',
      'bela vista': 'Bela Vista',
      'butanta': 'Butantã',
      'centro': 'Sé',
      'consolacao': 'Consolação',
      'cerqueira cesar': 'Consolação',
      'chacara dona olivia': 'Cidade Ademar',
      'chacara santa clara - capao redondo': 'Capão Redondo',
      'cidade tiradentes': 'Cidade Tiradentes',
      'conj. hab. barro branco ii': 'Jaraguá',
      'freguesia do o': 'Freguesia do Ó',
      'guaianazes': 'Guaianases',
      'heliopolis': 'Sacomã',
      'higienopolis': 'Santa Cecília',
      'ipiranga': 'Ipiranga',
      'ipiranga.': 'Ipiranga',
      'itaim bibi': 'Itaim Bibi',
      'itaim paulista': 'Itaim Paulista',
      'jardim boa vista': 'São Lucas',
      'jardim da saude': 'Saúde',
      'jardim iguatemi': 'Iguatemi',
      'jardim iris': 'Cidade Ademar',
      'jardim paulista': 'Jardim Paulista',
      'jardim paulistano': 'Morumbi',
      'jardim pirituba': 'Pirituba',
      'jd. guedala': 'Mooca',
      'jabaquara': 'Jabaquara',
      'jaragua': 'Jaraguá',
      'jardim esmeralda': 'Itaquera',
      'jardim guapira': 'Jaçanã',
      'jardim noronha': 'Vila Prudente',
      'jardim parana': 'Santana',
      'jardim santa terezinha': 'Vila Formosa',
      'jardim sao pedro': 'Ipiranga',
      'jardim sao vicente': 'Pirituba',
      'lapa': 'Lapa',
      'lauzane paulista': 'Mandaqui',
      'morumbi': 'Morumbi',
      'parada inglesa': 'Casa Verde',
      'paraiso': 'Vila Mariana',
      'penha de franca': 'Penha',
      'perdizes': 'Perdizes',
      'pinheiros': 'Pinheiros',
      'ponte pequena': 'Tremembé',
      'parque casa de pedra': 'Cidade Ademar',
      'parque cisper': 'Cidade Ademar',
      'parque continental': 'Vila Sônia',
      'parque do carmo': 'Parque do Carmo',
      'pirituba': 'Pirituba',
      'republica': 'República',
      'santa cecilia': 'Santa Cecília',
      'santa ifigenia': 'República',
      'santo amaro': 'Santo Amaro',
      'sao joao climaco': 'São Lucas',
      'sao rafael': 'São Rafael',
      'tatuape': 'Tatuapé',
      'vila andrade': 'Vila Andrade',
      'vila buarque': 'República',
      'vila campanela': 'Sacomã',
      'vila cordeiro': 'Vila Medeiros',
      'vila guilherme': 'Vila Guilherme',
      'vila inglesa': 'Vila Mariana',
      'vila mariana': 'Vila Mariana',
      'vila matilde': 'Vila Matilde',
      'vila olimpia': 'Itaim Bibi',
      'vila prel': 'Sé',
      'vila prudente': 'Vila Prudente',
      'vila romana': 'Lapa',
      'vila gertrudes': 'Sacomã',
      'vila maria': 'Vila Maria',
      'vila nova conceicao': 'Itaim Bibi',
      'vila do sol': 'Tremembé',
  }

  # Cada entrada: (% de moradores em vulnerabilidade alta - grupos 5 e 6 do IPVS,
  # % em vulnerabilidade baixa - grupos 1 e 2). Fonte: SEADE, IPVS 2022.
  # https://repositorio.seade.gov.br/dataset/ipvs-tabelas/resource/382bcf29-3e79-4c02-90d4-5c3f9c4a4c01?inner_span=True
  IPVS_DISTRITOS = {
      'Água Rasa': (0.00, 91.18),
      'Alto de Pinheiros': (0.00, 97.61),
      'Anhanguera': (32.98, 41.42),
      'Aricanduva': (6.92, 74.48),
      'Artur Alvim': (8.19, 76.54),
      'Barra Funda': (6.53, 84.52),
      'Bela Vista': (0.00, 70.73),
      'Belém': (4.76, 68.54),
      'Bom Retiro': (16.47, 58.97),
      'Brás': (13.57, 41.16),
      'Brasilândia': (52.04, 26.61),
      'Butantã': (1.15, 79.07),
      'Cachoeirinha': (28.56, 51.39),
      'Cambuci': (0.16, 67.77),
      'Campo Belo': (7.58, 90.66),
      'Campo Grande': (3.49, 90.36),
      'Campo Limpo': (31.80, 44.73),
      'Cangaiba': (18.12, 68.64),
      'Capão Redondo': (44.04, 29.01),
      'Carrão': (2.30, 94.82),
      'Casa Verde': (1.08, 87.34),
      'Cidade Ademar': (42.30, 34.93),
      'Cidade Dutra': (25.35, 59.02),
      'Cidade Lider': (15.84, 70.51),
      'Cidade Tiradentes': (52.21, 21.06),
      'Consolação': (0.00, 83.51),
      'Cursino': (7.78, 77.70),
      'Ermelino Matarazzo': (24.12, 52.52),
      'Freguesia do Ó': (6.30, 81.74),
      'Grajaú': (60.91, 16.90),
      'Guaianases': (32.64, 35.79),
      'Moema': (0.00, 99.66),
      'Iguatemi': (53.31, 20.48),
      'Ipiranga': (12.61, 76.02),
      'Itaim Bibi': (0.30, 98.40),
      'Itaim Paulista': (30.19, 33.22),
      'Itaquera': (15.15, 59.97),
      'Jabaquara': (20.38, 63.32),
      'Jaçanã': (26.00, 57.96),
      'Jaguara': (4.79, 80.23),
      'Jaguaré': (29.28, 51.89),
      'Jaraguá': (24.16, 52.33),
      'Jardim Ângela': (70.14, 10.96),
      'Jardim Helena': (46.79, 24.10),
      'Jardim Paulista': (0.00, 98.83),
      'Jardim São Luís': (37.74, 39.76),
      'José Bonifácio': (21.67, 57.17),
      'Lapa': (1.22, 95.38),
      'Liberdade': (0.00, 70.52),
      'Limão': (6.72, 79.56),
      'Mandaqui': (2.79, 83.60),
      'Marsilac': (40.55, 10.76),
      'Mooca': (0.18, 88.19),
      'Morumbi': (14.53, 75.65),
      'Parelheiros': (59.30, 11.67),
      'Pari': (9.66, 64.83),
      'Parque do Carmo': (24.93, 48.80),
      'Pedreira': (56.87, 25.31),
      'Penha': (5.69, 77.36),
      'Perdizes': (0.00, 98.47),
      'Perus': (44.59, 42.13),
      'Pinheiros': (0.00, 98.04),
      'Pirituba': (15.60, 62.42),
      'Ponte Rasa': (5.86, 84.66),
      'Raposo Tavares': (25.06, 42.32),
      'República': (3.65, 60.36),
      'Rio Pequeno': (20.59, 58.38),
      'Sacomã': (25.09, 58.08),
      'Santa Cecília': (0.44, 85.13),
      'Santana': (0.91, 98.33),
      'Santo Amaro': (0.00, 96.66),
      'São Lucas': (7.48, 86.31),
      'São Mateus': (14.54, 62.72),
      'São Miguel': (15.02, 69.99),
      'São Rafael': (53.39, 30.87),
      'Sapopemba': (28.80, 46.43),
      'Saúde': (1.00, 95.49),
      'Sé': (6.87, 29.06),
      'Socorro': (5.61, 83.08),
      'Tatuapé': (0.90, 92.64),
      'Tremembé': (44.38, 43.80),
      'Tucuruvi': (0.23, 95.32),
      'Vila Andrade': (40.78, 51.95),
      'Vila Curuçá': (19.74, 51.83),
      'Vila Formosa': (0.59, 92.66),
      'Vila Guilherme': (2.30, 90.78),
      'Vila Jacuí': (33.83, 47.04),
      'Vila Leopoldina': (6.52, 89.94),
      'Vila Maria': (22.21, 54.91),
      'Vila Mariana': (0.98, 96.17),
      'Vila Matilde': (1.52, 85.55),
      'Vila Medeiros': (12.19, 73.45),
      'Vila Prudente': (6.14, 80.74),
      'Vila Sônia': (23.74, 69.07),
      'São Domingos': (21.52, 68.63),
      'Lajeado': (46.90, 18.93),
  }
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
          text='Oferta acessível de cinema por distrito × vulnerabilidade social (São Paulo, 2026)',
          anchor='middle',
        ),
      )
  )
  st.altair_chart(bubble_vuln)
  st.caption('Cada bolha é um distrito: eixo X é a parcela da população em grupos de alta vulnerabilidade (IPVS 2022, grupos 5-6); eixo Y, o índice médio de acessibilidade das salas em funcionamento; o tamanho, o número de salas. Distritos com alta vulnerabilidade tendem a concentrar poucas salas — e, em geral, de menor acessibilidade. Nove dos distritos mais vulneráveis não têm nenhuma sala de cinema: Jardim Ângela, Grajaú, Parelheiros, Pedreira, Brasilândia, Lajeado, Jardim Helena, Perus e Marsilac.')

  distritos_sem_sala = sorted(
    {d for d in IPVS_DISTRITOS if IPVS_DISTRITOS[d][0] >= 40} - set(df_vuln_agg['Distrito'])
  )
  if distritos_sem_sala:
    st.write('**Distritos com ≥ 40% da população em alta vulnerabilidade e sem nenhuma sala de cinema:** ' + ', '.join(distritos_sem_sala) + '.')

  # ---------------------------------------------------------------------------
  # (6) Diagnóstico de acessibilidade por UF (ranking)
  # ---------------------------------------------------------------------------
  st.subheader('Diagnóstico de acessibilidade por estado (UF)')

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

  bar_uf = (
    alt.Chart(df_uf_agg)
      .mark_bar(cornerRadiusEnd=3)
      .encode(
        y=alt.Y('UF_COMPLEXO:N', title='Estado', sort='-x', axis=alt.Axis(labelOverlap=False, labelLimit=100, labelPadding=6)),
        x=alt.X('Índice médio:Q', title='Índice médio de acessibilidade (0-6)', scale=alt.Scale(domain=[0, 6])),
        color=alt.Color('Índice médio:Q', title='Índice médio', scale=alt.Scale(scheme='blues')),
        tooltip=['Posição', 'UF_COMPLEXO', 'Salas', 'Índice médio', '% Rampa de acesso à sala', '% Banheiros acessíveis'],
      )
      .properties(
        height={'step': 22},
        title=alt.TitleParams(
          text='Ranking dos estados por índice médio de acessibilidade das salas em funcionamento (2026)',
          anchor='middle',
        ),
      )
  )
  st.altair_chart(bar_uf)
  st.caption('Ranking das UFs pelo índice composto médio (0-6, um ponto por recurso: assentos para cadeirantes, mobilidade reduzida, obesidade, rampa nos assentos, rampa de acesso à sala e banheiros acessíveis), considerando apenas salas em funcionamento. A barra mais clara (menor índice) indica menor acessibilidade média. O líder é Roraima (4,85) e o último, Acre (2,43). A variância é maior nos critérios mais raros: rampa de acesso à sala (de 0% no Acre a 48,5% no Mato Grosso) e banheiros acessíveis (de 37% em Tocantins a 100% no Acre).')
