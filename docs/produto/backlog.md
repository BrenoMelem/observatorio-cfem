# Product Backlog do Observatório da CFEM

Retrato de 19/11/2026 do Product Backlog da plataforma, exportado da ferramenta de gestão do projeto (projeto "CFEM 3 · Produto – Plataforma Observatório", lista "Product Backlog"). São 51 itens: 3 entregas contratuais e 48 itens (PB-01 a PB-48). Dois estão EM PROGRESSO (PB-01 e PB-02); os outros 49 estão PENDENTES.

O retrato anterior era de 12/11/2026. De lá para cá mudaram o status de PB-01 e PB-02 (de PENDENTE para EM PROGRESSO, com subtarefas), a prioridade das entregas contratuais (antes sem prioridade, agora Alta) e a exportação passou a trazer o número de subtarefas de PB-31 a PB-36. Nomes, datas de vencimento e prioridades de PB-01 a PB-48 não mudaram.

Como ler este arquivo:

- **A lista viva fica na ferramenta de gestão.** Aqui está a cópia de uma data. Ao exportar de novo, troque as tabelas das seções 1 e 2 e a data acima, e revise a seção 3.
- **O backlog diz o que o produto deve entregar e quando.** Ele não é fonte de regra de negócio: uma regra só nasce ou muda por decisão do mantenedor, como descreve o [README das regras](../regras-de-negocio/README.md).
- **As seções 1 e 2 são a exportação, sem alteração de conteúdo.** As seções 3 a 5 são leitura feita neste repositório em 12/11/2026 e revista em 19/11/2026: ligam cada item às regras e decisões que já existem e apontam o que falta ou conflita.

## 1. Entregas contratuais

| ID | Nome | Tags | Data de vencimento | Prioridade |
| --- | --- | --- | --- | --- |
| [1.5] | ENTREGA: Implementar a plataforma e a base de dados padronizada e documentada para consulta pública | entrega-contratual, meta-1 | 31/03/2028 | Alta |
| [1.6] | ENTREGA: Testes de software (funcional, carga e aceitação), implantação e sustentabilidade | entrega-contratual, meta-1 | 31/03/2028 | Alta |
| [4.2] | ENTREGA: Desenvolver o marketplace como um espaço na plataforma | entrega-contratual, meta-4 | 30/09/2028 | Alta |

As três estão PENDENTES.

## 2. Itens do backlog (PB-01 a PB-48)

| ID | Nome | Status | Data de vencimento | Prioridade | Subtarefas |
| --- | --- | --- | --- | --- | --- |
| PB-01 | Definir arquitetura e stack da plataforma (front-end, back-end, banco analítico, hospedagem) | EM PROGRESSO | 31/10/2026 | Alta | 3 |
| PB-02 | Configurar repositório, integração contínua e ambientes de desenvolvimento e homologação | EM PROGRESSO | 30/11/2026 | Alta | 3 |
| PB-03 | Modelar o banco de dados analítico (CFEM, orçamento, indicadores, territórios) | PENDENTE | 30/11/2026 | Alta | — |
| PB-04 | Como administrador, quero perfis de acesso (público, gestor, administrador) para controlar quem publica e modera | PENDENTE | 31/12/2026 | Alta | — |
| PB-05 | Como cidadão, quero uma navegação simples e acessível para encontrar as informações do Observatório | PENDENTE | 31/12/2026 | Alta | — |
| PB-06 | Carregar a série histórica de 10 anos de arrecadação e uso da CFEM dos dois municípios | PENDENTE | 31/12/2026 | Alta | — |
| PB-07 | Carregar a base socioeconômica e socioambiental (dimensões social, econômica, ambiental e institucional) | PENDENTE | 28/02/2027 | Alta | — |
| PB-08 | Automatizar a atualização periódica das fontes (ANM, TCM-PA, orçamentos municipais) | PENDENTE | 31/05/2027 | Normal | — |
| PB-09 | Como pesquisador, quero o catálogo de metadados e o dicionário de dados para entender a origem de cada variável | PENDENTE | 31/03/2027 | Alta | — |
| PB-10 | Como cidadão, quero consultar e baixar a base de dados (CSV/API) para fazer minhas próprias análises | PENDENTE | 31/05/2027 | Alta | — |
| PB-11 | Como cidadão, quero ver um painel da arrecadação da CFEM ao longo do tempo para acompanhar quanto cada município recebe | PENDENTE | 31/03/2027 | Alta | — |
| PB-12 | Como conselheiro, quero ver onde os recursos da CFEM e do orçamento foram aplicados (por área) para avaliar as prioridades | PENDENTE | 30/04/2027 | Alta | — |
| PB-13 | Como gestor, quero ver o quadro de indicadores por dimensão para avaliar o desenvolvimento municipal | PENDENTE | 30/04/2027 | Alta | — |
| PB-14 | Como usuário, quero filtrar painéis por período, município e dimensão | PENDENTE | 31/05/2027 | Alta | — |
| PB-15 | Como usuário, quero comparar indicadores entre municípios e ao longo do tempo | PENDENTE | 30/06/2027 | Normal | — |
| PB-16 | Publicar as visualizações das análises estatísticas e correlações (CFEM × indicadores) | PENDENTE | 30/06/2027 | Alta | — |
| PB-17 | Como cidadão, quero ler artigos curtos sobre as análises dos indicadores | PENDENTE | 30/09/2027 | Alta | — |
| PB-18 | Como participante dos cursos, quero acessar cartilha, apresentação e guia de uso na plataforma | PENDENTE | 30/09/2027 | Normal | — |
| PB-19 | Como equipe do projeto, quero um módulo de gestão de conteúdo para publicar textos e materiais sem depender dos desenvolvedores | PENDENTE | 30/06/2027 | Alta | — |
| PB-20 | Como cidadão, quero páginas que expliquem o que é a CFEM e o projeto | PENDENTE | 30/06/2027 | Normal | — |
| PB-21 | Como gestor, quero ver os indicadores num mapa por bairro/jurisdição para identificar desigualdades no território | PENDENTE | 31/08/2027 | Alta | — |
| PB-22 | Carregar os limites territoriais (bairros, distritos) dos dois municípios | PENDENTE | 30/06/2027 | Alta | — |
| PB-23 | Como usuário, quero clicar num bairro e ver sua ficha de indicadores | PENDENTE | 30/09/2027 | Normal | — |
| PB-24 | Como cidadão, quero enviar informações e relatos ao Observatório (canal de escuta) | PENDENTE | 30/09/2027 | Alta | — |
| PB-25 | Como cidadão, quero comentar indicadores e publicações, com moderação pela equipe | PENDENTE | 31/10/2027 | Alta | — |
| PB-26 | Como equipe, quero abrir consultas públicas e mostrar os resultados | PENDENTE | 30/11/2027 | Normal | — |
| PB-27 | Incorporar à plataforma os ajustes do quadro de indicadores validados nas oficinas | PENDENTE | 31/03/2028 | Alta | — |
| PB-28 | Como cidadão, quero acompanhar o andamento das demandas que enviei | PENDENTE | 31/12/2027 | Baixa | — |
| PB-29 | Como usuário, quero escolher indicadores e gerar um relatório em PDF | PENDENTE | 30/11/2027 | Alta | — |
| PB-30 | Como conselheiro, gestor ou educador, quero modelos de relatório adequados ao meu público | PENDENTE | 31/01/2028 | Normal | — |
| PB-31 | Escolher o modelo de IA, o provedor e a arquitetura de busca em documentos (RAG) | PENDENTE | 30/09/2027 | Alta | 5 |
| PB-32 | Indexar os dados validados e os conteúdos do Observatório como base de conhecimento do assistente | PENDENTE | 30/11/2027 | Alta | 3 |
| PB-33 | Como cidadão, quero perguntar ao assistente sobre a CFEM e os indicadores e receber respostas com as fontes | PENDENTE | 31/12/2027 | Alta | 5 |
| PB-34 | Como gestor, quero que o assistente resuma informações e aponte padrões nos indicadores | PENDENTE | 31/01/2028 | Normal | 3 |
| PB-35 | Aplicar salvaguardas ao assistente: escopo restrito, transparência, proteção de dados e registro de uso | PENDENTE | 31/01/2028 | Alta | 4 |
| PB-36 | Avaliar a qualidade das respostas do assistente com um conjunto de perguntas de teste | PENDENTE | 29/02/2028 | Normal | 4 |
| PB-37 | Como responsável por uma iniciativa local, quero cadastrar meu projeto no marketplace | PENDENTE | 31/01/2028 | Alta | — |
| PB-38 | Como visitante, quero buscar iniciativas por município e área | PENDENTE | 31/03/2028 | Alta | — |
| PB-39 | Como moderador, quero aprovar ou recusar cadastros do marketplace | PENDENTE | 29/02/2028 | Alta | — |
| PB-40 | Como visitante, quero ver a página de uma iniciativa e como entrar em contato | PENDENTE | 31/05/2028 | Normal | — |
| PB-41 | Criar testes funcionais automatizados das funcionalidades principais | PENDENTE | 31/03/2028 | Alta | — |
| PB-42 | Executar testes de carga | PENDENTE | 29/02/2028 | Alta | — |
| PB-43 | Conduzir testes de aceitação com a Vale e representantes dos usuários | PENDENTE | 31/03/2028 | Alta | — |
| PB-44 | Garantir acessibilidade e uso em celular | PENDENTE | 31/03/2028 | Normal | — |
| PB-45 | Revisar segurança e adequação à LGPD (política de privacidade, termos de uso) | PENDENTE | 31/01/2028 | Alta | — |
| PB-46 | Implantar em produção (servidor, domínio, certificado) | PENDENTE | 31/07/2027 | Alta | — |
| PB-47 | Configurar monitoramento, backup e documentação técnica | PENDENTE | 31/03/2028 | Alta | — |
| PB-48 | Preparar a sustentabilidade e replicabilidade (código documentado, guia para outros municípios, transferência) | PENDENTE | 31/03/2028 | Alta | — |

Subtarefas dos itens em progresso, todas PENDENTES em 19/11/2026:

| Item | Subtarefa | Prioridade |
| --- | --- | --- |
| PB-01 | Definir a arquitetura e a stack do front-end, incluindo a integração com a API | (não informada) |
| PB-01 | Decidir hospedagem e implantação | (não informada) |
| PB-01 | Consolidar as decisões e verificar pendências | (não informada) |
| PB-02 | Configurar e validar o workflow de CI | Alta |
| PB-02 | Aplicar a estrutura de código do ADR-013 | Alta |
| PB-02 | Configurar os ambientes de desenvolvimento e homologação — Documentar e validar o fluxo de CI e dos ambientes | Alta |

As subtarefas de PB-31 a PB-36 não vieram na exportação, só a quantidade.

Resumo por prioridade, contado nas tabelas acima: 39 itens com prioridade Alta (36 do backlog e as 3 entregas), 11 Normal e 1 Baixa, total de 51. O resumo da própria exportação diz 42 Alta, 8 Normal e 1 Baixa, o que não bate com a lista; o retrato de 12/11/2026 dizia 38 Alta e 9 Normal entre os 48 itens, também em desacordo com a lista, que não mudou (as Normais são PB-08, 15, 18, 20, 23, 26, 30, 34, 36, 40 e 44).

## 3. Correspondência com a documentação

Leitura de 12/11/2026, revista em 19/11/2026. O agrupamento por assunto é deste arquivo, não da exportação. A coluna "Situação" usa quatro valores:

| Situação | Significado |
| --- | --- |
| **Com regra** | As regras vigentes já dizem o que o item deve garantir |
| **Parcial** | As regras cobrem a parte de dados do item; o restante não tem regra |
| **Sem regra** | Nenhum documento do repositório trata do item |
| **Conflito** | O texto do item contradiz uma regra; o conflito está registrado em [pendencias.md, seção 6](../regras-de-negocio/pendencias.md#6-conflitos-com-o-product-backlog), sem decisão. Conflito já decidido sai do valor entre parênteses |

"Decisão N do mapa" é a linha N do [mapa de decisões técnicas](../adr/README.md). Em 19/11/2026 estão aceitas as decisões 1 a 5, 7, 8 e 10 (ADR-007 a ADR-014); a 6 (hospedagem e segredos) foi adiada pelo mantenedor em 13/11/2026 e a 9 (assistente de IA) está pendente.

### Fundação

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-01 Arquitetura e stack | Em progresso desde o retrato de 19/11/2026. Decisões 1 a 10 do mapa: aceitas a 1 e a 2 em 11/11/2026 ([ADR-007](../adr/ADR-007-onde-mora-o-produto.md), [ADR-008](../adr/ADR-008-linguagem-e-ambiente.md)), a 3 a 5 em 13/11/2026 ([ADR-009](../adr/ADR-009-armazenamento-das-camadas.md) a [ADR-011](../adr/ADR-011-execucao-e-agendamento-das-coletas.md)), a 7, 8 e 10 em 17/11/2026 ([ADR-012](../adr/ADR-012-testes-lint-e-ci.md) a [ADR-014](../adr/ADR-014-formato-do-pacote-publicado.md)); a 6 foi adiada e a 9 está pendente. As subtarefas abertas são exatamente as lacunas: o front-end não consta do mapa, e a hospedagem é a decisão 6 | Parcial |
| PB-02 Repositório, integração contínua e ambientes | Em progresso desde o retrato de 19/11/2026. Decisões 7 (qualidade) e 8 (organização do repositório) do mapa, aceitas em 17/11/2026 ([ADR-012](../adr/ADR-012-testes-lint-e-ci.md), [ADR-013](../adr/ADR-013-organizacao-do-repositorio.md)): as subtarefas de CI e de estrutura do código aplicam esses ADRs. A subtarefa dos ambientes de desenvolvimento e homologação depende da decisão 6, adiada. Já existe o fluxo de branches do `AGENTS.md` e o arquivamento da ANM a cada 4 horas ([guia](../guias/arquivo-anm.md)) | Parcial |
| PB-03 Modelo do banco analítico | [modelo-de-dados.md](../regras-de-negocio/modelo-de-dados.md) (esquema único, RN-MOD-01 a 04; manifesto, RN-MOD-25) e [territorio.md](../regras-de-negocio/territorio.md). O armazenamento é a decisão 3 do mapa, pendente em 12/11/2026 e depois aceita: arquivos ([ADR-009](../adr/ADR-009-armazenamento-das-camadas.md)), em parquet por indicador com manifestos JSON ([ADR-014](../adr/ADR-014-formato-do-pacote-publicado.md)) | Com regra |
| PB-04 Perfis de acesso (público, gestor, administrador) | Nada. RN-ENT-02 descreve só leitura e metadados | Sem regra |
| PB-05 Navegação simples e acessível | Nada sobre o front-end | Sem regra |

### Dados

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-06 Série de 10 anos de arrecadação e uso da CFEM dos dois municípios | [mineracao-cfem.md](../regras-de-negocio/mineracao-cfem.md): arrecadação desde 2003 (RN-CFE-22), nos 12 municípios (RN-TER-01); "os dois municípios" são os de foco (RN-TER-13, conflito B2 decidido em 17/11/2026). O "uso" depende de RN-CFE-24 (PROPOSTA). O lote da arrecadação está bloqueado por duplicatas (RN-VPU-11) | Conflito (B3) |
| PB-07 Base socioeconômica e socioambiental por dimensão | [regras-por-fonte.md](../regras-de-negocio/regras-por-fonte.md), [indicadores-derivados-e-compostos.md](../regras-de-negocio/indicadores-derivados-e-compostos.md) e o manifesto (RN-MOD-25). As regras organizam os indicadores em blocos temáticos. A dimensão econômica é a primeira e tem composição decidida (RN-ENT-12, 13/11/2026); a correspondência das outras três dimensões com os blocos não está definida | Parcial |
| PB-08 Atualização automática (ANM, TCM-PA, orçamentos municipais) | Agenda por fonte (RN-TMP-01, RN-TMP-02), publicação só de lote validado (RN-VPU-01, RN-VPU-03) e a decisão 5 do mapa, aceita em 13/11/2026 ([ADR-011](../adr/ADR-011-execucao-e-agendamento-das-coletas.md)). TCM-PA e orçamentos municipais não são fontes nas regras | Conflito (B4) |
| PB-09 Catálogo de metadados e dicionário de dados | Manifesto único (RN-MOD-25), proveniência (RN-MOD-21, RN-FON-13) e o [glossário](../regras-de-negocio/glossario.md) | Com regra |
| PB-10 Consulta e download (CSV/API) | API própria e CSV aberto (RN-ENT-02, RN-ENT-03), metadados nas exportações (RN-ENT-05, PROPOSTA), arquivos integrais da ANM fora do consumidor (RN-ENT-06) | Com regra |
| PB-22 Limites territoriais (bairros, distritos) dos dois municípios | Nada abaixo do município; "os dois municípios" são os de foco (RN-TER-13, conflito B2 decidido em 17/11/2026) | Conflito (B5) |

### Painéis e análises

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-11 Painel da arrecadação da CFEM no tempo | Primeiros gráficos (RN-ENT-09, PROPOSTA), só dado homologado (RN-VPU-10). Atenção ao texto: "quanto cada município recebe" é a CFEM recebida (distribuição), que não se confunde com a arrecadada (RN-CFE-02, RN-CFE-03) | Com regra |
| PB-12 Onde a CFEM e o orçamento foram aplicados, por área | Despesa por função pelo SICONFI (RN-FNT-04). Dizer que uma despesa foi paga com CFEM exige a fonte de recursos confirmada (RN-CFE-24, PROPOSTA) | Parcial |
| PB-13 Quadro de indicadores por dimensão | Manifesto (RN-MOD-25), regras dos derivados e compostos (RN-IND-01 a 13), painel de status (RN-ENT-04); a dimensão econômica é a primeira (RN-ENT-12) | Com regra |
| PB-14 Filtros por período, município e dimensão | Nada específico; os metadados de cada ponto seguem RN-VPU-09 | Sem regra |
| PB-15 Comparar municípios e períodos | Municípios de comparação (RN-TER-09), agregação regional (RN-TER-02) e as regras de comparabilidade de [modelo-de-dados.md](../regras-de-negocio/modelo-de-dados.md) (RN-MOD-13 a 19) | Com regra |
| PB-16 Análises estatísticas e correlações (CFEM × indicadores) | Só a marca de análise derivada (RN-IND-05, PROPOSTA). Não há regra sobre método, publicação ou ressalvas de correlações | Parcial |

### Conteúdo

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-17 Artigos curtos sobre as análises | Nada | Sem regra |
| PB-18 Cartilha, apresentação e guia de uso | Nada | Sem regra |
| PB-19 Módulo de gestão de conteúdo | Nada | Sem regra |
| PB-20 Páginas sobre a CFEM e o projeto | Nada como regra; o [glossário](../regras-de-negocio/glossario.md) e [mineracao-cfem.md](../regras-de-negocio/mineracao-cfem.md) servem de insumo | Sem regra |

### Mapa por bairro

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-21 Indicadores num mapa por bairro/jurisdição | Nada abaixo do município | Conflito (B5) |
| PB-23 Ficha de indicadores do bairro | Nada abaixo do município | Conflito (B5) |

### Participação

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-24 Canal de escuta (envio de relatos) | Nada | Sem regra |
| PB-25 Comentários com moderação | Nada | Sem regra |
| PB-26 Consultas públicas | Nada | Sem regra |
| PB-27 Ajustes do quadro de indicadores validados nas oficinas | Nada sobre o processo; a mudança entraria pelo manifesto (RN-MOD-25) | Sem regra |
| PB-28 Acompanhar demandas enviadas | Nada | Sem regra |

### Relatórios

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-29 Relatório em PDF com indicadores escolhidos | Exportações levam os metadados (RN-ENT-05, PROPOSTA) e leem só a camada publicada (RN-ENT-01) | Parcial |
| PB-30 Modelos de relatório por público | Nada | Sem regra |

### Assistente de IA

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-31 Modelo, provedor e arquitetura de busca (RAG) | Decisão 9 do mapa, pendente em 19/11/2026 | Sem regra |
| PB-32 Indexar dados validados e conteúdos | O assistente lê só a camada publicada (RN-ENT-01; RN-ENT-07, PROPOSTA). Não há regra sobre indexar conteúdos editoriais | Parcial |
| PB-33 Perguntas com respostas e fontes | RN-ENT-07 (PROPOSTA): responder só com a camada publicada, com fonte, período e limitações | Com regra |
| PB-34 Resumos e padrões nos indicadores | Só o limite de RN-ENT-07 | Parcial |
| PB-35 Salvaguardas (escopo, transparência, proteção de dados, registro de uso) | Escopo e transparência em RN-ENT-07. Proteção de dados e registro de uso não têm regra (ver B1) | Parcial |
| PB-36 Avaliação com perguntas de teste | RN-ENT-08 (PROPOSTA): critérios listados, metas numéricas em aberto. Em 11/11/2026 o mantenedor definiu que o assistente vem depois do tratamento dos dados | Com regra |

### Marketplace

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-37 Cadastro de iniciativa | Nada | Sem regra |
| PB-38 Busca por município e área | Nada | Sem regra |
| PB-39 Moderação dos cadastros | Nada | Sem regra |
| PB-40 Página da iniciativa e contato | Nada | Sem regra |

### Qualidade e operação

| Item | O que a documentação já tem | Situação |
| --- | --- | --- |
| PB-41 Testes funcionais automatizados | Decisão 7 do mapa, aceita em 17/11/2026 ([ADR-012](../adr/ADR-012-testes-lint-e-ci.md): CI com testes, lint e tipos). O protótipo tem testes em `scripts/` | Sem regra |
| PB-42 Testes de carga | Nada | Sem regra |
| PB-43 Testes de aceitação com a Vale e representantes dos usuários | Nada | Sem regra |
| PB-44 Acessibilidade e uso em celular | Nada | Sem regra |
| PB-45 Segurança e adequação à LGPD | Credenciais (RN-FON-08, RN-PRI-10). A privacidade deixou de ser requisito em 07/11/2026 | Conflito (B1) |
| PB-46 Implantação em produção | Decisão 6 do mapa (hospedagem e segredos), adiada pelo mantenedor em 13/11/2026 | Sem regra |
| PB-47 Monitoramento, backup e documentação técnica | Relatório de qualidade por execução (RN-VPU-06) e painel de status (RN-ENT-04) cobrem só o monitoramento dos dados | Parcial |
| PB-48 Sustentabilidade e replicabilidade | Nada. A lista de municípios é fixa nos 12 da RI Carajás (RN-TER-01); um guia para outros municípios não está previsto | Sem regra |

### Totais

| Situação | Itens | Quantos |
| --- | --- | ---: |
| Com regra | PB-03, 09, 10, 11, 13, 15, 33, 36 | 8 |
| Parcial | PB-01, 02, 07, 12, 16, 29, 32, 34, 35, 47 | 10 |
| Sem regra | PB-04, 05, 14, 17 a 20, 24 a 28, 30, 31, 37 a 44, 46, 48 | 24 |
| Conflito | PB-06, 08, 21, 22, 23, 45 | 6 |

## 4. Conflitos e lacunas

Os cinco conflitos (B1 a B5) estão em [pendencias.md, seção 6](../regras-de-negocio/pendencias.md#6-conflitos-com-o-product-backlog), com as duas versões e as datas. Em 19/11/2026 só o B2 (recorte territorial) está decidido, desde 17/11/2026; o B3 foi adiado pelo mantenedor em 19/11/2026.

As lacunas maiores, que nenhuma regra cobre:

- **Escrita na plataforma.** Perfis de acesso, gestão de conteúdo, canal de escuta, comentários, consultas públicas e marketplace (PB-04, PB-19, PB-24 a 26, PB-28, PB-37 e PB-39) exigem que a plataforma receba e guarde dados de usuários. As regras só descrevem coleta de fontes públicas e leitura da camada publicada.
- **Front-end e conteúdo.** Navegação, filtros, artigos, materiais dos cursos, páginas explicativas, acessibilidade (PB-05, PB-14, PB-17, PB-18, PB-20, PB-44). As regras são do backend.
- **Dimensões do backlog × blocos das regras.** O backlog fala em quatro dimensões (social, econômica, ambiental e institucional); as regras, em blocos temáticos. Em 13/11/2026 o mantenedor decidiu a composição da dimensão econômica (RN-ENT-12: CFEM, PIB, preços, finanças municipais e despesa por função; emprego e renda ficam na social). Falta dizer qual bloco entra em cada uma das outras três dimensões (PB-07, PB-13, PB-14).
- **Operação.** Testes de carga e de aceitação, backup e transferência (PB-42, PB-43, PB-47, PB-48).

## 5. Prazos

- **Já vencido em 19/11/2026:** PB-01 (31/10/2026), em progresso. Faltam a parte de front-end, a decisão 6 (hospedagem, adiada) e a consolidação; a decisão 9 (assistente) também segue pendente.
- **Vencem em 30/11/2026:** PB-02 (em progresso) e PB-03 (pendente).
- **Vencem em 31/12/2026:** PB-04, PB-05 e PB-06. O PB-06 depende de destravar o lote da arrecadação (RN-VPU-11) e do conflito B3 (B2 foi decidido em 17/11/2026).
- **Primeira versão no ar.** Em 11/11/2026 o mantenedor informou o prazo de até maio de 2027 (restrição registrada no [mapa de decisões](../adr/README.md)). No backlog, a implantação em produção (PB-46) vence em 31/07/2027, e os itens que vencem até 31/05/2027 são PB-01 a PB-14. Falta dizer quais deles compõem a primeira versão.
- **Ordem de trabalho.** Em 13/11/2026 o mantenedor decidiu que a dimensão econômica é a primeira, na carga dos dados e nos painéis (RN-ENT-12). Dentro de PB-07 e PB-13, a parte econômica vem antes das partes social, ambiental e institucional; as datas de vencimento dos itens não mudaram. A ordem das outras três dimensões não foi decidida.
- **Entregas contratuais:** [1.5] e [1.6] em 31/03/2028; [4.2] em 30/09/2028.
