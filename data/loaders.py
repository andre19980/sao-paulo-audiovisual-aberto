import streamlit as st
import pandas as pd

import io
import zipfile
import urllib.request

from lib.checkers import checa_municipio

@st.cache_data(scope='session')
def load_data(url):
  data = pd.read_csv(url, sep=';')

  return data

@st.cache_data(scope='session', ttl=86400)
def load_obras_brasileiras(url):
  """Baixa o ZIP de obras não publicitárias brasileiras e concatena os CSVs anuais.

  O arquivo contém um CSV por ano (2002-2026), todos com o mesmo cabeçalho.
  O download + descompactação acontecem em memória (io.BytesIO), sem gravar em disco.
  """
  req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  raw = urllib.request.urlopen(req, timeout=120).read()
  zip_bytes = io.BytesIO(raw)

  frames = []
  with zipfile.ZipFile(zip_bytes) as zf:
    for name in zf.namelist():
      if not name.endswith('.csv'):
        continue
      ano = name.rsplit('-', 1)[1].split('.')[0]
      df_ano = pd.read_csv(
        zf.open(name),
        sep=';',
        encoding='utf-8-sig',
      )
      df_ano['ANO'] = int(ano)
      frames.append(df_ano)

  df = pd.concat(frames, ignore_index=True)
  
  municipios_conflitantes = checa_municipio(df['MUNICIPIO_REQUERENTE'])
  for normalizado, original in municipios_conflitantes.items():
    df['MUNICIPIO_REQUERENTE'] = df['MUNICIPIO_REQUERENTE'].replace(original, normalizado)

  return df
