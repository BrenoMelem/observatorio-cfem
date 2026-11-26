# Observatório CFEM

Projeto de pesquisa e desenvolvimento de um observatório de dados públicos sobre a Compensação Financeira pela Exploração de Recursos Minerais (CFEM), nos 12 municípios da Região de Integração Carajás, no Pará, com foco em Canaã dos Carajás e Parauapebas.

## Escopo atual

O repositório reúne a pesquisa de viabilidade, o mapeamento de fontes e indicadores, validações exploratórias e um protótipo local do pipeline de população. A pesquisa diferencia arrecadação da CFEM, distribuição aos entes beneficiários e autuações, que são medidas distintas.

O produto começa em `backend/`, com a estrutura do ADR-013 e uma API de leitura da camada publicada, ainda sem implantação; roda com `uv` ou em Docker (ADR-015). Quando há publicação válida, ela expõe a arrecadação da CFEM (conferida ao centavo com a tabela oficial da ANM), a despesa por função do SICONFI (conferida com o RREO e a MSC) e a população homologada, e informa as lacunas dos demais indicadores. As coletas da CFEM e do SICONFI têm workflows no GitHub Actions que publicam o pacote como Release (guias [pipeline-cfem.md](docs/guias/pipeline-cfem.md) e [pipeline-siconfi.md](docs/guias/pipeline-siconfi.md)). O laboratório mantém um protótipo local do pipeline de população; limitações e validações pendentes seguem documentadas.

## Estrutura

- `docs/`: toda a documentação, com [índice em docs/README.md](docs/README.md).
- `docs/regras-de-negocio/`: regras e pendências do projeto.
- `docs/produto/`: o [Product Backlog](docs/produto/backlog.md) da plataforma (51 itens, retrato de 19/11/2026) e o que as regras já cobrem de cada item.
- `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`: relatório de viabilidade, fontes, bibliografia e pacote LaTeX.
- `scripts/`: o laboratório, em Python com [uv](https://docs.astral.sh/uv/): coletas e sondas de teste, protótipo local da API, notebook e testes. Não é o produto. Veja o [mapa em scripts/README.md](scripts/README.md).
- `backend/`: o produto, pacote `observatorio` (modelo, fontes, validação, publicação e API), separado do laboratório. Veja [estrutura e como executar](backend/README.md).
- `docker-compose.yml`: ambiente provisório com a API e o PostgreSQL (ADR-015, ADR-016).
- `data/`: referências versionadas (população do IBGE por ano; arrecadação da CFEM por município e mês e totais nacionais da ANM, com as capturas em `evidencias-anm/`) e o manifesto de indicadores.
- `docs/guias/` e `docs/registros/`: como rodar as coletas (do produto e do laboratório) e o que cada execução encontrou, por data.
- `docs/adr/` e `docs/api/`: decisões técnicas, o contrato da API do produto (`openapi-producao.yaml`) e o esboço do protótipo (`openapi.yaml`).
- `AGENTS.md`: instruções para agentes de IA que trabalham no repositório (o `CLAUDE.md` apenas aponta para ele).

## Começar

Instale o [uv](https://docs.astral.sh/uv/) e rode `uv sync` na raiz. Depois, por exemplo, `uv run python -m scripts.populacao.atualizar` coleta e valida a população, `uv run python -m scripts.servidor.servidor` inicia a API local do protótipo e `uv run pytest` roda os testes. O notebook de laboratório (`scripts/notebook/laboratorio_fontes_observatorio_cfem.ipynb`) abre em Jupyter ou Google Colab. Cada script tem `--help` e uma docstring que diz o que faz.

Os scripts que consultam serviços externos fazem requisições às fontes indicadas no código. Para bases que exigem autenticação, use os meios oficiais e não inclua credenciais, tokens ou dados identificáveis neste repositório.

## Fontes e proveniência

As fontes públicas, seus formatos, limitações e referências estão documentados em `docs/regras-de-negocio/fontes/pesquisa-observatorio-cfem/`. Dados brutos baixados, resultados de execução e imagens de sessão não são versionados. Gere esses artefatos localmente e confirme a licença e a proveniência antes de redistribuir dados derivados.

## Situação

Em 26/11/2026, o produto (`backend/`) publica a arrecadação da CFEM e a despesa por função do SICONFI, com coletas no GitHub Actions; a API ainda não tem hospedagem pública. A definição final de requisitos e o plano de produção ainda precisam ser aprovados.

## Protótipo local e pendências

O pipeline de população via SIDRA atende os 12 municípios, reconcilia 2025 e 2026 com referências independentes do IBGE e publica somente lotes homologados na API e no CSV. O painel informa a atualização e o ano de referência. Consulte [execução e limites](docs/guias/populacao.md) e o [ADR-005](docs/adr/ADR-005-pipeline-populacao.md).

Na coleta de 26/11/2026 (edição `anm-2026-11-25-1358` dos arquivos da ANM), a arrecadação da CFEM foi aprovada sem erros: 1.463 células município-mês de 2004 a 2025 conferidas ao centavo com a tabela oficial da ANM, 47 provisórias (janeiro a junho de 2026), 5 aguardando volume (julho a outubro de 2026) e 22 observações de 2003 sem referência (o arquivo da ANM não tem janeiro a abril de 2003 no país). O controle nacional (RN-CFE-12) cobre 2004 a 2025, com maior diferença de 0,4393% (2008). As 28 repetições integrais do recorte são somadas pela exceção de `RN-VPU-11` de 08/11/2026. Veja o [registro de 26/11/2026](docs/registros/pipeline-cfem-2026-11-26.md).

As coletas locais da DCA e do FRED, o relatório de duplicatas e seus limites estão em [coletas de despesa e commodities](docs/guias/despesa-e-commodities.md). As rotas do protótipo do laboratório estão em [openapi.yaml](docs/api/openapi.yaml); as da API do produto, em [openapi-producao.yaml](docs/api/openapi-producao.yaml), e o pipeline da CFEM da coleta à API, no [guia](docs/guias/pipeline-cfem.md).
