# Observatório CFEM

Projeto de pesquisa e desenvolvimento de um observatório de dados públicos sobre a Compensação Financeira pela Exploração de Recursos Minerais (CFEM), com foco inicial em Canaã dos Carajás e Parauapebas, no Pará.

## Escopo atual

O repositório reúne a pesquisa de viabilidade, o mapeamento de fontes e indicadores, validações exploratórias e um protótipo local do pipeline de população. A pesquisa diferencia arrecadação da CFEM, distribuição aos entes beneficiários e autuações, que são medidas distintas.

O observatório ainda não tem backend de produção. Há um protótipo local do pipeline de população estimada e uma preparação dos dados da CFEM arrecadada; limitações, validações pendentes e decisões de produção seguem documentadas.

## Estrutura

- `docs/regras-de-negocio/`: regras e pendências do projeto.
- `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`: relatório de viabilidade, fontes, bibliografia e pacote LaTeX.
- `notebooks/`: laboratório exploratório de fontes do observatório.
- `scripts/`: scripts de validação e reconciliação, além dos protótipos de atualização de população e preparação da CFEM.
- `src/` e `test/`: código e testes dos protótipos locais.
- `docs/adr/`, `docs/api/`, `docs/architecture/` e `docs/database/`: decisões e desenhos técnicos.
- `AGENTS.md`: instruções para agentes de IA que trabalham no repositório (o `CLAUDE.md` apenas aponta para ele).

## Começar

Para executar o protótipo local de população (Node.js 24), use `node scripts/atualizar-populacao.mjs` para coletar e validar e `node scripts/servir.mjs` para iniciar a API. Abra `notebooks/laboratorio_fontes_observatorio_cfem.ipynb` em Jupyter ou Google Colab. Os scripts Python informam suas dependências nos próprios arquivos ou usam bibliotecas comuns de análise de dados; consulte cada cabeçalho antes de executar.

Os scripts que consultam serviços externos fazem requisições às fontes indicadas no código. Para bases que exigem autenticação, use os meios oficiais e não inclua credenciais, tokens ou dados identificáveis neste repositório.

## Fontes e proveniência

As fontes públicas, seus formatos, limitações e referências estão documentados em `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`. Dados brutos baixados, resultados de execução e imagens de sessão não são versionados. Gere esses artefatos localmente e confirme a licença e a proveniência antes de redistribuir dados derivados.

## Situação

Pesquisa de viabilidade e validação de fontes, com um protótipo local de população. A definição final de requisitos, arquitetura, licenças de redistribuição e plano de produção ainda precisa ser aprovada.

## Protótipo local e pendências

O pipeline de população via SIDRA atende os 12 municípios, reconcilia 2025 e 2026 com referências independentes do IBGE e publica somente lotes homologados na API e no CSV. O painel informa a atualização e o ano de referência. Consulte [execução e limites](docs/implementacao-populacao.md) e o [ADR-005](docs/adr/ADR-005-pipeline-populacao.md).

A leitura do CSV completo da ANM encontrou 129 repetições exatas no recorte da arrecadação. O lote de CFEM permanece bloqueado por `RN-VPU-11`; nenhum valor foi publicado. Veja o [relatório de duplicatas](docs/revisao-duplicatas-cfem-2026-10-30.md), a [preparação da CFEM](docs/implementacao-cfem.md) e as [pendências de regras de negócio](docs/regras-de-negocio/pendencias.md).
