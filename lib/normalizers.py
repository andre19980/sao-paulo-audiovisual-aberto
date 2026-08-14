import unicodedata

import pandas as pd
import numpy as np

def normaliza_cnpj(cnpj):
  if pd.isna(cnpj) or cnpj == 'PESSOA FÍSICA':
    return np.nan
  cnpj_limpo = str(cnpj).replace('.', '').replace('/', '').replace('-', '').strip()

  # Alguns CNPJs chegam com um "0" (zero) extra no início; descarta o dígito de
  # excesso e fica com a parte subsequente.
  if len(cnpj_limpo) > 14 and cnpj_limpo.startswith('0'):
    cnpj_limpo = cnpj_limpo[1:]
  return cnpj_limpo

def normaliza_municipio(municipio):
  if pd.isna(municipio):
    return np.nan
  return unicodedata.normalize('NFD', str(municipio)).encode('ascii', 'ignore').decode().upper().strip()

def converte_moeda(valor_str):
  if pd.isna(valor_str) or valor_str == '':
    return 0.0
  valor_limpo = str(valor_str).replace('R$ ', '').replace('.', '').replace(',', '.').strip()
  try:
    return float(valor_limpo)
  except:
    return 0.0