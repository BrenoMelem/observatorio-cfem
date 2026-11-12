# Decisões de arquitetura (ADR)

Uma decisão técnica por arquivo. As regras de negócio (o quê e por quê) estão em [../regras-de-negocio/](../regras-de-negocio/README.md); aqui fica o como. Um ADR não é fonte de regra de negócio.

Atualizado em 11/11/2026.

## Restrições do mantenedor

O que não está nas regras e condiciona as escolhas (equipe, orçamento, prazo, infraestrutura disponível). Cada item com a data em que foi informado.

- **Equipe:** 1 a 2 pessoas, que dominam Python (11/11/2026).
- **Hospedagem e orçamento:** ainda não definidos. As escolhas devem funcionar em plano gratuito e poder migrar sem retrabalho grande (11/11/2026).
- **Relação com `obcefem_api` e `obcefem`:** mesma equipe. Os repositórios são do professor, que os modifica (11/11/2026).
- **Prazo:** há prazo para a primeira versão no ar, e o projeto deve poder crescer depois. A primeira versão deve estar no ar em até 6 meses, ou seja, até maio de 2027 (11/11/2026).

## Restrições das regras e do protótipo

Levantadas em 11/11/2026. Cada uma cita a regra ou o arquivo de origem.

- A entrega é por API própria, com leitura e metadados, e o CSV aberto sai da mesma camada (RN-ENT-02, RN-ENT-03).
- Front-end, exportações e assistente de IA leem só a camada publicada, nunca a fonte externa (RN-ENT-01); os CSVs nacionais da ANM não vão ao navegador (RN-ENT-06).
- A camada publicada só troca quando o lote novo passa na validação; se falhar, fica o último dado bom e abre-se uma issue (RN-VPU-01, RN-VPU-03).
- Cada execução de coleta gera um relatório de qualidade (RN-VPU-06); mudança de colunas na fonte falha o lote de forma explícita (RN-VPU-04).
- Só dado homologado alimenta os gráficos, e a homologação exige reconciliação com publicação independente (RN-VPU-07, RN-VPU-10). A `obcefem_api` ainda não cumpre isso ([divergências](../regras-de-negocio/divergencias-entre-repositorios.md), "Em aberto").
- Cada fonte tem agenda própria (RN-TMP-02) e o ano mais recente é descoberto em tempo de execução (RN-TMP-01).
- Há um painel de status por indicador, com a última atualização e o ano de referência (RN-ENT-04).
- A resposta da API é híbrida: envelope da `obcefem_api` mais observações no esquema comum; a `obcefem_api` ainda não faz isso (RN-MOD-03, exceção de 08/11/2026).
- O mantenedor mandou manter o comportamento da `obcefem_api` nos itens D2 a D11 ([divergências](../regras-de-negocio/divergencias-entre-repositorios.md)).
- Os arquivos da ANM têm centenas de MB (arrecadação: 325 MB, 2,4 milhões de linhas) e exigem User-Agent de navegador e o certificado intermediário (`AGENTS.md`, [guia do arquivo da ANM](../guias/arquivo-anm.md)).
- As versões dos arquivos da ANM já são arquivadas em Releases a cada 4 horas pelo GitHub Actions (RN-TMP-18, [guia](../guias/arquivo-anm.md)).
- Base dos Dados e Earth Engine dependem de conta de serviço do Google Cloud, ainda não criada (RN-FON-09); o FRED exige chave por variável de ambiente (`AGENTS.md`).
- A `obcefem_api` é FastAPI com pandas e parquet, publicada na Vercel no modo pré-processado: o GitHub Actions gera `dados_processados/` (8 MB) todo dia e o commit dispara o deploy (README da `obcefem_api`, lido em 11/11/2026). Cobre só a CFEM (arrecadação, autuação e distribuição estimada).
- O protótipo daqui é Python com `uv`, arquivos locais por camada e uma API que lê só `publicado/`; cobre população, despesa (SICONFI) e commodities ([ADR-005](ADR-005-pipeline-populacao.md), [scripts](../../scripts/README.md)). A linguagem do protótipo não decide a de produção.

## Mapa de decisões

Na ordem em que precisam ser tomadas.

| # | Decisão | Área | Depende de | Situação | Registro |
| --- | --- | --- | --- | --- | --- |
| 1 | Onde mora o produto e a relação com a `obcefem_api` | Infraestrutura e processo | nenhuma | aceita em 11/11/2026 | [ADR-006](ADR-006-onde-mora-o-produto.md) |
| 2 | Linguagem e ambiente de execução do backend | API e backend | 1 | próxima | |
| 3 | Armazenamento das camadas (bruto, qualidade, publicado) | Dados e coleta | 1, 2 | pendente | |
| 4 | Framework e contrato da API (inclui o formato híbrido de resposta) | API e backend | 2, 3 | pendente | |
| 5 | Execução e agendamento das coletas, com a abertura de issue na falha | Dados e coleta | 2, 3 | pendente | |
| 6 | Hospedagem e segredos | Infraestrutura e processo | 3, 4, 5 | pendente | |
| 7 | Qualidade e entrega: testes, lint, CI e publicação | Infraestrutura e processo | 2, 6 | pendente | |
| 8 | Organização do repositório e do fluxo de trabalho | Infraestrutura e processo | 1 a 7 | pendente | |

Depois das decisões 1 a 3 já é possível criar a estrutura inicial do código.

## ADRs

| ADR | Título | Status |
| --- | --- | --- |
| [ADR-005](ADR-005-pipeline-populacao.md) | Protótipo local do pipeline de população | aceito para o protótipo local em 30/10/2026 |
| [ADR-006](ADR-006-onde-mora-o-produto.md) | Onde mora o produto e a relação com a `obcefem_api` | aceito pelo mantenedor em 11/11/2026 |
