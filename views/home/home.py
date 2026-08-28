import streamlit as st

with st.container(horizontal=True, horizontal_alignment='center'):
  st.image('assets/Logo-Obseratorio-Spcine-principal-v.png', width=120)
  st.image('assets/logo_spcine-principal.png', width=120)

st.title('Audiovisual SP Aberto')
st.markdown(
  """
  O **Audiovisual SP Aberto** é um painel interativo produzido pelo [Observatório Spcine](https://spcine.com.br/observatorio/) que reúne, em um só lugar, dados
  públicos do setor audiovisual brasileiro para apoiar a análise, o planejamento e a
  transparência das políticas públicas voltadas ao audiovisual. A partir de dados
  abertos da **Ancine**, o painel oferece uma visão ampla do setor, com foco especial
  na cidade de São Paulo, permitindo explorar a oferta cultural, o fomento à produção,
  o público e o consumo, as coproduções internacionais e a eficiência do fomento público.

  ## Os eixos do painel

  A navegação é organizada em cinco eixos temáticos:

  - **Eixo 1 — Mapeamento da Oferta Cultural**: análise da rede de exibição, com
    distribuição geográfica de salas e complexos cinematográficos e sua evolução ao
    longo do tempo, incluindo recortes de densidade e acessibilidade.
  - **Eixo 2 — Fomento à Produção Local e Independente**: panorama das produtoras
    independentes, das obras brasileiras e dos projetos com renúncia fiscal, com
    destaque para a segmentação das obras e a participação de São Paulo.
  - **Eixo 3 — Análise de Público e Consumo Cultural**: estudo dos lançamentos
    comerciais por distribuidora, comparando obras nacionais e estrangeiras em
    termos de quantidade, público e renda, e a participação de municípios produtores.
  - **Eixo 4 — Coproduções Internacionais e Filmagens Estrangeiras**: mapeamento das
    coproduções com participação brasileira, das filmagens de produções estrangeiras
    no país e dos agentes econômicos estrangeiros regularizados.
  - **Eixo 5 — Transparência e Eficiência do Fomento Público**: acompanhamento dos
    projetos financiados pelo FSA e pela renúncia fiscal, incluindo prestação de
    contas, contribuintes e a sobreposição entre os mecanismos de fomento.

  ## Fonte dos dados

  Todos os dados apresentados são de acesso público e foram obtidos a partir dos
  **Dados Abertos da Ancine** (Agência Nacional do Cinema), disponíveis em
  [dados.ancine.gov.br](https://www.gov.br/ancine/pt-br/oca/dados-abertos). Entre as bases utilizadas estão:

  - Obras brasileiras não publicitárias;
  - Produtoras independentes e produtores;
  - Projetos com renúncia fiscal e seus contribuintes;
  - Projetos do Fundo Setorial do Audiovisual (FSA);
  - Lançamentos comerciais por distribuidora;
  - Salas de exibição e complexos cinematográficos;
  - Coproduções internacionais, filmagens estrangeiras e agentes econômicos;
  - Processos em prestação de contas.

  Os dados são carregados diretamente das fontes oficiais, podendo ser atualizados
  conforme a disponibilização pela Ancine.
  """
)