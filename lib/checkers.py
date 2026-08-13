import pandas as pd
import numpy as np
import re

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