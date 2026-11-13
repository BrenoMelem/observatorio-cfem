# Observatório CFEM

Projeto de pesquisa e desenvolvimento de um observatório de dados públicos sobre a Compensação Financeira pela Exploração de Recursos Minerais (CFEM), com foco inicial em Canaã dos Carajás e Parauapebas, no Pará.

## Escopo atual

O repositório reúne a pesquisa de viabilidade, o mapeamento de fontes e indicadores, validações exploratórias e um protótipo local do pipeline de população. A pesquisa diferencia arrecadação da CFEM, distribuição aos entes beneficiários e autuações, que são medidas distintas.

Há uma API de leitura da camada publicada em `backend/`, ainda sem implantação. Ela expõe a população homologada quando o arquivo publicado está disponível e informa explicitamente as lacunas dos demais indicadores. Há também um protótipo local do pipeline de população estimada e uma preparação dos dados da CFEM arrecadada; limitações e validações pendentes seguem documentadas.

## Estrutura

- `docs/`: toda a documentação, com [índice em docs/README.md](docs/README.md).
- `docs/regras-de-negocio/`: regras e pendências do projeto.
- `docs/produto/`: o [Product Backlog](docs/produto/backlog.md) da plataforma (51 itens, retrato de 12/11/2026) e o que as regras já cobrem de cada item.
- `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`: relatório de viabilidade, fontes, bibliografia e pacote LaTeX.
- `scripts/`: todo o código, em Python com [uv](https://docs.astral.sh/uv/): coleta, validação e reconciliação das fontes, protótipo local da API, notebook de laboratório e testes. Veja o [mapa em scripts/README.md](scripts/README.md).
- `backend/`: API de leitura da camada publicada por dimensão, separada do laboratório. Veja [como executar](backend/README.md).
- `data/`: referências versionadas (população do IBGE por ano) e manifesto de indicadores.
- `docs/guias/` e `docs/registros/`: como rodar as coletas do protótipo e o que cada execução encontrou, por data.
- `docs/adr/` e `docs/api/`: decisões técnicas e o esboço do contrato do protótipo.
- `AGENTS.md`: instruções para agentes de IA que trabalham no repositório (o `CLAUDE.md` apenas aponta para ele).

## Começar

Instale o [uv](https://docs.astral.sh/uv/) e rode `uv sync` na raiz. Depois, por exemplo, `uv run python -m scripts.populacao.atualizar` coleta e valida a população, `uv run python -m scripts.servidor.servidor` inicia a API local do protótipo e `uv run pytest` roda os testes. O notebook de laboratório (`scripts/notebook/laboratorio_fontes_observatorio_cfem.ipynb`) abre em Jupyter ou Google Colab. Cada script tem `--help` e uma docstring que diz o que faz.

Os scripts que consultam serviços externos fazem requisições às fontes indicadas no código. Para bases que exigem autenticação, use os meios oficiais e não inclua credenciais, tokens ou dados identificáveis neste repositório.

## Fontes e proveniência

As fontes públicas, seus formatos, limitações e referências estão documentados em `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`. Dados brutos baixados, resultados de execução e imagens de sessão não são versionados. Gere esses artefatos localmente e confirme a licença e a proveniência antes de redistribuir dados derivados.

## Situação

Pesquisa de viabilidade e validação de fontes, com um protótipo local de população. A definição final de requisitos, arquitetura, licenças de redistribuição e plano de produção ainda precisa ser aprovada.

## Protótipo local e pendências

O pipeline de população via SIDRA atende os 12 municípios, reconcilia 2025 e 2026 com referências independentes do IBGE e publica somente lotes homologados na API e no CSV. O painel informa a atualização e o ano de referência. Consulte [execução e limites](docs/guias/populacao.md) e o [ADR-005](docs/adr/ADR-005-pipeline-populacao.md).

A leitura do CSV completo da ANM encontrou 129 repetições exatas no recorte da arrecadação. O lote de CFEM permanece bloqueado por `RN-VPU-11`; nenhum valor foi publicado. Veja o [relatório de duplicatas](docs/registros/duplicatas-cfem-2026-10-30.md), a [preparação da CFEM](docs/guias/cfem.md) e as [pendências de regras de negócio](docs/regras-de-negocio/pendencias.md).

As coletas locais da DCA e do FRED, o relatório de duplicatas e seus limites estão em [coletas de despesa e commodities](docs/guias/despesa-e-commodities.md). O contrato inicial das rotas implementadas está em [OpenAPI](docs/api/openapi.yaml).
