import unicodedata
from enum import Enum
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
  if pd.isna(valor_str) or valor_str == '' or valor_str == 'R$ 0,00':
    return 0.0
  valor_limpo = str(valor_str).replace('R$ ', '').replace('.', '').replace(',', '.').strip()
  try:
    return float(valor_limpo)
  except:
    return 0.0

class Tipo(Enum):
  FICCAO = 'Ficção'
  DOCUMENTARIO = 'Documentário'
  PUBLICIDADE = 'Publicitária'
  NAO_PUBLICITARIA = 'Não publicitária'
  REALITY = 'Reality Show'
  VIDEOCLIPE = 'Videoclipe'
  MUSICA = 'Música / Music Video'
  PROGRAMA = 'Programa'
  VARIEDADES = 'Variedades'
  ENTREVISTA = 'Entrevista'
  NOTICIAS = 'Notícias'
  INSTITUCIONAL = 'Institucional'
  CORPORATIVO = 'Corporativo'
  EDUCATIVO = 'Educativo'
  STREAMING = 'Streaming'
  REDES_SOCIAIS = 'Redes Sociais'
  BANCO_IMAGENS = 'Banco de Imagens'
  CALENDARIO_MAKING_OF = 'Calendário e Making of'
  CHAMADAS = 'Chamadas'
  SEQUENCIA_TITULOS = 'Sequência de Títulos'
  COBERTURA_EVENTO = 'Cobertura de Evento'
  TRANSMISSAO_AO_VIVO = 'Transmissão ao Vivo'
  DRAMA = 'Drama'
  NOVELA = 'Novela'
  SERIE = 'Série'
  INTERVALO_DATA = 'Intervalo de data'
  NAO_TIPO = 'Não é tipo de obra'
  OUTRO = 'Outro'
  
def _normalizar(texto):
  if texto is None:
    return None
  texto = str(texto).strip().lower()
  return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode()

# Sinônimos que caem no mesmo tipo (chaves do enum).
_SINONIMOS = {
  'ficcao': Tipo.FICCAO,
  'ficcao (serie)': Tipo.FICCAO,
  'drama': Tipo.DRAMA,
  'novela': Tipo.NOVELA,
  'documentario': Tipo.DOCUMENTARIO,
  'documentario institucional': Tipo.DOCUMENTARIO,
  'documentario / institucional': Tipo.DOCUMENTARIO,
  'obra publicitaria': Tipo.PUBLICIDADE,
  'publicitaria': Tipo.PUBLICIDADE,
  'comercial': Tipo.PUBLICIDADE,
  'obra nao publicitaria': Tipo.NAO_PUBLICITARIA,
  'reality show': Tipo.REALITY,
  'reality': Tipo.REALITY,
  'serie (reality)': Tipo.REALITY,
  'ficcao / reality show': Tipo.REALITY,
  'videoclipe': Tipo.VIDEOCLIPE,
  'video clipe': Tipo.VIDEOCLIPE,
  'clip': Tipo.VIDEOCLIPE,
  'music video': Tipo.MUSICA,
  'video music': Tipo.MUSICA,
  'video musical': Tipo.MUSICA,
  'video de musica': Tipo.MUSICA,
  'programa': Tipo.PROGRAMA,
  'programa de tv': Tipo.PROGRAMA,
  'programa de televisao': Tipo.PROGRAMA,
  'programa para tv': Tipo.PROGRAMA,
  'programa de entrevistas': Tipo.ENTREVISTA,
  'entrevista': Tipo.ENTREVISTA,
  'programa de noticias': Tipo.NOTICIAS,
  'programa de variedades': Tipo.VARIEDADES,
  'seriado de variedades': Tipo.VARIEDADES,
  'variedades': Tipo.VARIEDADES,
  'institucional': Tipo.INSTITUCIONAL,
  'entretenimento corporativo': Tipo.CORPORATIVO,
  'video corporativo': Tipo.CORPORATIVO,
  'video educativo': Tipo.EDUCATIVO,
  'educacional / pesquisa': Tipo.EDUCATIVO,
  'streaming': Tipo.STREAMING,
  'redes sociais': Tipo.REDES_SOCIAIS,
  'videos para aplicativo': Tipo.STREAMING,
  'banco de imagens': Tipo.BANCO_IMAGENS,
  'calendario e making of': Tipo.CALENDARIO_MAKING_OF,
  'chamadas': Tipo.CHAMADAS,
  'sequencia de titulos': Tipo.SEQUENCIA_TITULOS,
  'cobertura de evento': Tipo.COBERTURA_EVENTO,
  'transmissao ao vivo': Tipo.TRANSMISSAO_AO_VIVO,
  'serie': Tipo.SERIE,
}

# Valores que não são tipo de obra (datas, nomes de empresa etc.).
_NAO_TIPO = [
  '03/10/2022 a 2022-10-14',
  '16/10/2022 a 2022-10-27',
  '2022-09-22 a 2022-09-28',
  '2022-10-18',
  '2022-10-20 a 2022-10-21',
  '2022-10-26 a 2022-10-29',
  'bps producoes e servicos eireli',
]


def classificar_tipo(valor):
  """Mapeia um valor bruto de TIPO_OBRA para um membro do enum Tipo."""
  if valor is None:
    return Tipo.NAO_TIPO.value
  chave = _normalizar(valor)
  if chave in _NAO_TIPO:
    return Tipo.NAO_TIPO.value
  if chave in _SINONIMOS:
    return _SINONIMOS[chave].value
  if any(p in chave for p in ['2022', 'a 2022']):
    return Tipo.INTERVALO_DATA.value
  return Tipo.OUTRO.value


class Pais(Enum):
  AFRICA_DO_SUL = 'África do Sul'
  ALEMANHA = 'Alemanha'
  ARGENTINA = 'Argentina'
  ARABIA_SAUDITA = 'Arábia Saudita'
  AUSTRALIA = 'Austrália'
  AUSTRIA = 'Áustria'
  BELGICA = 'Bélgica'
  BOSNIA_HERZEGOVINA = 'Bósnia e Herzegovina'
  CANADA = 'Canadá'
  CATAR = 'Catar'
  CHINA = 'China'
  COLOMBIA = 'Colômbia'
  COREIA_DO_SUL = 'Coreia do Sul'
  DINAMARCA = 'Dinamarca'
  EGITO = 'Egito'
  EMIRADOS_ARABES = 'Emirados Árabes Unidos'
  EQUADOR = 'Equador'
  ESCOCIA = 'Escócia'
  ESPANHA = 'Espanha'
  ESTADOS_UNIDOS = 'Estados Unidos'
  FRANCA = 'França'
  GRECIA = 'Grécia'
  HOLANDA = 'Países Baixos'
  HONG_KONG = 'Hong Kong'
  INDIA = 'Índia'
  INGLATERRA = 'Reino Unido'
  IRAQUE = 'Iraque'
  IRLANDA = 'Irlanda'
  IRA = 'Irã'
  ISRAEL = 'Israel'
  ITALIA = 'Itália'
  JAPAO = 'Japão'
  KUWAIT = 'Kuwait'
  LIBANO = 'Líbano'
  LONDRES = 'Reino Unido'
  MEXICO = 'México'
  NEPAL = 'Nepal'
  NICARAGUA = 'Nicarágua'
  NIGERIA = 'Nigéria'
  NORUEGA = 'Noruega'
  PAQUISTAO = 'Paquistão'
  PERU = 'Peru'
  POLONIA = 'Polônia'
  PORTUGAL = 'Portugal'
  REINO_UNIDO = 'Reino Unido'
  REPUBLICA_TCHECA = 'República Tcheca'
  ROMENIA = 'Romênia'
  RUSSIA = 'Rússia'
  SINGAPURA = 'Singapura'
  SUICA = 'Suíça'
  SUECIA = 'Suécia'
  TURQUIA = 'Turquia'
  UCRANIA = 'Ucrânia'
  URUGUAI = 'Uruguai'
  SEM_INFORMACAO = 'Sem informação'
  NAO_PAIS = 'Não é país'


_PAIS_SINONIMOS = {
  'africa do sul': Pais.AFRICA_DO_SUL,
  'alemanha': Pais.ALEMANHA,
  'argentina': Pais.ARGENTINA,
  'arabia saudita': Pais.ARABIA_SAUDITA,
  'australia': Pais.AUSTRALIA,
  'austria': Pais.AUSTRIA,
  'belgica': Pais.BELGICA,
  'bosnia e herzegovina': Pais.BOSNIA_HERZEGOVINA,
  'canada': Pais.CANADA,
  'catar': Pais.CATAR,
  'china': Pais.CHINA,
  'cingapura': Pais.SINGAPURA,
  'singapura': Pais.SINGAPURA,
  'colombia': Pais.COLOMBIA,
  'corea do sul': Pais.COREIA_DO_SUL,
  'coreia do sul': Pais.COREIA_DO_SUL,
  'coreia': Pais.COREIA_DO_SUL,
  'republica da coreia, coreia do sul': Pais.COREIA_DO_SUL,
  'republica da coreia': Pais.COREIA_DO_SUL,
  'dinamarca': Pais.DINAMARCA,
  'egito': Pais.EGITO,
  'emirados arabes unidos': Pais.EMIRADOS_ARABES,
  'emirados arabes': Pais.EMIRADOS_ARABES,
  'equador': Pais.EQUADOR,
  'escocia': Pais.ESCOCIA,
  'espanha': Pais.ESPANHA,
  'estados unidos': Pais.ESTADOS_UNIDOS,
  'estados unidos da america': Pais.ESTADOS_UNIDOS,
  'eua': Pais.ESTADOS_UNIDOS,
  'franca': Pais.FRANCA,
  'grecia': Pais.GRECIA,
  'holanda': Pais.HOLANDA,
  'paises baixos': Pais.HOLANDA,
  'hong kong': Pais.HONG_KONG,
  'hong kong (china)': Pais.HONG_KONG,
  'india': Pais.INDIA,
  'inglaterra': Pais.INGLATERRA,
  'reino unido': Pais.REINO_UNIDO,
  'reino unido/inglaterra': Pais.REINO_UNIDO,
  'londres': Pais.LONDRES,
  'iraque': Pais.IRAQUE,
  'irlanda': Pais.IRLANDA,
  'ira': Pais.IRA,
  'israel': Pais.ISRAEL,
  'italia': Pais.ITALIA,
  'japao': Pais.JAPAO,
  'kuwait': Pais.KUWAIT,
  'libano': Pais.LIBANO,
  'mexico': Pais.MEXICO,
  'nepal': Pais.NEPAL,
  'nicaragua': Pais.NICARAGUA,
  'nigeria': Pais.NIGERIA,
  'noruega': Pais.NORUEGA,
  'paquistao': Pais.PAQUISTAO,
  'peru': Pais.PERU,
  'polonia': Pais.POLONIA,
  'portugal': Pais.PORTUGAL,
  'republica tcheca': Pais.REPUBLICA_TCHECA,
  'romenia': Pais.ROMENIA,
  'russia': Pais.RUSSIA,
  'suica': Pais.SUICA,
  'suecia': Pais.SUECIA,
  'turquia': Pais.TURQUIA,
  'ucrania': Pais.UCRANIA,
  'uruguai': Pais.URUGUAI,
}

_PAIS_NAO_PAIS = [
  '-', '1', '3', '4', '6', '15',
  'n.a.', 'nao consta',
  'jacareacanga- pa e alta floresta- mt',
]

_PAIS_SEM_INFORMACAO = [
  'nao consta', 'n.a.', '-',
]


def normaliza_pais(valor):
  """Normaliza um valor bruto de PAIS para um membro do enum Pais.

  Trata variações de caixa/acento, sinônimos (ex.: EUA = Estados Unidos) e
  valores inválidos. Valores compostos (ex.: 'México / Uruguai / Dinamarca')
  não são mapeáveis a um único país e retornam Pais.NAO_PAIS.
  """
  if valor is None:
    return Pais.SEM_INFORMACAO.value
  chave = _normalizar(valor)
  if chave in _PAIS_SEM_INFORMACAO:
    return Pais.SEM_INFORMACAO.value
  if chave in _PAIS_NAO_PAIS:
    return Pais.NAO_PAIS.value
  if chave in _PAIS_SINONIMOS:
    return _PAIS_SINONIMOS[chave].value
  return Pais.NAO_PAIS.value

def normaliza_nr_tecnicos(valor):
  """Normaliza NR_TECNICOS_ARTISTAS_ESTRANGEIROS para inteiro.

  Converte strings numéricas (inclusive com zero à esquerda, ex.: '01') para
  int. Valores não numéricos ('CANCELADO', 'N.A.') e ausentes (NaN) retornam
  np.nan.
  """
  if valor is None:
    return np.nan
  if pd.isna(valor):
    return np.nan
  texto = str(valor).strip()
  if texto in ('CANCELADO', 'N.A.'):
    return np.nan
  if texto.isdigit():
    return int(texto)
  return np.nan