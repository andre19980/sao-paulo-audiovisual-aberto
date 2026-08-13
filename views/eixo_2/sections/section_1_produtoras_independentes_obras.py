import json

import pandas as pd
import streamlit as st
import unicodedata
import altair as alt
import numpy as np

from lib.getters import capitais_brasileiras, uf_capitais_brasileiras
from lib.normalizers import normaliza_cnpj
from lib.checkers import checa_cnpj

from charts.bar import plot_custom_ranking_bar_chart
from charts.hist import plot_custom_histogram_chart
from charts.brazil_map import plot_custom_brazil_map

# Identificar quantas obras audiovisuais são produzidas por empresas sediadas no município vs. por empresas de outros locais.
# Mapear produtoras independentes paulistanas que não acessam mecanismos federais de fomento – alvo potencial para um edital municipal de apoio ao audiovisual.
# Cruzar dados de captação via leis de incentivo (ex.: Art. 1º, 3º, 18 da Lei do Audiovisual) com o município do proponente para avaliar se São Paulo está sendo contemplada adequadamente.

def section(df_produtoras_independentes, df_produtores):  
  produtoras_independentes_cnpj = df_produtoras_independentes['CNPJ'].apply(checa_cnpj)
  
  df_produtoras_independentes['CNPJ_LIMPO'] = df_produtoras_independentes['CNPJ'].apply(normaliza_cnpj)
  df_produtores['CNPJ_LIMPO'] = df_produtores['CNPJ_PRODUTOR'].apply(normaliza_cnpj)
  
  df_merge_produtores = df_produtoras_independentes.merge(
    df_produtores,
    on='CNPJ_LIMPO',
    how='left',
    suffixes=('_produtora_independente', '_produtor')
  )
  
  df_produtividade = df_merge_produtores.groupby(['REGISTRO_ANCINE', 'RAZAO_SOCIAL', 'MUNICIPIO', 'UF']).agg({
    'CPB': 'count',
    'CNPJ': 'first'  # Apenas para referência
  }).rename(columns={'CPB': 'QTD_OBRAS'}).reset_index()

  df_produtividade = df_produtividade.sort_values('QTD_OBRAS', ascending=False)

  df_produtividade_sp = df_produtividade[df_produtividade['MUNICIPIO'] == 'SÃO PAULO']
  top_sp = df_produtividade_sp.head(10)
  
  st.header('Produtoras independentes e obras no município de São Paulo')
  with st.container(horizontal=True, horizontal_alignment='right'):
    if (produtoras_independentes_cnpj == 'CNPJ VÁLIDO').all():
      st.badge("Verificação de CNPJ sem erros", icon=":material/check:", color="green")
    else:
      st.markdown(f":orange-badge[⚠️ CNPJ com inconsistência]") 
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1])

    obras_sp = len(df_merge_produtores[(df_merge_produtores['CPB'].notna()) & (df_merge_produtores['MUNICIPIO'] == 'SÃO PAULO')])
    produtoras_sp = len(df_merge_produtores[df_merge_produtores['MUNICIPIO'] == 'SÃO PAULO']['CNPJ'].unique())
    
    with col1:
      st.metric("Obras não-publicitárias de produtoras independentes", obras_sp, border=True)
      
    with col2:
      st.metric("Produtoras independentes", produtoras_sp, border=True)
      
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1])

    with col1:
      with st.container(border=True):
        faixas = ['0 obras', '1 obra', '2 a 3', '4 a 5', '6 a 10', '11 a 50', 'mais de 50']
        limites = {
          '0 obras': (0, 0),
          '1 obra': (1, 1),
          '2 a 3': (2, 3),
          '4 a 5': (4, 5),
          '6 a 10': (6, 10),
          '11 a 50': (11, 50),
          'mais de 50': (51, 10_000),
        }
        df_faixas = pd.DataFrame({
          'Faixa': faixas,
          'Produtoras': [
            ((df_produtividade_sp['QTD_OBRAS'] >= limites[f][0]) & (df_produtividade_sp['QTD_OBRAS'] <= limites[f][1])).sum()
            for f in faixas
          ],
        })

        plot_custom_histogram_chart(
          df=df_faixas,
          x='Faixa',
          x_title=None,
          y='Produtoras',
          y_title='Número de produtoras',
          faixas=faixas,
          title='Distribuição de produtoras independentes de São Paulo por faixa de obras',
          color_scale_scheme='tableau10'
        )

        st.text(
          'Barras com a quantidade de produtoras paulistanas por faixa de obras registradas na '
          'ANCINE. A enorme barra em "0 obras" mostra que a maioria das produtoras independentes de '
          'São Paulo está registrada mas ainda não tem nenhum vínculo de obra; depois disso, a '
          'frequência cai rapidamente — pouquíssimas produtoras passam de 10 obras.'
        )
    
    with col2:
      with st.container(border=True):
        plot_custom_ranking_bar_chart(
          df=top_sp,
          x='QTD_OBRAS',
          x_title='Número de obras',
          y='RAZAO_SOCIAL',
          y_title=None,
          title='Top 10 produtoras independentes de São Paulo',
          tooltip=['RAZAO_SOCIAL', 'QTD_OBRAS'],
          color='QTD_OBRAS',
          label_limit=280,
        )
        st.caption(
          'O ranking considera apenas produtoras independentes sediadas no município de São Paulo e '
          'conta os vínculos obra-produtora registrados na ANCINE (CPB). Cada barra é uma produtora; '
          'quanto mais longa, mais obras produzidas.'
        )
  

  st.header('Produtoras independentes e obras por estados e capitais brasileiras')
  st.subheader('Distribuição de produtividade e produtoras nas capitais brasileiras')
  df_cidade_stats = df_produtividade.groupby(['UF', 'MUNICIPIO']).agg({
    'QTD_OBRAS': ['sum', 'mean', 'count']
  }).round(2)

  df_cidade_stats.columns = ['TOTAL_OBRAS', 'MEDIA_OBRAS_POR_PRODUTORA', 'TOTAL_PRODUTORAS']
  df_cidade_stats = df_cidade_stats.reset_index()

  def _sem_acentos(texto):
    return unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode().upper().strip()

  uf_capitais = uf_capitais_brasileiras()
  capitais = capitais_brasileiras()
  capitais_norm = {_sem_acentos(c): c for c in capitais}
  uf_esperada = {_sem_acentos(c): uf for c, uf in uf_capitais.items()}
  df_cidade_stats['CAPITAL_NORM'] = df_cidade_stats['MUNICIPIO'].map(_sem_acentos)
  df_capitais = df_cidade_stats[
    df_cidade_stats['CAPITAL_NORM'].isin(capitais_norm)
    & (df_cidade_stats['UF'] == df_cidade_stats['CAPITAL_NORM'].map(uf_esperada))
  ].copy()
  df_capitais = df_capitais.groupby('CAPITAL_NORM', as_index=False).agg({
    'TOTAL_OBRAS': 'sum',
    'MEDIA_OBRAS_POR_PRODUTORA': 'mean',
    'TOTAL_PRODUTORAS': 'sum',
    'UF': 'first',
  })
  df_capitais['MUNICIPIO'] = df_capitais['CAPITAL_NORM'].map(capitais_norm)
  df_capitais = df_capitais.drop(columns=['CAPITAL_NORM'])

  coordenadas_capitais = {
    'RIO BRANCO': (-9.974, -67.806),
    'MACEIÓ': (-9.666, -35.735),
    'MACAPÁ': (0.035, -51.071),
    'MANAUS': (-3.116, -60.028),
    'SALVADOR': (-12.966, -38.501),
    'FORTALEZA': (-3.717, -38.543),
    'BRASÍLIA': (-15.794, -47.883),
    'VITÓRIA': (-20.315, -40.313),
    'GOIÂNIA': (-16.682, -49.251),
    'SÃO LUÍS': (-2.539, -44.286),
    'CUIABÁ': (-15.601, -56.098),
    'CAMPO GRANDE': (-20.470, -54.620),
    'BELO HORIZONTE': (-19.917, -43.935),
    'BELÉM': (-1.456, -48.504),
    'JOÃO PESSOA': (-7.115, -34.878),
    'CURITIBA': (-25.428, -49.273),
    'RECIFE': (-8.048, -34.877),
    'TERESINA': (-5.089, -42.802),
    'RIO DE JANEIRO': (-22.907, -43.173),
    'NATAL': (-5.794, -35.195),
    'PORTO ALEGRE': (-30.033, -51.230),
    'PORTO VELHO': (-8.761, -63.873),
    'BOA VISTA': (2.820, -60.673),
    'FLORIANÓPOLIS': (-27.596, -48.548),
    'SÃO PAULO': (-23.556, -46.640),
    'ARACAJU': (-10.947, -37.073),
    'PALMAS': (-10.212, -48.361),
  }

  df_capitais['Latitude'] = df_capitais['MUNICIPIO'].map(lambda m: coordenadas_capitais[m][0])
  df_capitais['Longitude'] = df_capitais['MUNICIPIO'].map(lambda m: coordenadas_capitais[m][1])

  df_capitais_prod = df_capitais.sort_values('TOTAL_PRODUTORAS', ascending=False)
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1], gap='large')
    
    with col1:
      with st.container(border=True):  
        plot_custom_brazil_map(
          df=df_capitais,
          geojson_path='assets/brazil-states.geojson',
          label='MUNICIPIO',
          size='TOTAL_OBRAS',
          size_title='Total de obras',
          color='MEDIA_OBRAS_POR_PRODUTORA',
          color_title='Média de obras por produtora',
          title='Obras e produtividade média por capital',
          tooltip_fields=['MUNICIPIO', 'TOTAL_OBRAS', 'TOTAL_PRODUTORAS', 'MEDIA_OBRAS_POR_PRODUTORA'],
        )
        st.caption(
          'Mapa do Brasil com as 27 capitais: o tamanho de cada bolinha representa o total de obras '
          'das produtoras locais e a intensidade da cor, a média de obras por produtora. SÃO PAULO e '
          'o RIO DE JANEIRO concentram o maior volume (bolinhas grandes), enquanto VITÓRIA e '
          'PORTO ALEGRE se destacam pela maior produtividade média (cores mais escuras).'
        )
    
    with col2:
      with st.container(border=True):
        plot_custom_ranking_bar_chart(
          df=df_capitais_prod,
          x='TOTAL_PRODUTORAS',
          x_title='Produtoras independentes',
          y='MUNICIPIO',
          y_title=None,
          title='Quantidade de produtoras independentes por capital',
          tooltip=['MUNICIPIO', 'UF', 'TOTAL_PRODUTORAS', 'TOTAL_OBRAS'],
          step=28,
        )
        st.caption(
          'Ranking das 27 capitais pelo número de produtoras independentes registradas na ANCINE '
          'e sediadas na própria cidade. SÃO PAULO (3.091) e RIO DE JANEIRO (2.316) concentram o '
          'maior número de empresas, seguidas de BRASÍLIA e BELO HORIZONTE.'
        )
        

  st.subheader('Distribuição de produtoras e obras por estado')
  # Choropleth: produtoras independentes por estado (UF)
  df_uf_produtoras = (
    df_produtividade.groupby('UF')['REGISTRO_ANCINE']
      .count()
      .rename('TOTAL_PRODUTORAS')
      .reset_index()
      .sort_values('TOTAL_PRODUTORAS', ascending=False)
  )

  with open("assets/brazil-states.geojson", "r") as file:
    geojson_uf = json.load(file)

  df_uf_join = df_uf_produtoras[['UF', 'TOTAL_PRODUTORAS']].set_index('UF')
  for feat in geojson_uf['features']:
    sigla = feat['properties']['sigla']
    if sigla in df_uf_join.index:
      feat['properties']['TOTAL_PRODUTORAS'] = int(df_uf_join.loc[sigla, 'TOTAL_PRODUTORAS'])
    else:
      feat['properties']['TOTAL_PRODUTORAS'] = None

  # Barra de ranking: total de obras por estado
  df_uf_obras = (
    df_produtividade.groupby('UF')['QTD_OBRAS']
      .sum()
      .rename('TOTAL_OBRAS')
      .reset_index()
      .sort_values('TOTAL_OBRAS', ascending=False)
  )
  
  with st.container(horizontal=True):
    col1, col2 = st.columns([1,1], gap='large')
    
    with col1:
      with st.container(border=True):
        choropleth_layer = (
          alt.Chart(alt.Data(values=geojson_uf, format=alt.DataFormat(property='features')))
            .mark_geoshape(stroke='#b6bfc9', strokeWidth=0.7)
            .encode(
              color=alt.Color(
                'properties.TOTAL_PRODUTORAS:Q',
                title='Produtoras independentes',
                scale=alt.Scale(scheme='inferno'),
              ),
              tooltip=[
                alt.Tooltip('properties.name:N', title='Estado'),
                alt.Tooltip('properties.TOTAL_PRODUTORAS:Q', title='Produtoras'),
              ],
            )
        )
      
        # Camada fantasma (grid com subset separado) para impedir que o Altair eleve o
        # GeoJSON ao `data` de nível superior do spec. Se isso acontecer, o Streamlit
        # extrai `data.values`, descarta o `format` do GeoJSON e serializa o
        # FeatureCollection como Arrow — fazendo o mapa renderizar sem nenhum estado.
        dummy_grid = pd.DataFrame({'x': [0.0], 'y': [0.0]})
        grid_layer = (
          alt.Chart(dummy_grid)
            .mark_point(opacity=0, size=0)
            .encode(
              x=alt.X('x:Q', axis=None),
              y=alt.Y('y:Q', axis=None),
            )
        )
      
        choropleth_uf = (
          alt.layer(choropleth_layer, grid_layer)
            .project(type='equalEarth')
            .properties(
              width=760,
              height=620,
              title=alt.TitleParams(
                text='Produtoras independentes por estado',
                anchor='start',
              ),
            )
        )
        st.altair_chart(choropleth_uf)
        st.caption(
          'Mapa do Brasil colorido pelo número de produtoras independentes registradas em cada UF. '
          'Tons mais quentes indicam maior quantidade de produtoras; São Paulo (SP) lidera, seguido '
          'do Rio de Janeiro (RJ).'
        )
    
    with col2:
      with st.container(border=True):
        plot_custom_ranking_bar_chart(
          df=df_uf_obras,
          x='TOTAL_OBRAS',
          x_title='Total de obras',
          y='UF',
          y_title=None,
          title='Total de obras por estado',
          tooltip=['UF', 'TOTAL_OBRAS'],
          label_limit=60,
          step=24,
        )
        st.caption(
          'Ranking dos estados pelo total de obras registradas na ANCINE (soma de todos os vínculos '
          'obra-produtora). SÃO PAULO (SP) e RIO DE JANEIRO (RJ) lideram com folga, concentrando a '
          'maior parte da produção audiovisual brasileira.'
        )

  return