import pandas as pd
import numpy as np
import re

from lib.normalizers import normaliza_municipio

def checa_cnpj(cnpj):
  """Verifica se o CNPJ está no formato XX.XXX.XXX/XXXX-XX (14 dígitos).

  Retorna 'CNPJ VÁLIDO' quando o formato está correto; caso contrário,
  retorna o próprio valor recebido (inclusive vazio ou NaN).
  """
  if pd.isna(cnpj) or cnpj == '':
    return cnpj
  if re.fullmatch(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', str(cnpj).strip()):
    return 'CNPJ VÁLIDO'
  elif re.fullmatch(r'\d{3}\.\d{3}\.\d{3}/\d{4}-\d{2}', str(cnpj).strip()):
    return 'CNPJ MAL FORMATADO'
  return cnpj

def checa_municipio(s):
  normalized_to_original = {}

  for original_municipio in s.unique():
    normalized = normaliza_municipio(original_municipio)
    if normalized not in normalized_to_original:
      normalized_to_original[normalized] = []
    normalized_to_original[normalized].append(original_municipio)

  conflicting_municipalities = {k: v for k, v in normalized_to_original.items() if len(v) > 1}

  return conflicting_municipalities