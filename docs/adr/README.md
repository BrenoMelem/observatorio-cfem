# Decisões de arquitetura (ADR)

Uma decisão técnica por arquivo. As regras de negócio (o quê e por quê) estão em [../regras-de-negocio/](../regras-de-negocio/README.md); aqui fica o como. Um ADR não é fonte de regra de negócio.

Atualizado em 20/11/2026.

## Restrições do mantenedor

O que não está nas regras e condiciona as escolhas (equipe, orçamento, prazo, infraestrutura disponível). Cada item com a data em que foi informado.

- **Equipe:** cinco pessoas, com papéis separados (19/11/2026): duas no backend, que dominam Python (o mantenedor e mais uma); uma na parte de IA (o assistente); uma no front-end; e uma na coordenação e organização do projeto. Em 11/11/2026 o registro dizia "1 a 2 pessoas, que dominam Python", e os ADR-007 a ADR-016 citam esse número; ele corresponde às duas pessoas do backend, a quem cabem a API, a coleta e a operação. As decisões desses ADRs continuam válidas e eles não foram reescritos.
- **Hospedagem e orçamento:** ainda não definidos. As escolhas devem funcionar em plano gratuito e poder migrar sem retrabalho grande (11/11/2026). A produção provavelmente será a AWS, mas a equipe não tem acesso e não há previsão; a conta não é da equipe. Até lá, o ambiente é a máquina de cada pessoa e, se for possível, uma máquina da universidade (19/11/2026).
- **Docker:** a equipe já usa (19/11/2026).
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
| 6 | Hospedagem e segredos | Infraestrutura e processo | 3, 4, 5 | seção 4.3 | aceita em 19/11/2026 como provisória (Docker local; AWS provável, serviço a decidir em ADR novo; revisão em 31/03/2027) | [ADR-015](ADR-015-hospedagem-provisoria-e-segredos.md) |
| 7 | Qualidade: testes, lint e CI (a publicação passou para a decisão 6 em 17/11/2026) | Infraestrutura e processo | 1, 2 | seção 6 (Fase 5) | aceita em 17/11/2026 | [ADR-012](ADR-012-testes-lint-e-ci.md) |
| 8 | Organização do repositório e do fluxo de trabalho | Infraestrutura e processo | 1 a 5, 7 | seção 4.1 (pasta `backend/`) | aceita em 17/11/2026 | [ADR-013](ADR-013-organizacao-do-repositorio.md) |
| 9 | Assistente de IA: forma da resposta, onde roda e como usa a camada publicada | API e backend | 4, 6 | seções 2 (contrato do assistente) e 4.3 | pendente; adiada pelo mantenedor em 21/11/2026 (ver nota abaixo) | |
| 10 | Formato do pacote publicado (acrescentada em 17/11/2026; o ADR-009 deixou o formato de fora) | Dados e coleta | 3, 8 | seção 4.2 | aceita em 17/11/2026 | [ADR-014](ADR-014-formato-do-pacote-publicado.md) |
| 11 | Armazenamento dos dados enviados por usuários (perfis, conteúdo, relatos, comentários, consultas, marketplace), acrescentada em 19/11/2026; a lacuna foi registrada no ADR-009 e no ADR-013 | Dados e coleta | 3, 6 | nenhum | aceita em 19/11/2026 (PostgreSQL; o que guardar de dado pessoal depende do conflito B1) | [ADR-016](ADR-016-armazenamento-dos-dados-de-usuarios.md) |
| 12 | Padrões de código e manutenção (acrescentada em 20/11/2026): contrato das fontes, organização da `api/` e convenções | API e backend | 2, 7, 8 | nenhum | aceita em 20/11/2026 | [ADR-017](ADR-017-padroes-de-codigo.md) |
| 13 | Biblioteca de processamento de dados (acrescentada em 20/11/2026; o ADR-008 e o ADR-014 a deixaram de fora) | Dados e coleta | 2, 3, 10, 12 | nenhum | aceita em 20/11/2026 (polars) | [ADR-018](ADR-018-biblioteca-de-processamento-de-dados.md) |

Depois das decisões 1 a 3 já é possível criar a estrutura inicial do código. Com a decisão 12 aceita (20/11/2026), a estrutura inicial pode ser criada: mover `app/` para `src/observatorio/api/` com o módulo de configuração (ADR-013, ADR-017) e o CI do ADR-012.

### Decisão 9 adiada — nota de 21/11/2026

A decisão 9 foi explicada ao mantenedor em 20/11/2026, e ele a adiou em 21/11/2026. Ela tem três partes:

1. o contrato entre o site e a API: pergunta e contexto na entrada; resposta, citações, limitações e ações na saída;
2. onde o assistente roda: como rota da API ou como serviço separado;
3. como ele usa a camada publicada: o código calcula os números e a IA só redige.

Junto vem a escolha do modelo, do provedor e da busca em documentos (PB-31).

Faltou para decidir:

- a etapa do assistente vem depois do tratamento dos dados (decisão do mantenedor de 11/11/2026, RN-ENT-08);
- o PB-31 vence em 30/09/2027, depois da primeira versão;
- não há camada publicada com dados reais nem hospedagem definitiva;
- o custo do provedor e quem o paga não estão definidos.

Quando a etapa começar, a sugestão é dividir a decisão:

- **9a:** contrato e onde roda, com o responsável pela API;
- **9b:** modelo, provedor e busca em documentos, com a pessoa responsável pela IA.

### Estrutura inicial do código — proposta de 20/11/2026

Proposta apresentada ao mantenedor em 20/11/2026 e **ainda não aprovada**. Esta sessão só documenta: a estrutura será criada depois, em trabalho de desenvolvimento, em dois PRs empilhados.

**PR A: estrutura, configuração e Docker** (ADR-013, ADR-015, ADR-016, ADR-017)

```text
backend/
  pyproject.toml          pacote instalável "observatorio", layout src/; grupo opcional "coleta"
  Dockerfile              imagem só da API, sem dados dentro (ADR-015)
  .dockerignore
  .env.example            todas as variáveis, sem valores secretos
  README.md               como subir com uv e com docker compose
  src/observatorio/
    config.py             único lugar que lê variável de ambiente; fim do parents[n] (ADR-017)
    modelo/               vazio: esquema comum da observação (RN-MOD, RN-TER)
    fontes/               vazio: um módulo por fonte, contrato comum (RN-FNT, ADR-017)
    validacao/            vazio: qualidade e relatório do lote (RN-VPU)
    publicacao/           vazio: montagem e troca do pacote (RN-VPU-01, RN-VPU-03)
    api/                  o atual backend/app/, movido sem mudar comportamento; camadas mantidas
  tests/
    api/test_api.py       os testes atuais, movidos
    test_esqueleto.py     teste de fumaça: o pacote importa e os subpacotes existem
docker-compose.yml        na raiz: serviço "api" e serviço "postgres" (ADR-015, ADR-016)
```

- O `config.py` lê `OBS_PUBLICADO_DIR` e `DATABASE_URL`. O manifesto de indicadores é lido de dentro do pacote publicado (ver o ponto do manifesto, abaixo).
- O Postgres entra no compose por causa do ADR-016, mas nenhum código o usa ainda.
- O comando de execução passa a ser `uvicorn observatorio.api.main:app`.

**PR B: CI e qualidade** (ADR-012, ADR-013, ADR-017)

- Um workflow, a cada PR para a `develop` e a `main`:
  - no `backend/`: `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` e `lint-imports`;
  - em `scripts/`: `ruff check` e `pytest`.
- O contrato do `import-linter`: `modelo` não importa ninguém; `api` não importa `fontes`, `validacao` nem `publicacao`.
- Antes do workflow, é preciso:
  - reformatar 6 arquivos do `backend/`;
  - corrigir os 70 apontamentos do ruff em `scripts/` (medidos em 20/11/2026; 52 corrigíveis automaticamente);
  - ajustar o que o mypy `--strict` apontar.

**Fica de fora dos dois PRs:**

- a publicação do pacote como Release (ADR-015), porque ainda não há gerador de pacote no produto;
- coletores, regras de validação e rotas novas;
- o subpacote dos dados de usuários (nota de 19/11/2026 do ADR-013);
- a proteção de branch no GitHub.

**Manifesto `data/indicadores.json`: resolvido pelo ADR-014 (conferido em 20/11/2026).** A API atual lê esse arquivo na raiz do repositório com `parents[3]`, fora do `backend/` e da imagem Docker. O [ADR-014](ADR-014-formato-do-pacote-publicado.md) já fixou que o manifesto de indicadores (RN-MOD-25) é copiado para dentro do pacote publicado. Assim:

- a API lê o manifesto do pacote, pela `OBS_PUBLICADO_DIR`, como lê os dados (RN-ENT-01);
- a imagem não leva o arquivo, nem é preciso uma variável de ambiente para ele;
- `data/indicadores.json` continua na raiz como origem, e a publicação o copia para o pacote.

Enquanto não houver gerador de pacote, o arquivo é copiado à mão para a pasta publicada local, junto com o `populacao.json`.

### Decisão 6 adiada — nota de 13/11/2026

Nota de 19/11/2026: a decisão 6 foi tomada como provisória no [ADR-015](ADR-015-hospedagem-provisoria-e-segredos.md). Os fatos abaixo continuam valendo como insumo para a revisão de 31/03/2027, se a AWS não sair.

A decisão 6 foi apresentada em 13/11/2026 com três opções (Vercel no plano Hobby, Render no serviço gratuito e Google Cloud Run) e o mantenedor escolheu adiar; o motivo não foi informado. Em 17/11/2026 o mantenedor manteve o adiamento e aceitou separar da decisão 7 a publicação, que passou para a decisão 6; assim, a decisão 7 (ADR-012) e a 8 deixaram de depender da hospedagem. A decisão 9 continua dependendo dela. Para não repetir a pesquisa, ficam os fatos consultados em 13/11/2026 na documentação oficial:

- Vercel, plano Hobby (https://vercel.com/docs/functions/limitations): duração máxima de 300 s, 2 GB de memória e 1 vCPU, pacote Python de até 500 MB sem compressão, corpo de requisição ou resposta de até 4,5 MB (não vale para resposta em fluxo). Não foi conferido se o plano tem restrição de uso.
- Render, serviço web gratuito (https://render.com/docs/free): dorme após 15 minutos sem requisição e leva cerca de 1 minuto para voltar; 750 horas de instância por mês por workspace; sem disco persistente.
- Google Cloud Run: a página de preços não pôde ser lida em 13/11/2026; a camada gratuita e a exigência de conta de faturamento não foram conferidas.

Em todas as opções apresentadas, o transporte proposto era o GitHub Actions gravar o pacote publicado (só agregados) no repositório, com o commit disparando a implantação, e os segredos ficarem nos Secrets do GitHub (coletas) e nas variáveis de ambiente da plataforma (API). Nada disso está decidido.

### Aprovação da Fase 1 — revisão e aprovação de 13/11/2026

O ADR-007 confirma a construção do backend de produção neste repositório, fora de `scripts/`, e o ADR-008 confirma Python com `uv`. O ADR-007 deixa o nome da pasta fora da decisão. A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md) exige aprovação da Fase 1 antes de iniciá-la; os itens 8 e 9 do mapa acima seguem pendentes (os itens 3 e 4 foram aceitos em 13/11/2026, ADR-009 e ADR-010, sem que isso aprove a Fase 1). Na revisão do histórico e dos PRs #18, #19, #21, #22, #23 e #26 em 13/11/2026, não foi localizado registro explícito dessa aprovação. A existência de código em `backend/` no PR #23 não substitui a decisão. O mantenedor precisa confirmar o avanço da Fase 1 e decidir os itens dependentes antes de expandir a implementação ou mesclar o PR.

**Aprovação de 13/11/2026.** Com os ADR-009 e ADR-010 aceitos, o mantenedor aprovou em 13/11/2026 a Fase 1 (a API de leitura por dimensão), com `backend/` como pasta provisória até a decisão 8. A aprovação não alcança a Fase 2 (assistente), que continua dependendo das decisões 6 e 9, nem o merge do PR #23, que é decisão à parte.

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
| [ADR-012](ADR-012-testes-lint-e-ci.md) | Testes, lint e integração contínua | aceito pelo mantenedor em 17/11/2026 |
| [ADR-013](ADR-013-organizacao-do-repositorio.md) | Organização do repositório e do código do produto | aceito pelo mantenedor em 17/11/2026 |
| [ADR-014](ADR-014-formato-do-pacote-publicado.md) | Formato do pacote publicado | aceito pelo mantenedor em 17/11/2026 |
| [ADR-015](ADR-015-hospedagem-provisoria-e-segredos.md) | Hospedagem provisória em Docker local e segredos | aceito pelo mantenedor em 19/11/2026 |
| [ADR-016](ADR-016-armazenamento-dos-dados-de-usuarios.md) | Armazenamento dos dados enviados por usuários | aceito pelo mantenedor em 19/11/2026 |
| [ADR-017](ADR-017-padroes-de-codigo.md) | Padrões de código e manutenção | aceito pelo mantenedor em 20/11/2026 |
| [ADR-018](ADR-018-biblioteca-de-processamento-de-dados.md) | Biblioteca de processamento de dados | aceito pelo mantenedor em 20/11/2026 |
