# Decisões de arquitetura (ADR)

Uma decisão técnica por arquivo. As regras de negócio (o quê e por quê) estão em [../regras-de-negocio/](../regras-de-negocio/README.md); aqui fica o como. Um ADR não é fonte de regra de negócio.

Atualizado em 13/11/2026.

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

| # | Decisão | Área | Depende de | Insumo na análise da Fase 0 | Situação | Registro |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Onde mora o produto e a relação com a `obcefem_api` | Infraestrutura e processo | nenhuma | seção 4.1 | aceita em 11/11/2026 | [ADR-007](ADR-007-onde-mora-o-produto.md) |
| 2 | Linguagem e ambiente de execução do backend | API e backend | 1 | seção 4.1 | aceita em 11/11/2026 | [ADR-008](ADR-008-linguagem-e-ambiente.md) |
| 3 | Armazenamento das camadas (bruto, qualidade, publicado) | Dados e coleta | 1, 2 | seção 4.2 | aceita em 13/11/2026 | [ADR-009](ADR-009-armazenamento-das-camadas.md) |
| 4 | Framework e contrato da API (inclui o formato híbrido de resposta) | API e backend | 2, 3 | seções 4.4 e 4.5 | aceita em 13/11/2026 | [ADR-010](ADR-010-framework-e-contrato-da-api.md) |
| 5 | Execução e agendamento das coletas, com a abertura de issue na falha | Dados e coleta | 2, 3 | seção 4.2 (produtor e transporte, em aberto) | aceita em 13/11/2026 | [ADR-011](ADR-011-execucao-e-agendamento-das-coletas.md) |
| 6 | Hospedagem e segredos | Infraestrutura e processo | 3, 4, 5 | seção 4.3 | adiada pelo mantenedor em 13/11/2026 (ver nota abaixo) | |
| 7 | Qualidade e entrega: testes, lint, CI e publicação | Infraestrutura e processo | 2, 6 | seção 6 (Fase 5) | pendente | |
| 8 | Organização do repositório e do fluxo de trabalho | Infraestrutura e processo | 1 a 7 | seção 4.1 (pasta `backend/`) | pendente | |
| 9 | Assistente de IA: forma da resposta, onde roda e como usa a camada publicada | API e backend | 4, 6 | seções 2 (contrato do assistente) e 4.3 | pendente | |

Depois das decisões 1 a 3 já é possível criar a estrutura inicial do código.

### Decisão 6 adiada — nota de 13/11/2026

A decisão 6 foi apresentada em 13/11/2026 com três opções (Vercel no plano Hobby, Render no serviço gratuito e Google Cloud Run) e o mantenedor escolheu adiar; o motivo não foi informado. As decisões 7, 8 e 9 dependem dela. Para não repetir a pesquisa, ficam os fatos consultados em 13/11/2026 na documentação oficial:

- Vercel, plano Hobby (https://vercel.com/docs/functions/limitations): duração máxima de 300 s, 2 GB de memória e 1 vCPU, pacote Python de até 500 MB sem compressão, corpo de requisição ou resposta de até 4,5 MB (não vale para resposta em fluxo). Não foi conferido se o plano tem restrição de uso.
- Render, serviço web gratuito (https://render.com/docs/free): dorme após 15 minutos sem requisição e leva cerca de 1 minuto para voltar; 750 horas de instância por mês por workspace; sem disco persistente.
- Google Cloud Run: a página de preços não pôde ser lida em 13/11/2026; a camada gratuita e a exigência de conta de faturamento não foram conferidas.

Em todas as opções apresentadas, o transporte proposto era o GitHub Actions gravar o pacote publicado (só agregados) no repositório, com o commit disparando a implantação, e os segredos ficarem nos Secrets do GitHub (coletas) e nas variáveis de ambiente da plataforma (API). Nada disso está decidido.

### Pendência de aprovação da Fase 1 — revisão de 13/11/2026

O ADR-007 confirma a construção do backend de produção neste repositório, fora de `scripts/`, e o ADR-008 confirma Python com `uv`. O ADR-007 deixa o nome da pasta fora da decisão. A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md) exige aprovação da Fase 1 antes de iniciá-la; os itens 8 e 9 do mapa acima seguem pendentes (os itens 3 e 4 foram aceitos em 13/11/2026, ADR-009 e ADR-010, sem que isso aprove a Fase 1). Na revisão do histórico e dos PRs #18, #19, #21, #22, #23 e #26 em 13/11/2026, não foi localizado registro explícito dessa aprovação. A existência de código em `backend/` no PR #23 não substitui a decisão. O mantenedor precisa confirmar o avanço da Fase 1 e decidir os itens dependentes antes de expandir a implementação ou mesclar o PR.

O coletor de laboratório `scripts/commodities/pink_sheet.py`, já incorporado à `develop` antes do PR #23, ainda produz um único indicador mensal de ferro em `USD/dmt`. Isso diverge de RN-TMP-13 e RN-TMP-14, que exigem contrato anual em `¢/dmtu` (1985–2005) e spot mensal em `$/dmt` (desde dezembro de 2008), separados. O backend do PR #23 não lê esse coletor nem publica commodities; a correção é independente do merge deste PR. Próximo passo: abrir uma correção própria do coletor e dos testes, sem publicar ferro até validar o recorte e as unidades.

A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md) não é um ADR: é o insumo das decisões 3 a 6, 8 e 9, e traz também o inventário das rotas existentes, a situação de cada dimensão do site e os conflitos com regras que não podem ser resolvidos por implementação. Ela nasceu como ADR-006 (proposta) e foi desmembrada por decisão do mantenedor de 11/11/2026; o número 006 não será reaproveitado.

## ADRs

| ADR | Título | Status |
| --- | --- | --- |
| [ADR-005](ADR-005-pipeline-populacao.md) | Protótipo local do pipeline de população | aceito para o protótipo local em 30/10/2026 |
| ADR-006 | Camada publicada por dimensão e assistente (Fase 0) | não é mais ADR desde 11/11/2026: virou a [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md) |
| [ADR-007](ADR-007-onde-mora-o-produto.md) | Onde mora o produto e a relação com a `obcefem_api` | aceito pelo mantenedor em 11/11/2026 |
| [ADR-008](ADR-008-linguagem-e-ambiente.md) | Linguagem e ambiente de execução do backend | aceito pelo mantenedor em 11/11/2026 |
| [ADR-009](ADR-009-armazenamento-das-camadas.md) | Armazenamento das camadas (bruto, qualidade, publicado) | aceito pelo mantenedor em 13/11/2026 |
| [ADR-010](ADR-010-framework-e-contrato-da-api.md) | Framework e contrato da API | aceito pelo mantenedor em 13/11/2026 |
| [ADR-011](ADR-011-execucao-e-agendamento-das-coletas.md) | Execução e agendamento das coletas | aceito pelo mantenedor em 13/11/2026 |
