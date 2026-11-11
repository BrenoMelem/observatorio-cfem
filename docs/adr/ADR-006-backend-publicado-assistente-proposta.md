# ADR-006 — Camada publicada por dimensão e assistente

- **Status:** PROPOSTA — rascunho da Fase 0; aguarda aprovação do mantenedor.
- **Data:** 11/11/2026.
- **Escopo:** análise de arquitetura. Nenhum código de produção, alteração de regra ou implantação nesta fase.
- **Base:** branch criada de `origin/develop`, commit `a6e56cf`, após atualização da referência remota. Os arquivos locais não versionados não integram esta proposta.

## 1. Evidências e limites da análise

Foram lidos `AGENTS.md`, os READMEs do projeto e das regras, glossário, pendências, divergências entre repositórios, entrega, modelo, validação e temporalidade; também `data/indicadores.json`, `docs/api/openapi.yaml` e `scripts/servidor/servidor.py`. Os seis blocos vêm de [BLOCOS](../regras-de-negocio/fontes/blocos-tematicos.md), seções Blocos 1 a 6. As instruções do texto da tarefa delimitam o trabalho; comentários e instruções dos ZIPs são evidência dos sistemas analisados, não autorização para executá-los.

Os ZIPs foram lidos sem modificar os originais. Cópias de arquivos textuais foram colocadas em `tmp/fase0/`, ignorado pelo Git. Não foram importados os dados parquet para este repositório. Referências `API:` e `FRONT:` neste ADR identificam caminhos internos desses snapshots, não a versão atualmente implantada.

| Snapshot | SHA-256 do ZIP |
| --- | --- |
| `obcefem_api-main.zip` (`API:`) | `6be20b8df6f20bb3d20b7bc7d1b5f3f45dcb08c2b61073f1b0835cd8fa25c73c` |
| `obcefem-main.zip` (`FRONT:`) | `d27a336806e67ba9e2716b40ce33ab9c714771292f74443b62921636d2c2a54b` |

Na API foram inspecionados `app/main.py`, `config.py`, `repositorio.py`, `dominio.py`, README, os seis JSONs de `exemplos/`, o workflow de atualização e os consumidores em `front/`. No front institucional foram inspecionados `assistente.js` e as quatro páginas `dimensao-*.html`, incluindo dados embutidos, substituições de gráficos e `window.OBCFEM`.

“Verificado” abaixo significa conferido no código ou nos JSONs fornecidos. Não significa total reconciliado com ANM, fonte oficial consultada novamente, rota executada ou implantação testada. Os exemplos da API são snapshots, não gabaritos homologados. Não foi demonstrada nesta fase a existência de um pacote de produção homologado.

## 2. Mapa de rotas e consumidores

### API CFEM do ZIP

Prefixo de todas as rotas abaixo: `/api/v1`. Fonte: `API:app/main.py`, dependências `obter_filtros`, fábricas `_rota` e `_rota_dist`. Há **26 operações explícitas de negócio/sistema**, incluindo as criadas pelas fábricas. A documentação automática do FastAPI e os arquivos estáticos não entram nessa contagem.

| Método e sufixo | Resposta/uso real | Equivalente no protótipo local | Consumo no front |
| --- | --- | --- | --- |
| GET `/saude` | Estado de carga, modo, versão, última verificação/erro | Não há saúde; `/api/v1/status` é status de população | Painel da API consulta saúde; dimensões não consultam |
| GET `/meta` | Bases, municípios, anos, substâncias, cores e cobertura | Manifesto local não tem rota própria | Painel monta filtros |
| POST `/admin/atualizar` | 202 em servidor com token; 409 em pré-processado | Não existe | Botão administrativo do painel |
| GET `/indicadores` | Cartões de totais/foco/médias | Não existe | Painel de arrecadação/autuação |
| GET `/evolucao-anual` | Séries anuais | Não existe | Painel de arrecadação/autuação |
| GET `/comparacao-medias` | Municípios × médias PA/BR | Não existe | Painel de arrecadação/autuação |
| GET `/participacao` | Percentuais na região | Não existe | Painel de arrecadação/autuação |
| GET `/ranking` | Ranking regional | Não existe | Painel de arrecadação/autuação |
| GET `/serie-mensal` | Série mensal, somente arrecadação | Não existe | Painel de arrecadação |
| GET `/substancias` | Top N por substância | Não existe | Painel de arrecadação/autuação |
| GET `/mapa-calor` | Município × ano | Não existe | Painel de arrecadação/autuação |
| GET `/titulares` | Maiores titulares | Não existe | Painel de arrecadação/autuação |
| GET `/tabela-resumo` | Município × ano, totais e médias | Não existe | Painel de arrecadação/autuação |
| GET `/painel` | Todas as visualizações | Não existe | Download JSON do painel |
| GET `/exportar.csv` | Linhas regionais filtradas, BOM, `;`, vírgula decimal | CSVs de população e commodities, outros esquemas | Download CSV do painel |
| GET `/distribuicao/regras` | Percentuais e regimes da estimativa | Não existe | Painel de distribuição |
| GET `/distribuicao/indicadores` | Arrecadado e parcelas estimadas | Não existe | Painel de distribuição |
| GET `/distribuicao/fluxo` | Fluxo entre origens e destinos | Não existe | Painel de distribuição |
| GET `/distribuicao/destinos-anual` | Destinos por ano | Não existe | Painel de distribuição |
| GET `/distribuicao/comparacao-medias` | Cota estimada × médias | Não existe | Painel de distribuição |
| GET `/distribuicao/peso-nos-repasses` | Participações nas parcelas | Não existe | Painel de distribuição |
| GET `/distribuicao/ranking` | Cota municipal estimada | Não existe | Painel de distribuição |
| GET `/distribuicao/tabela-destinos` | Município × destino | Não existe | Painel de distribuição |
| GET `/distribuicao/tabela-resumo` | Cota estimada × ano | Não existe | Painel de distribuição |
| GET `/distribuicao/painel` | Todas as visualizações de distribuição | Não existe | Download JSON da distribuição |
| GET `/distribuicao/exportar.csv` | Município × ano × destino | Não existe | Download CSV da distribuição |

Os filtros efetivos incluem `base`, anos, meses, substâncias, agrupamento, tipo de titular, municípios por nome, denominador, exclusão do foco, `top_n` e `regra`. A base só admite arrecadação/autuação. Distribuição é derivada da arrecadação; não há base de repasse efetivo carregada. Metadados e saúde têm respostas próprias; só as visualizações usam `filtros`, `versao_dados`, `notas`, `dados`.

`API:front/comum.js` centraliza `fetch`, filtros e downloads; `app.js` e `distribuicao.js` definem as visualizações. Isso é distinto do site `obcefem`. Os links para a API nas páginas de dimensão são navegação para outro painel, não ingestão dos seus números.

`API:exemplos/openapi.json` declara 3.1.0 e apenas as 15 operações do primeiro grupo, sem as 11 de distribuição. Logo, está atrasado em relação a `app/main.py`. Os outros exemplos preservam estruturas próprias em `dados`; não contêm a lista comum de observações exigida por D7. `exemplos/meta.json` inclui fontes locais com URL e data de download nulas: não se pode completar proveniência por suposição.

### Protótipo local

Fonte: [servidor.py](../../scripts/servidor/servidor.py), método `_rotear`, e [OpenAPI local](../api/openapi.yaml). Todas as operações são GET.

| Rota | Comportamento conferido | Relação com as dimensões |
| --- | --- | --- |
| `/api/v1/populacao` | Lista de observações; filtro `municipio_id`; 503 sem publicação | Candidata para Social; não há chamada no HTML |
| `/api/v1/populacao.csv` | Exporta população; não aplica o filtro municipal da rota JSON | Candidato a download futuro |
| `/api/v1/commodities` | Lista provisória; filtro `indicador`; 503 sem série | Candidata para Econômica após homologação para gráficos |
| `/api/v1/commodities.csv` | CSV provisório com filtro `indicador` | Não equivale à garantia de gráficos homologados |
| `/api/v1/despesa-funcao` | Três estágios separados; 503 quando não publicada | Lacuna nas quatro dimensões; contas/reconciliação pendentes |
| `/api/v1/status` | Só população: situação, referência e atualização | Insuficiente para status de todos os indicadores |
| `/status` | HTML de status do manifesto | Não é rota de saúde |

Não existem rotas locais de CFEM, dimensões ou assistente. A existência de leitor de arquivos não comprova homologação do conteúdo nele colocado. O pipeline de população exige reconciliação; commodities são gravadas como provisórias; o coletor DCA não homologa. O caminho padrão do manifesto no servidor usa `parents[2] / "data"`, que aponta para `scripts/data`, diferente de `data/indicadores.json` na raiz; registrar para correção do laboratório em trabalho próprio.

### Contrato efetivamente disponível no assistente

`FRONT:assistente.js`, linhas 169–173, retorna em `contexto()`:

```text
pagina, dimensao, tema { id, titulo }, periodo [de, ate],
comparacoes [], graficos [{ i, titulo, tipo, real }]
```

**O contexto atual não envia valores dos gráficos**, apesar do resumo da tarefa. Os valores são acessíveis localmente por `OBCFEM.grafico(temaId, i)` em `dados` e `filtrado`. O comentário de `responder()` prevê `{ pergunta, contexto, historico }`; o histórico é intenção, sem esquema HTTP implementado. `perguntar()` chama `responder()` via `setTimeout`, sem `fetch`. Não existe resposta JSON consumida hoje.

| Capacidade já existente | Ligação proposta à resposta futura |
| --- | --- |
| `escolherTema(id)` | Ação de selecionar aba válida |
| `definirPeriodo(de, ate)` | Ação de período; a UI aproxima para anos disponíveis |
| `definirSeries(nomes)` | Ação de comparações; só nomes existentes, ao menos um válido |
| `restaurar()` | Restaurar filtros |
| `destacar(temaId, i)` | Destacar gráfico com índice conferido |
| `irPara(pagina, tema, i)` no assistente | Navegar entre as quatro dimensões por caminho predefinido |

**PROPOSTA:** entrada conserva pergunta e contexto com esses campos; histórico, se aceito, será opcional e limitado. Saída estruturada com `resposta`, `citacoes`, `limitacoes`, `acoes`; nomes e DTOs das ações serão definidos na Fase 2. Citação contém indicador, fonte, período, edição e referência à observação consultada. Não existe executor remoto de ações no front: integrar exige alteração futura no repositório somente leitura, mediante autorização separada. Texto do LLM não deve ser inserido como HTML arbitrário; o front atual renderiza HTML produzido localmente.

## 3. Dimensões, blocos e disponibilidade

Esta correspondência entre navegação e blocos é **PROPOSTA**, não nova regra de negócio. “Real no front” significa somente `real: true` ou uso de `REAL(...)` no snapshot. Não equivale a pipeline, reconciliação ou homologação. Os dados das quatro páginas são embutidos em `dadosDimensao()`, com selos derivados desse atributo.

| Dimensão / abas | Blocos de BLOCOS | Evidência de dado real | Lacunas da camada publicada — EM ABERTO |
| --- | --- | --- | --- |
| Social / `populacao` | 1 — Dinâmica Populacional | HTML marca população, crescimento e estrutura etária como reais. Manifesto tem `populacao_estimada`; reconciliação de 2025/2026 documentada em pendências §4 | Censo, pirâmides e crescimento não são a série de estimativas. Pacote homologado para produção ainda precisa ser fornecido/verificado |
| Social / `trabalho` | 2 — Economia e Mercado de Trabalho | HTML rotula emprego/população, setores, remuneração, escolaridade e trabalho por sexo como reais | Sem pipeline publicado de emprego/renda. Não converter valores do HTML em observações validadas; separar RAIS e CAGED |
| Social / `educacao`, `saude`, `pobreza`, `seguranca`, `moradia` | 4 — Sociedade; despesas no 6; saneamento também no 5 | HTML rotula IDEB, mortalidade, CadÚnico, violência, infraestrutura, frota e algumas despesas como reais | Sem pipeline homologado desses indicadores; saúde e saneamento EM ABERTO. Despesas dependem de RN-FNT-04; comparações usam universos distintos |
| Econômica / `crescimento` | 2 | PIB per capita rotulado real no HTML | PIB, VAB e participações sem pipeline publicado; denominador regional pendente em RN-IND-09 |
| Econômica / `precos` | 2 e 3 — Mineração e CFEM | Manifesto: `preco_minerio_ferro`, `preco_cobre`, provisórios. API tem arrecadação/autuação e repartição estimada | Gráficos de preços e cota desta aba são demonstrativos. FRED ainda sem reconciliação; CFEM da API sem homologação demonstrada; distribuição recebida não é estimativa |
| Econômica / `financas`, `gasto` | 6 — Finanças Públicas; CFEM no 3 | HTML rotula composição de receita, ICMS, impostos, peso CFEM e algumas despesas como reais | Manifesto só prevê os três estágios de despesa, bloqueados; receitas/investimentos não têm publicação homologada. Explorador é demonstração, não API SICONFI |
| Ambiental / `uso` | 5 — Meio Ambiente e Saneamento | Duas roscas de Canaã (1985/2025) rotuladas reais; série intermediária explicitamente ilustrativa | Sem pipeline publicado MapBiomas; interpolação não vira dado real. Coleção/edição e cobertura municipal precisam ser comprovadas |
| Ambiental / `emissoes`, `saneamento` | 5 e 6 | Saneamento domiciliar e despesa de saneamento rotulados reais; emissões demonstrativas | SEEG e saneamento sem pipeline homologado; contas de despesa pendentes |
| Institucional / `sustentabilidade` | 6 (compostos) | Barômetro 2022 e IDSC 2025 rotulados reais | Sem artefato congelado com edição verificada na camada publicada; não recalcular os compostos |
| Institucional / `receita`, `gestao` | 6; itens de gestão sem correspondência integral nos blocos | Relação receita × IDSC, ranking CLP, qualidade contábil, conselhos e servidores são demonstrações no snapshot | Sem pipeline e sem definição completa para os itens adicionais de gestão; não inventar indicador ou ampliar o manifesto como decisão |

Fontes: `FRONT:dimensao-social.html` §`dadosDimensao` (203–298), econômica (203–320), ambiental (203–272, incluindo substituição por roscas), institucional (196–225); [manifesto](../../data/indicadores.json); [pendências](../regras-de-negocio/pendencias.md) §2 e §4. O manifesto tem sete indicadores, não um catálogo completo dos gráficos. Não inventar IDs para os ausentes.

## 4. Alternativas de arquitetura

### 4.1 Onde mora a produção

| Alternativa | Vantagens | Custos / restrições |
| --- | --- | --- |
| Evoluir `obcefem_api` | Reaproveita operação, painel, filtros e cálculos | Repositório somente leitura nesta tarefa; exigiria autorização e mudança de escopo. Ainda falta homologação e D7 |
| Serviço novo em `backend/` neste repositório | Respeita a separação de `scripts/`; permite DTOs e testes independentes | Passa a coexistir produção com pesquisa; requer aprovação explícita e atualização da descrição do projeto |
| BFF que apenas encaminha HTTP à API | Menos duplicação de cálculo; adapta formato para as dimensões | Disponibilidade/latência dependentes da API; não cria proveniência nem homologação ausentes; a API só cobre CFEM |

**Recomendação PROPOSTA:** serviço novo em `backend/` com papel de BFF (API voltada ao front), leitura de publicações e cálculos determinísticos limitados. Localização e papel não são opções mutuamente exclusivas. Não importar módulos de `scripts/` no runtime de produção, nem copiar a API inteira. Só implementar após aprovação desta localização. A coleta permanece fora do ciclo da requisição.

Estrutura futura sugerida, ainda não criada:

```text
backend/
  pyproject.toml, uv.lock, .env.example
  app/main.py
  app/controllers/       # HTTP e validação de entrada
  app/services/          # consultas, cobertura, citações e ações permitidas
  app/dtos/              # Observacao, envelopes e assistente
  app/repositories/      # leitura do pacote publicado e interface de acesso
  app/llm/               # interface de redação e mock
  tests/                 # testes da produção; separados do laboratório
  Dockerfile, docker-compose.yml
docs/api/openapi-producao.yaml
.github/workflows/backend.yml
```

`backend/pyproject.toml` e lock próprios evitam misturar dependências do produto com o laboratório (`package = false` na raiz). Python ≥3.12, dependências adicionadas por `uv add`. Não se cria serviço auxiliar, volume ou banco nesta proposta.

Na Fase 1, permitir explicitamente `backend/.env.example` no `.gitignore`: o padrão atual `.env.*` também ignora exemplos. O arquivo conterá apenas nomes e valores não secretos.

### 4.2 Fonte de dados: HTTP ou parquet

| Opção | Vantagens | Limitações |
| --- | --- | --- |
| HTTP da `obcefem_api` | Usa consultas prontas, filtros e versão | `dados` é agregado para visualização; não fornece todas as observações/metadados exigidos. Não homologar por HTTP 200; limite de resposta e indisponibilidade propagam |
| Parquet da `obcefem_api` | Mais granularidade e sem salto HTTP durante consulta; adequado ao modo pré-processado | Acoplamento ao esquema interno, carga em memória e atualização por pacote; parquet processado não prova homologação. Falta população e demais dimensões |
| Pacote da camada publicada com observações e evidências | Mesma versão para API, CSV e assistente; independe do formato interno da API | Exige definir produtor, entrega e metadados de homologação; hoje não demonstrado |

**PROPOSTA:** começar pela interface de leitura de pacote publicado imutável, com observações e metadados de qualidade/versão, incorporado ao artefato de implantação. População é candidata inicial; se não houver pacote verificado, responder “sem dado validado”. JSON já é usado no laboratório e basta ao primeiro recorte; parquet pode ser formato de armazenamento posterior sem virar contrato público. Não incluir dados brutos no Git.

HTTP/parquet da API são candidatos a adaptadores de entrada, não selo de publicação. Para liberar CFEM, será necessário obter evidência de reconciliação e proveniência do recorte; a Fase 1 não realizará um pipeline novo implicitamente. Sem isso, status explicita a lacuna. **EM ABERTO:** produtor responsável, transporte do pacote e atualização de produção; o arquivo periódico de versões ANM nesta `develop` é evidência bruta, não homologação.

### 4.3 Assistente na Vercel

| Opção | Vantagem | Desvantagem |
| --- | --- | --- |
| Resposta JSON dentro da requisição | Compatível com o contrato pretendido; testes offline simples | Depende do prazo da função e do provedor; demanda limites e tratamento de timeout |
| Streaming | Pode mostrar texto progressivamente | Front não implementa esse protocolo; aumenta a superfície de contrato |
| Job assíncrono com polling/fila | Permite processamento demorado | Exige estado/serviço extra e muda o contrato; fora do pedido |

**PROPOSTA:** JSON síncrono, sem thread contínua, fila ou escrita durável. Primeiro valida filtros/contexto, consulta observações homologadas, calcula números deterministicamente e só então chama a interface do LLM para redigir. Recusa de lacuna não depende do provedor. RAG restrito ao manifesto, glossário e regras com status, exceções, seção e versão; busca local simples é suficiente inicialmente, sem banco vetorial. Nunca executar código, SQL, URL ou instrução livre vinda de pergunta, contexto ou texto recuperado. O contexto da página, incluindo `real`, não é fonte de verdade.

Timeout do provedor deve caber na duração da função; não fixar capacidade de plano sem conferir o projeto implantado. Limitar corpo, histórico, resultados e saída; respostas/CSVs serão recortados para caber no limite da plataforma. Chave só em variável de ambiente, com `.env.example` sem valores secretos. Modo mock deve ser explícito e não fabricar números de domínio.

O limite documentado de corpo de requisição/resposta é 4,5 MB; memória local não deve ser usada como cota global de usuários. **PROPOSTA:** proteção de taxa da plataforma mais limite local defensivo; **EM ABERTO:** plano/capacidade da conta, configuração de taxa e orçamento. Sem mecanismo global verificado, não afirmar que um contador em memória protege todas as instâncias. Isso não autoriza acrescentar Redis ou outro serviço.

Fontes oficiais consultadas em 11/11/2026: [limites de Functions](https://vercel.com/docs/functions/limitations) e [duração](https://vercel.com/docs/functions/configuring-functions/duration). O código `API:app/config.py` reconhece `/tmp` como gravável: a premissa “sem disco gravável” significa aqui sem persistência confiável, não inexistência absoluta de área temporária. `repositorio.garantir()` carrega parquet sob demanda; o agendador só inicia no modo servidor.

### 4.4 Resposta híbrida e compatibilidade

Base normativa: [RN-MOD-03 e RN-MOD-04](../regras-de-negocio/modelo-de-dados.md), exceção de 08/11/2026 (D7). Manter `filtros`, `versao_dados`, `notas`; `dados` passa a lista de observações, uma por valor. Séries com cores/rótulos podem acompanhar em campo extra opcional.

Campos de `Observacao`: `indicador`, `municipio_id`, `municipio_nome`, `nivel_territorial`, `ano`, `mes`, `valor`, `unidade`, `natureza_valor`, `estado_validacao`, `fonte`, `edicao_fonte`, `atualizado_em`, `versao_tratamento`. Mês nulo em anuais; ausência é nulo com natureza explícita, nunca zero. Metodologia e limitações são resolvidas no manifesto, sem inventar proveniência. Status operacional por indicador não é natureza do valor nem status da regra.

| Opção | Consequência |
| --- | --- |
| Substituir `dados` nas rotas existentes da API | Cumpre D7, mas quebra consumidores que esperam objetos e não é permitido alterar o outro repositório |
| Novas rotas de dimensão no serviço proposto | Cumpre D7 sem modificar o painel atual; requer integração futura do site. Recomendada |
| Manter só séries e acrescentar metadados gerais | Menos alteração, mas não cumpre D7; descartada |

**EM ABERTO:** o esquema enumera município/RI, enquanto commodities são globais (RN-MOD-19), e médias PA/BR/grupos da API não são municípios. Propor nível global e representação explícita dos agregados; não atribuir código de município fictício nem reutilizar o nome de um município. Não publicar essas observações até validar a representação com o mantenedor. O esboço local já aceita campos municipais nulos, mas não decide essa extensão da regra.

Na Fase 1, propor GET `/api/v1/dimensoes/{dimensao}`, exportação CSV correspondente, status por indicador e `/saude` (com eventual alias `/api/v1/saude` para familiaridade). Esses caminhos são desenho técnico a confirmar, não rotas existentes. Indicador conhecido sem publicação terá motivo explícito e nenhuma observação inventada; indicador desconhecido, entrada inválida e falha operacional serão distinguidos. CSV deve ter filtros equivalentes ao JSON e metadados de fonte, edição, método e limitações. Dado fictício fica em demonstração do front com rótulo obrigatório, fora da camada publicada e das respostas numéricas do assistente (RN-ENT-11).

### 4.5 OpenAPI

**Diretriz do pedido:** 3.1 em arquivo novo, preservando `docs/api/openapi.yaml`. **PROPOSTA técnica:** `docs/api/openapi-producao.yaml`, 3.1.0 inicialmente, com componentes e exemplos de lacuna, parcialidade, erro e resposta híbrida; comparar com o esquema gerado pelo aplicativo. 3.0 daria compatibilidade com clientes antigos, mas exigiria tradução de nulabilidade e contraria o pedido sem benefício demonstrado. Uma revisão posterior de 3.1 pode ser avaliada sem mudar a semântica de versão da API.

O esboço local e o snapshot OpenAPI da API usam 3.1.0. A especificação 3.1 alinha o Schema Object ao JSON Schema 2020-12; referência oficial: [OpenAPI 3.1.0](https://spec.openapis.org/oas/v3.1.0). Não pressupor que o snapshot desatualizado inclua as rotas de distribuição.

## 5. Conflitos que não podem virar decisão por implementação

| Constatação | Regra / fonte | Tratamento nesta proposta |
| --- | --- | --- |
| Produção em repositório descrito como pesquisa; `scripts/` só laboratório | `AGENTS.md`, README | Propor `backend/` e aguardar aprovação antes de criar |
| CFEM da API não demonstra homologação | RN-VPU-07, 08, 10 e 12; divergências §Em aberto | Não liberar para gráficos/assistente só porque está processada ou online |
| Duplicatas aceitas, mas README/manifesto ainda dizem bloqueio por duplicatas | Exceção RN-VPU-11 de 08/11/2026; pendências §4 | D2 não substitui reconciliação. Registrar defasagem; não reescrever história nem promover estado |
| Ano parcial por volume na API e regra geral de meses completos | Exceções RN-CFE-05/06 versus RN-VPU-05 | Preservar exceções específicas; harmonização textual e efeito por indicador EM ABERTO |
| Nome municipal na API versus código na observação | D5/RN-TER-03 e D7/RN-MOD-03 | Adaptador com de-para oficial; não converter médias e grupos em municípios |
| Repartição estimada apresentada como distribuição | RN-CFE-25/26; `API:app/dominio.py` | Distinguir estimativa e recebida; início da regra e cota dos afetados continuam EM ABERTO, sem novo parecer jurídico |
| `real: true` no HTML sem evidência de homologação | RN-VPU-09/10, RN-ENT-11 | Selo não basta. Despesas, emprego, saúde, saneamento e compostos não são liberados |
| Preços demonstrativos citam Pink Sheet; coletor usa FRED provisório | RN-TMP-12/13/14, RN-MOD-19 | Não calcular média anual incompleta nem preencher meses; início efetivo do ferro e representação global pendentes |
| Grupos de comparação no site diferem da API | RN-TER-09, RN-CFE-27 | “Mineradores do PA”, “média do PA” e RI não são sinônimos; não fazer mapeamento silencioso |
| Catálogo incompleto e textos antigos de licença | RN-MOD-25; obsolescência RN-PRI-01 a 06/08 e RN-ENT-10 | Revisão futura do manifesto; não criar bloqueios de privacidade/licença |
| Metadados CSV e assistente são regras PROPOSTAS, embora pedidos para as próximas fases | RN-ENT-05/07/08 | Implementar no escopo aprovado, sem mudar automaticamente o status documental; metas numéricas EM ABERTO |
| Atualização diária da API versus agenda mensal da CFEM | RN-TMP-02; workflow `atualizar-dados.yml` | Execuções diárias verificadas no YAML, não no histórico de runs; frequência de checagem não prova nova edição mensal nem homologação |
| Contexto sem números e ausência de cliente HTTP de IA | `FRONT:assistente.js` §contexto/perguntar | Preservar forma existente; mapear gráficos a indicadores no servidor, com integração do front pendente |

As fontes históricas não foram alteradas. Nenhuma nova exceção ou mudança de status foi decidida nesta fase; por isso as propostas arquiteturais ficam neste ADR. Aprovação que contrariar regra deverá ser registrada no campo Exceções e em `pendencias.md`, com totais e referências cruzadas quando aplicável.

## 6. Plano das Fases 1 a 5

Cada fase exige aprovação da anterior, branch nova baseada na `develop` atualizada e PR para `develop`. Não iniciar a seguinte apenas por terminar o PR; não fazer merge automaticamente. Testes de cada entrega acompanham a fase; a Fase 5 consolida cobertura e CI, sem postergar verificações essenciais.

| Fase | Arquivos/entrega propostos | Critério de conclusão e comandos planejados |
| --- | --- | --- |
| 1 — API por dimensão | `backend/app/{controllers,services,dtos,repositories}`, configuração e `.env.example`; status, CSV e saúde | Contrato híbrido, filtros consistentes, ausências explícitas, só publicação comprovada. `uv run --project backend pytest`; `uv run --project backend ruff check backend`; execução local por `uv run --project backend uvicorn app.main:app --app-dir backend` |
| 2 — Assistente | `backend/app/llm`, controller/service/DTO do POST; corpus explicativo e conjunto de avaliação | Consultas determinísticas, citações rastreáveis, recusa sem dado, mock offline, limites, ações permitidas, injection testada. Mesmos comandos de teste/lint; testes específicos no conjunto `backend/tests`. Integração do front depende de autorização no outro repo |
| 3 — Docker | `backend/Dockerfile`, `backend/docker-compose.yml` mínimos | Um worker, sem volumes, pacote publicado incorporado; iniciar/consultar saúde e dados sem chave LLM. `docker compose -f backend/docker-compose.yml build` e `up`; verificar também o modo pré-processado sem agendador |
| 4 — OpenAPI | `docs/api/openapi-producao.yaml` e exemplos | 3.1, todas as rotas novas, observação/envelope, parâmetros, lacunas/erros; esquema confrontado com app. Não sobrescrever o esboço local; teste de contrato em `backend/tests` |
| 5 — Testes e CI | Testes unitários, integração/contrato e `.github/workflows/backend.yml` | LLM mockado; sem credenciais ou fontes ao vivo; lint, pytest e build de imagem. Avaliação cobre 12 municípios, fonte/período/edição, recusa, custo e latência medidos; metas continuam EM ABERTO |

Gabaritos numéricos da avaliação virão de observações de edição homologada, com consulta determinística reproduzível. Fixtures sintéticas testam o software e devem ser identificadas como tal; não demonstram verdade de domínio. Casos de ausência incluirão despesa bloqueada, ano incompleto, gráfico fictício, município sem observação e instruções maliciosas no contexto. Fórmulas de crescimento, participação e comparação só entram quando o método estiver definido, sem cálculo delegado ao LLM.

## 7. Entrega, verificações e aprovação

Estrutura alterada nesta fase: este ADR e um link em `docs/README.md`. Os arquivos completos estão no diff do PR. Não há aplicação de produção para executar nesta entrega.

Comandos de verificação da Fase 0, na raiz:

```powershell
uv run ruff check
uv run pytest
uv run python -m scripts.cfem.checar_totais_regras
git diff --check
```

Verificações executadas em 11/11/2026: `uv run pytest` passou (19 testes); `checar_totais_regras` confirmou 173 regras (126 DECIDIDAS, 34 PROPOSTAS, 5 EM ABERTO, 8 OBSOLETAS); `git diff --check` passou e todos os links locais deste ADR foram encontrados. `uv run ruff check` falhou com 92 apontamentos em código preexistente, incluindo arquivos da pasta local não versionada `.codex-worktrees/`; não houve alteração Python nesta fase. O lint não está verde e esses problemas não foram corrigidos neste PR documental. O `uv` não estava no PATH: foi instalado apenas em `tmp/fase0/ferramentas/`, e o ambiente foi sincronizado com `uv sync --frozen`, sem mudança no lock.

Nenhum teste dos ZIPs, requisição às APIs de produção, nova coleta oficial, reconciliação dos valores dos exemplos, inspeção do conteúdo parquet, medição de memória/latência/custo, build Docker ou deploy foi realizado. A análise estática do workflow não confirma sucesso de execução nem configuração real da Vercel.

**PROPOSTAS para aprovação:** `backend/` como serviço/BFF separado do laboratório; interface para pacote publicado imutável; contrato híbrido nas novas rotas; assistente JSON síncrono, mock e busca documental local; OpenAPI 3.1 em arquivo novo; plano faseado acima.

**EM ABERTO:** responsável e mecanismo de entrega da publicação homologada; homologação CFEM; representação global e de médias/grupos; integração autorizada do front; pipelines de emprego/saúde/saneamento e demais lacunas da tabela; provedor/modelo, orçamento, limites de taxa/entrada e plano Vercel; metas da avaliação; pendências normativas já listadas. Nenhuma dessas lacunas permite inventar valores.

**Ponto de parada:** aguardar aprovação do mantenedor para a Fase 1 e, em particular, para hospedar produção em `backend/`. A confirmação é exigida explicitamente pela tarefa, seção 2 (“Proponha o local na Fase 0 e aguarde minha confirmação”) e seção 3 (“uma por vez”).
