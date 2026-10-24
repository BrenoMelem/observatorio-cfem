# Observatório RI Carajás — Registro de Decisões

Oct 4, 2026 · @Daniel Rond

> Exportado do Claude Docs em 24/10/2026 (revisão 72). Conteúdo mantido como no original.

Registra as decisões do observatório — arquitetura, estratégia de fontes, municípios, tabelas, rotas de coleta e a justificativa de cada escolha —, além das fontes verificadas e das pendências. As tabelas de indicadores de cada bloco estão no documento Blocos Temáticos.

## Arquitetura e padrões de dados

Quem consome os dados nunca fala direto com as fontes: entre as duas pontas há uma camada intermediária de dados já tratados, padronizados e versionados. Uma fonte fora do ar não quebra nada, trocar a origem de um indicador não afeta o gráfico, e os dados servem a qualquer destino.

**Esquema único de saída.** Todo indicador, qualquer que seja a origem, vira o mesmo registro: `municipio_id`, `municipio_nome`, `ano`, `mes` (opcional), `indicador`, `valor`, `unidade`, `fonte`, `atualizado_em`. O campo `mes` é proposto por causa da CFEM (ver Bloco 3; aceite ainda pendente — ver Pendências): fica vazio nos indicadores anuais e preenchido só onde a fonte oferece detalhe mensal. Princípio geral: guardar sempre na granularidade mais fina da fonte e agregar só na saída.

**Manifesto `indicadores.yaml`.** Um único arquivo descreve cada indicador — id, nome, bloco, fonte, método, frequência, script responsável e a estratégia (ver compostos). É a fonte da verdade: documentação, agenda e configuração no mesmo lugar. A lista de municípios de comparação da mineração também mora aqui.

**Um adaptador por fonte, não por indicador.** Um módulo para o IBGE, um para o SICONFI, um para a Base dos Dados. Os indicadores viram configuração que chama esses adaptadores, evitando 45 scripts quase idênticos.

**Separar `raw` de `processed`.** Download bruto em `data/raw/` (fora do git quando grande); resultado tratado em `data/processed/` (versionado). Se um parsing falhar, dá para reprocessar sem baixar tudo de novo.

**Proveniência embutida.** Cada arquivo processado carrega quando foi gerado, de qual fonte e de qual ano-base, para o site exibir "atualizado em" e tornar óbvio quando algo parou.

**Validação antes de publicar.** Checagens simples: o município existe, o valor não é nulo, a série não encolheu, o número está numa faixa plausível. Se falhar, o pipeline mantém o dado antigo e abre uma issue em vez de publicar lixo. (Exceção conhecida: autuações da CFEM encolhem legitimamente — ver Bloco 3.)

**Uma agenda por fonte.** Mensal para CAGED, veículos, commodities e CFEM. Anual para Censo, PIB, SICONFI, INEP, MapBiomas e SEEG. Sob demanda para FAPESPA e CadÚnico. A cada eleição (bianual) para o eleitorado do TSE. Cada uma com seu próprio workflow agendado. O agendador roda o ETL, grava o tratado e registra a versão — GitHub Actions serve bem.

## Estratégia de fontes e acesso

**Fonte primária onde há API boa; Base dos Dados onde ela é a via prática.** IBGE SIDRA e SICONFI têm API própria — vá direto na primária. RAIS, IDEB, eleitorado (TSE) e Censo Escolar (INEP) chegam tratados e já com código IBGE pela Base dos Dados, no BigQuery — nesses casos, use a BD (TSE e INEP também têm download direto, como alternativa). CAGED e SIM têm rotas diretas: IPEADATA para o saldo de emprego e PySUS para os microdados de saúde, com a BD como alternativa. Nenhum item via BigQuery é fonte primária: MTE, DATASUS, INEP e TSE não publicam no BigQuery.

**A BD nunca é fonte primária — sempre citar a origem.** Na procedência, escreva "RAIS via Base dos Dados", nunca só "Base dos Dados". O prefixo `br_` nos nomes de tabela é a convenção da BD; sempre que aparecer, você está falando com a BD, não com o órgão.

**O ponto fraco da BD é a atualização, não a confiabilidade.** O tratamento deles é bom, mas a reingestão depende da comunidade e é irregular — por isso o Censo 2022 ainda não está lá no nível de detalhe necessário e o SIM começa só em 1996. Consequência: é justamente no bloco de emprego/educação/violência que a regra "descobrir o ano mais recente em tempo de execução" mais importa, porque é onde a BD pode ter parado sem aviso.

**Credencial única do Google Cloud.** O BigQuery exige autenticação: criar projeto no Google Cloud, ativar o BigQuery, gerar uma service account e guardar a chave JSON como secret no GitHub, nunca no código. O volume do projeto cabe na faixa gratuita (1 TB de consulta/mês). A mesma credencial serve para o Google Earth Engine do Bloco 5 (vegetação e mapas) — é um ponto único de autenticação, não duas frentes.

**Regra geral de método.** Automatizar onde há API; aceitar download onde a fonte publica arquivo estável; documentar como manual onde só há PDF. Um scraper de PDF frágil dá mais trabalho do que baixar o arquivo uma vez por ano.

**Emprego formal (CAGED) — IPEADATA como rota primária da série.** O saldo de emprego do Bloco 2 vem do IPEADATA (ambiente Regional), que serve dados do CAGED por API, filtrando pelo código IBGE de 7 dígitos na coluna `TERCODIGO`. Não há série municipal pronta de saldo: puxa-se `ADMISNC` (admissões) e `DESLIGNC` (demissões) do Novo CAGED e deriva-se o saldo — o que ainda rende admissões e demissões como indicadores próprios. Vantagem sobre a BD: API estável, sem FTP nem cadência de reingestão de terceiros. As duas séries estão confirmadas por município (Canaã e Parauapebas, 2020–2026, 80 meses cada). A Base dos Dados (BigQuery) fica como alternativa e para microdado; o painel BI do MTE serve só para conferência manual. As quebras por setor, escolaridade e remuneração continuam na RAIS via Base dos Dados — o IPEADATA não as substitui.

## Municípios da RI Carajás

A RI Carajás tem 12 municípios, conforme a [Estatística Municipal da FAPESPA](https://www.fapespa.pa.gov.br/estatistica-municipal/). Esta lista fixa quais municípios entram em toda agregação regional.

| Município | Código IBGE |
| --- | --- |
| Bom Jesus do Tocantins | 1501576 |
| Brejo Grande do Araguaia | 1501758 |
| Canaã dos Carajás | 1502152 |
| Curionópolis | 1502772 |
| Eldorado do Carajás | 1502954 |
| Marabá | 1504208 |
| Palestina do Pará | 1505494 |
| Parauapebas | 1505536 |
| Piçarra | 1505635 |
| São Domingos do Araguaia | 1507151 |
| São Geraldo do Araguaia | 1507458 |
| São João do Araguaia | 1507508 |

Os 12 códigos foram validados contra a [API de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) (out/2026); o nome oficial é "Eldorado do Carajás", não "dos". O pipeline repete essa checagem na largada e avisa se algum nome deixar de corresponder. A lista fica num arquivo de configuração (`municipios.yaml`) com a citação da FAPESPA.

## Tabelas da Base dos Dados confirmadas

Tabelas da Base dos Dados usadas pelo projeto, conferidas no [catálogo](https://basedosdados.org) em out/2026, com o `dataset.table_id` completo, o ano mais recente e a coluna de município. Mesmo assim, o pipeline descobre o ano máximo em tempo de execução (`SELECT MAX(ano)`), nunca cravado no código.

| Indicador | dataset.table\_id | Ano mais recente | Coluna município |
| --- | --- | --- | --- |
| População | `br_ibge_populacao.municipio` | 2025 | `id_municipio` (7 díg.) |
| PIB | `br_ibge_pib.municipio` | 2023 | `id_municipio` (7 díg.) |
| Novo CAGED | `br_me_caged.microdados_movimentacoes` | 2026-08 | verificar (ver nota) |
| RAIS (vínculos) | `br_me_rais.microdados_vinculos` | 2025 | `id_municipio` |
| IDEB | `br_inep_ideb.municipio` | 2025 | verificar (ver nota) |
| SIM / óbitos | `br_ms_sim.municipio_causa` | 2026 (início 1996) | `id_municipio` |
| SICONFI | `br_me_siconfi` — escolher demonstrativo | 2025 | `id_municipio` |

Dois pontos ficaram sem certeza na conferência e devem ser checados no dicionário da própria tabela antes de programar: a coluna de município na tabela nova do **CAGED** (`microdados_movimentacoes`) e no **IDEB** (`municipio`). O padrão da BD é `id_municipio` de 7 dígitos, mas isso não foi confirmado nessas duas.

Duas observações de uso: o **CAGED** atual é `microdados_movimentacoes` (pós-2020) — a `microdados_antigos` vai só até \~2019. O **SICONFI** tem várias tabelas-filhas; é preciso escolher o demonstrativo (ex.: `municipio_despesas_funcao` para despesa por função). As tabelas de RAIS e CAGED são grandes demais para baixar pela interface: o acesso tem de ser por SQL filtrando os municípios, nunca a tabela inteira.

## Rotas de coleta por fonte

Rotas de acesso por fonte. O status de verificação de cada link e código está na seção Fontes; o que ainda não foi testado precisa de um pull de teste com os códigos 1502152 e 1505536 antes de entrar no código.

| Tema / indicador | Fonte e método | Chave de acesso | Observação |
| --- | --- | --- | --- |
| Censo 2022 (favelas, entorno, domicílio, saneamento, rendimento, instrução) | SIDRA API | agregados 9900, 6591, 9923, 9922, 10296, 10061 | "Infraestrutura" não tem agregado próprio — cai em 6591/9922 |
| PIB municipal | SIDRA API (não IPEADATA) | agregado 5938 | traz VAB por setor; IPEADATA achata isso |
| População | SIDRA API | agregado 6579 (estimativas) + censos | — |
| Número de eleitores | Base dos Dados (TSE) / BigQuery | `perfil_eleitorado_municipio_zona` | total e gênero; `table_id` a confirmar; alternativa: TSE download |
| Preço de minério de ferro e cobre | FRED API | `PIORECRUSDM` (ferro), `PCOPPUSDM` (cobre) | global, não municipal; exige API key grátis; ferro só desde 1992 |
| Emprego formal (saldo) | IPEADATA Regional | `ADMISNC` − `DESLIGNC` | confirmado por município (2020–2026) |
| Taxa de homicídio | IPEADATA / Atlas da Violência | `AVIOL12_THOMIC` | municipal confirmado (1989–2022); substitui calcular do SIM |
| Demais indicadores de saúde | DATASUS via PySUS | SIM, SINASC, SIH, SIA, CNES | microdados `.dbc` → DataFrame; agregar por município |
| Censo Escolar (matrícula, infraestrutura escolar) | Base dos Dados (INEP) / BigQuery | tabela `escola` | `table_id` a confirmar; alternativa: INEP download |
| Despesa por função (2013+) | SICONFI API (DCA) | `/dca` · `id_ente` · `an_exercicio` · `no_anexo=DCA-Anexo I-E` | funções no campo `conta`; último ano fechado 2025 |
| Finanças históricas (pré-2013) | IPEADATA (FINBRA) | `FINBRA_DESP`, `FINBRA_REC` | só se precisar da série longa |
| IDH-M | Atlas Brasil (opcional) | download — a confirmar | não é indicador do plano; decenal (parado em 2010); `ADH_IDHM` no IPEADATA não veio municipal |
| Uso do solo (MapBiomas) | Google Earth Engine (`earthengine-api`) | Coleção 11, raiz `projects/mapbiomas-public/assets/brazil/lulc/collection11/` | asset ainda não testado; sem API tabular; Community Tier 150h EECU/mês grátis; mesma credencial do BigQuery |
| CFEM arrecadada | ANM, CSV direto | `dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv` | nacional, mensal, municipal (`CodigoMunicipio`) |
| CFEM recebida (distribuição) | ANM, CSV direto | `dadosabertos.anm.gov.br/CFEM/CFEM_Distribuicao.csv` | filtrar por `CodigoEnte` |
| Autuações da CFEM | ANM, CSV direto | `dadosabertos.anm.gov.br/CFEM/CFEM_Autuacao.csv` | separador `;`; município por nome; sem coluna de situação |
| VPM (valor da produção mineral) | ANM, AMB (CSV) | `dadosabertos.anm.gov.br/AMB/` | confirmado só por UF (sem coluna de município); separador vírgula |
| Pobreza (CadÚnico) | CECAD 2.0 | — | sem API; só download manual |
| Frota de veículos | Senatran via dados.gov.br | — | sem API paramétrica; raspar o link do mês e filtrar |
| Emissão de CO₂ | SEEG | — | sem API confirmada; download manual XLSX/CSV |

**Commodities: FRED em vez do Pink Sheet.** O World Bank Pink Sheet é só planilha para download; o FRED (Federal Reserve) espelha a série do IMF por API REST estável, que é o padrão para pipelines. O custo é que a série de minério de ferro (`PIORECRUSDM`) começa em 1992. Para os anos 1985–1991, a saída é congelar esse trecho do Pink Sheet uma vez e emendar — um caso a mais de "congelar com citação".

**Homicídios: IPEADATA, não SIM cru.** Calcular a taxa de homicídio a partir dos microdados do SIM é um erro metodológico — muitas mortes entram como "causa indeterminada". O Atlas da Violência (IPEA) redistribui essas mortes e publica a taxa corrigida, acessível por `AVIOL12_THOMIC` no `ipeadatapy`. Para a *taxa*, essa é a rota; o SIM/PySUS segue útil para os demais indicadores de saúde.

**Autuações da CFEM.** A ANM publica o CSV de autuações da CFEM (`CFEM_Autuacao.csv`, ver Fontes). Ressalvas do arquivo: separador `;`; traz só a data de publicação (lavratura), não o fato gerador; o município vem por nome, sem código; a empresa autuada é o campo `NomeTitular`; e não há coluna de situação do processo. O modelo de dados (evento + série, exceção de validação) está no Bloco 3.

**MapBiomas: caminho do asset ainda não testado.** A Coleção 11 (1985–2025) deve estar no GEE sob a raiz `projects/mapbiomas-public/` — a antiga `mapbiomas-workspace/public/` saiu de uso. O dado seria uma única `ee.Image` multibanda, uma banda por ano (`classification_2025` etc.), não uma ImageCollection, e o arquivo de cobertura atual terminaria em `_coverage_v3`. Como o sufixo muda em correções sem aviso, não se crava o nome: lista-se a pasta em tempo de execução (`ee.data.listAssets`) e pega-se o asset de coverage, do mesmo modo que o ano é descoberto por `MAX`. O teste depende do projeto Google Cloud (pré-requisito 3).

**IPEADATA (PIB e população): só plano B, ticker resolvido em execução.** PIB e população ficam no SIDRA como primária. Se um dia o IPEADATA servir de reserva, os códigos (`SERCODIGO`) mudam com o ano-base e não devem ser cravados: filtra-se `ipeadatapy.list_series()` por nome e nível `Municípios` e pega-se a série de `TEMFIM` mais recente. Os usos primários confirmados do IPEADATA são o emprego (`ADMISNC`, `DESLIGNC`, municipal, 2020–2026) e a taxa de homicídio (`AVIOL12_THOMIC`, municipal, 1989–2022). O IDH-M (`ADH_IDHM`) não retornou recorte municipal; se vier a ser incluído, a fonte é o Atlas Brasil por download (opcional — não é indicador do plano).

**Sem rota automatizável:** pobreza (CadÚnico), veículos (Senatran) e CO₂ (SEEG) seguem como download ou scraping.

**Verificação de procedência (out/2026).** Os testes bateram em cada fonte; os links estão na seção Fontes. **Confirmados:** SIDRA (dados reais de Canaã), SICONFI (DCA), FRED (ferro e cobre), as sete páginas de dataset da Base dos Dados, os 12 códigos de município, o emprego municipal no IPEADATA (`ADMISNC`, `DESLIGNC`, Canaã e Parauapebas, 2020–2026), a taxa de homicídio municipal no IPEADATA (`AVIOL12_THOMIC`, 1989–2022), os três CSVs da CFEM na ANM (arrecadação, distribuição, autuação), os CSVs do AMB (só por UF, sem coluna de município) e PySUS, FAPESPA, Atlas da Violência, SEEG e World Bank. **Ainda não testados:** o asset da Coleção 11 do MapBiomas e as consultas na Base dos Dados (ambos dependem do Google Cloud); TSE e DETRAN-PA bloquearam o acesso automatizado (HTTP 403 e erro de SSL), mas são rotas alternativas. A lista completa está em Pré-requisitos e pendências. **Fora do plano:** o IDH-M (`ADH_IDHM`) não retornou dados municipais via `ipeadatapy`; se quiserem incluí-lo, a fonte é o Atlas Brasil.

**Número de eleitores.** Total por município e por gênero (guardar os dois, decidir na exibição). Rota automatizada: Base dos Dados / BigQuery, dataset Eleições Brasileiras (TSE), tabela `perfil_eleitorado_municipio_zona` — já com `id_municipio` IBGE; `table_id` técnico a confirmar no 1º uso. Alternativa: TSE dados abertos (`dadosabertos.tse.jus.br/dataset/eleitorado-2026`, código TSE, exige de-para). Atualização bianual.

**Censo Escolar.** Matrícula por etapa/gênero e infraestrutura escolar (água, energia, internet, laboratórios, acessibilidade), já agregados por município na tabela `escola` (`id_municipio` IBGE). Automatizada: Base dos Dados / BigQuery, dataset Censo Escolar (INEP), `table_id` a confirmar. Download: INEP (resultados e microdados em gov.br/inep). Cobertura: `escola`/`turma` até 2024/2025; `matricula`/`docente` até 2020 (LGPD).

**Área de mineração × cobertura florestal (indicador derivado).** Cruzamento das classes "mineração" e "floresta" do MapBiomas por município/ano — cálculo próprio sobre dados que já estão no Bloco 5, sem fonte nova. Mostra o avanço da mineração sobre a floresta; pertinente para Canaã e Parauapebas.

## Bloco 3 — Mineração e CFEM

Decisões do bloco de mineração (a versão completa, no formato dos demais blocos, está no documento Blocos Temáticos):

- **Fonte única: ANM.** CFEM arrecadada, CFEM recebida (distribuição) e autuações vêm todas da ANM, em CSVs de download direto. Arquivos nacionais, filtrados pelos municípios de interesse.
- **Arrecadada ≠ recebida ≠ autuação.** A arrecadada é o que a extração gerou no município de origem; a recebida (distribuição) é o repasse que cada município recebe; a autuação é uma cobrança da fiscalização. Nunca são somadas nem exibidas no mesmo eixo sem aviso; arrecadada e recebida aparecem como indicadores distintos.
- **CFEM: guardar mensal, exibir anual.** O arquivo vem por mês; a base guarda no detalhe mensal (campo `mes`) e o gráfico agrega para o ano.
- **Comparação configurável.** Como o arquivo é nacional, comparar com outros municípios mineradores sai de graça. A lista entra no manifesto; o padrão é ranquear por CFEM recebida (arquivo de distribuição) e pegar os N primeiros.
- **Autuações: guardar o evento, derivar a série.** Tabela própria de eventos (data de publicação, valor, processo, município, titular); dela se deriva a série do gráfico. Fonte: o CSV de autuações da ANM (ver Fontes). Ressalvas: o município vem por nome, sem código (exige de-para com o IBGE); a empresa é o campo `NomeTitular`; e não há coluna de situação do processo (pago, em recurso, cancelado).
- **Data da autuação.** O CSV traz só a data de publicação (lavratura), não o fato gerador — por isso a série usa a data de lavratura, que é também a mais honesta para o observatório.
- **Exceção de validação.** No bloco de autuações, a regra "a série não encolheu" fica desligada — autuações diminuem legitimamente em recurso. É nota técnica, não decisão de negócio.
- **Nome da empresa: guardar agora, exibir depois.** Fica registrado na tabela de eventos; a decisão de exibi-lo no site é adiada (projeto ainda não vai ao ar) e pede um olhar jurídico quando a publicação se aproximar.

**Como a CFEM é calculada.** Em essência, CFEM = base de cálculo × alíquota — a base é o faturamento da venda do minério (receita bruta menos tributos sobre a comercialização) e a alíquota varia por substância (minério de ferro na faixa de \~3,5%), conforme a Lei 13.540/2017. Os percentuais exatos devem ser conferidos na legislação; o CSV da ANM já traz o valor arrecadado pronto, então a fórmula explica o indicador, não serve para recalcular. O VPM (Valor da Produção Mineral) é a base econômica de onde a CFEM deriva — ver a nota seguinte.

**VPM (Valor da Produção Mineral) — base da CFEM, confirmado só por UF.** O AMB da ANM publica o valor da produção em `Producao_Bruta.csv` e `Producao_Beneficiada.csv` (`dadosabertos.anm.gov.br/AMB/`, separador vírgula — o metadado da ANM diz ponto e vírgula, mas o arquivo real usa vírgula —, desde 2010). O cabeçalho real tem ano, **UF**, substância, quantidades e valores, sem nenhuma coluna de município. Por isso o VPM não entra como indicador de Canaã/Parauapebas: fica como contexto estadual opcional (Pará), e a CFEM serve de proxy da produção municipal.

## Indicadores compostos

Três indicadores não são séries que uma fonte republica: são conclusões dentro de um PDF ou paper, calculadas uma vez. Decisão: **todos entram no site congelados com citação, e marcados como "promovíveis" a recalculado**. Congelar não é deixar de fora — o número aparece com a fonte e o ano; a diferença é só se ele é uma foto (atualizada à mão a cada edição) ou um cálculo vivo. No manifesto, isso vira uma marca por indicador (`estrategia: congelado`, `promovivel: sim|nao`), para a ressalva não se perder.

| Indicador | Fonte | Estratégia | Promovível? |
| --- | --- | --- | --- |
| Relações receita per capita × IDSC | IPEA, TD 3146 (2025) | Congelado | Sim — candidato real |
| Barômetro da Sustentabilidade | FAPESPA | Congelado | Não |
| Ranking de competitividade | CLP | Congelado | Não |

**Relação do IPEA (TD 3146) — a única que vale recalcular.** No fundo é uma classificação 2×2: calcula-se a receita per capita (SICONFI ÷ população) e a nota do IDSC, define-se um corte de "alto/baixo" em cada eixo e classifica-se em quatro quadrantes (AA, AB, BA, BB). A conta é simples e usa dados que o projeto já terá. O que falta confirmar no próprio TD 3146 é o corte exato usado (mediana, média ou valor fixo), para o número bater com o deles. Promover só depois que o SICONFI estiver rodando.

**Barômetro e CLP — congelados sem previsão.** O Barômetro (metodologia Prescott-Allen) cruza um índice de bem-estar humano e um de ecossistema, cada um feito de vários sub-indicadores — reprodutível, mas pesado demais para um item anual. O ranking da CLP é um índice composto com pesos proprietários; reproduzir fielmente é inviável sem a documentação completa deles. Ambos ficam tratados como dado que a entidade publica, não que o observatório calcula.

## Publicação e extras

Dois recursos decididos:

**CSV aberto.** Qualquer pessoa pode baixar os dados já tratados em CSV. Como o dado já existe nesse formato na camada tratada, o custo é quase zero, e aumenta a credibilidade do observatório — vira fonte que outros podem reusar e citar.

**Painel de status.** Uma página simples mostrando, por indicador, quando foi atualizado pela última vez e qual o ano de referência. Serve de alarme de "fonte em silêncio": o visitante e você percebem na hora se algo parou de atualizar. Casa com os metadados de proveniência que todo arquivo processado já carrega.

**Nome de empresa autuada (do Bloco 3).** O dado fica guardado desde já; a decisão de exibir no site é adiada até a publicação se aproximar, com revisão jurídica antes de expor acusação ainda não julgada.

## Pré-requisitos e pendências

Situação dos três pré-requisitos travantes:

- **Resolvido — lista de municípios (pré-req. 1).** 12 municípios com códigos, fonte FAPESPA. Os 12 códigos foram validados contra a API do IBGE.
- **Resolvido — tabelas e anos da BD (pré-req. 2).** Nomes completos e anos conferidos no catálogo, com duas incertezas a checar no dicionário.
- **Pendente — projeto Google Cloud + credencial (pré-req. 3).** Criar o projeto, ativar BigQuery, gerar a service account e guardar a chave como secret. É a única peça que não funciona sem conta; serve também ao Earth Engine.

Pendências menores, que não travam o início:

- Confirmar a coluna de município (`id_municipio`?) nas tabelas novas do **CAGED** e do **IDEB**.
- Confirmar o `table_id` técnico das tabelas de **eleitorado (TSE)** e do **Censo Escolar** na Base dos Dados.
- Testar o asset da **Coleção 11 do MapBiomas** no Earth Engine (depende do pré-requisito 3).
- Avaliar as alternativas estaduais **CODEC/SEGUP-PA** e **DETRAN-PA** (se permitem download municipal).
- Escolher o(s) demonstrativo(s) do **SICONFI** (ex.: `municipio_despesas_funcao`).
- Confirmar o corte exato do **IPEA TD 3146** antes de, eventualmente, promover a relação receita × IDSC a recalculado.
- Decidir, perto da publicação, se o site exibe os nomes das empresas autuadas.
- Aceitar ou não o campo `mes` no esquema único como a forma de acomodar a CFEM (a alternativa é manter o mês só na base da mineração).

**Ordem recomendada.** Começar pelo indicador ponta a ponta que não exige credencial — população pelo SIDRA —, passando por coleta, tratamento, validação, publicação e agendamento; em paralelo, resolver o pré-requisito 3 (Google Cloud). Depois, replicar para o resto do Bloco 1 e para os blocos de API e CSV direto (SICONFI, mineração); em seguida o BigQuery (RAIS, IDEB, eleitorado, Censo Escolar) e o Earth Engine (Bloco 5). Se um indicador atravessar o fluxo inteiro, o resto é repetição.

**Fase atual: construir.** O levantamento de fontes está concluído — há rota mapeada para quase tudo, e os pontos que restam se resolvem com um pull de teste, não com mais pesquisa. A próxima ação concreta independe do pré-requisito 3: implementar a população pelo SIDRA ponta a ponta (coleta, esquema único, validação, publicação, agendamento), porque não exige credencial e prova a arquitetura inteira. Feito isso, o resto é repetição.

## Glossário

Termos, siglas e fontes citados neste documento.

| Termo | Significado |
| --- | --- |
| AMB | Anuário Mineral Brasileiro (ANM) — fonte do valor da produção mineral (VPM). |
| ANM | Agência Nacional de Mineração — fiscaliza a CFEM e publica arrecadação, distribuição, autuações e o AMB. |
| arrecadação (CFEM) | Valor de royalty gerado pela extração no município de origem. Distinto da distribuição e da autuação. |
| autuação | Cobrança que a ANM lança quando suspeita de recolhimento a menor. É acusação com valor, não dinheiro em caixa. |
| Barômetro da Sustentabilidade | Índice de sustentabilidade (metodologia Prescott-Allen) publicado pela FAPESPA. |
| Base dos Dados (BD) | Iniciativa que espelha dados públicos no BigQuery. Nunca é fonte primária; o prefixo `br_` nas tabelas é dela. |
| BigQuery | Serviço de banco de dados do Google onde a BD hospeda as tabelas; exige credencial. |
| CadÚnico / CECAD 2.0 | Cadastro Único e seu portal (MDS), fonte de dados de pobreza. Sem API — download manual. |
| CAGED / Novo CAGED | Cadastro Geral de Empregados e Desempregados — admissões e demissões formais. |
| Censo Escolar | Levantamento anual do INEP sobre escolas, matrículas, docentes e infraestrutura escolar. |
| CFEM | Compensação Financeira pela Exploração de Recursos Minerais — o royalty da mineração. |
| CLP | Centro de Liderança Pública — publica o ranking de competitividade dos municípios. |
| CODEC/SEGUP-PA | Estatísticas de segurança pública do Pará; alternativa estadual para violência. |
| DATASUS | Órgão de dados do Ministério da Saúde; mantém o SIM e outras bases. |
| DCA | Declaração de Contas Anuais — demonstrativo do SICONFI com a despesa por função. |
| DETRAN-PA | Departamento de Trânsito do Pará; alternativa estadual para a frota. |
| distribuição (CFEM) | Parcela da CFEM repassada a cada município (CFEM recebida). |
| EECU | Earth Engine Compute Unit — unidade de processamento do GEE (cota do tier gratuito). |
| esquema único | Formato padronizado em que todo indicador tratado é gravado. |
| FAPESPA | Fundação Amazônia de Amparo a Estudos e Pesquisas — órgão estatístico do Pará; define a RI Carajás. |
| fato gerador | Ano em que o débito de CFEM se originou (contraste com lavratura). |
| FRED | Federal Reserve Economic Data — API estável de séries econômicas; fonte dos preços de commodities. |
| GEE (Google Earth Engine) | Plataforma do Google para processar dados geoespaciais; rota de automação do MapBiomas. |
| IDEB | Índice de Desenvolvimento da Educação Básica. |
| IDH-M | Índice de Desenvolvimento Humano Municipal (PNUD). |
| IDSC | Índice de Desenvolvimento Sustentável das Cidades. |
| INEP | Instituto Nacional de Estudos e Pesquisas Educacionais; produz o Censo Escolar e o IDEB. |
| IPEA | Instituto de Pesquisa Econômica Aplicada. |
| IPEADATA | Base de séries do IPEA; o ambiente Regional traz dados a nível municipal via API. |
| lavratura | Ano em que a ANM emitiu a autuação (contraste com fato gerador). |
| manifesto (`indicadores.yaml`) | Arquivo único que descreve cada indicador: fonte, método, frequência, estratégia, script. |
| MapBiomas | Projeto de mapeamento anual de uso e cobertura do solo do Brasil. |
| N6 | Parâmetro do SIDRA que recorta o resultado a nível municipal. |
| PySUS | Biblioteca Python que baixa e converte microdados do DATASUS. |
| RAIS | Relação Anual de Informações Sociais — vínculos formais, com quebras por setor, sexo e escolaridade. |
| raw / processed | Dados brutos baixados (`data/raw/`) versus tratados e versionados (`data/processed/`). |
| RI Carajás | Região de Integração Carajás — recorte do governo do Pará, com 12 municípios. |
| service account | Credencial de "robô" do Google Cloud que autentica o pipeline no BigQuery e no GEE. |
| SEEG | Sistema de Estimativas de Emissões de Gases de Efeito Estufa — fonte de CO₂. |
| Senatran | Secretaria Nacional de Trânsito — fonte da frota de veículos. |
| SICONFI | Sistema de Informações Contábeis e Fiscais do Setor Público — finanças municipais por API. |
| SIDRA | Sistema IBGE de Recuperação Automática — API de agregados do IBGE. |
| SIM | Sistema de Informações sobre Mortalidade (DATASUS) — óbitos por causa. |
| TD 3146 | Texto para Discussão 3146 do IPEA — relação receita per capita × IDSC. |
| TSE | Tribunal Superior Eleitoral — fonte do número de eleitores. |
| VAB | Valor Adicionado Bruto — componente setorial do PIB (Agropecuária, Indústria, Serviços). |
| VPM | Valor da Produção Mineral — base econômica de onde a CFEM deriva (publicado pela ANM no AMB). |

## Fontes

Links verificados em 4 out 2026 por um script que bateu em cada endpoint: ✓ respondeu e confere, ⚠ depende de credencial/pacote, falta um teste final, ou ainda não passou pelo script. Os códigos de série e agregado específicos ainda pedem um pull de teste de quem implementar.

| Fonte | Acesso | Link | Status |
| --- | --- | --- | --- |
| IBGE SIDRA (agregados) | API | [servicodados…/agregados](https://servicodados.ibge.gov.br/api/v3/agregados) | ✓ agregados 9900, 6591, 9923, 9922, 10296, 10061, 5938, 6579 |
| IBGE localidades | API | [localidades/municipios](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | ✓ 12 códigos conferidos |
| SICONFI (DCA) | API | [apidatalake…/siconfi/tt/dca](https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca) | ✓ |
| FRED (commodities) | API (key grátis) | [fred…/PIORECRUSDM](https://fred.stlouisfed.org/series/PIORECRUSDM) | ✓ ferro + `PCOPPUSDM` cobre |
| IPEADATA | pacote `ipeadatapy` | [ipeadata.gov.br](https://www.ipeadata.gov.br) | ✓ emprego municipal (`ADMISNC`, `DESLIGNC`, 2020–2026); ✓ homicídio municipal (`AVIOL12_THOMIC`); ⚠ IDH-M (`ADH_IDHM`) não veio municipal |
| Base dos Dados | BigQuery | [basedosdados.org](https://basedosdados.org) | ✓ 7 datasets (ver tabela de tabelas); ⚠ eleitorado (TSE) e Censo Escolar com `table_id` a confirmar |
| ANM — CFEM arrecadação | CSV | [CFEM\_Arrecadacao.csv](https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv) | ✓ mensal; filtrar por `CodigoMunicipio` |
| ANM — CFEM distribuição (recebida) | CSV | [CFEM\_Distribuicao.csv](https://dadosabertos.anm.gov.br/CFEM/CFEM_Distribuicao.csv) | ✓ filtrar por `CodigoEnte` |
| ANM — CFEM autuação | CSV | [CFEM\_Autuacao.csv](https://dadosabertos.anm.gov.br/CFEM/CFEM_Autuacao.csv) | ✓ separador ";"; só data de publicação; município por nome; sem situação do processo |
| ANM — AMB (VPM) | CSV | [dadosabertos.anm.gov.br/AMB](https://dadosabertos.anm.gov.br/AMB/) | ✓ testado: só por UF, sem coluna de município; separador vírgula |
| TSE — eleitorado | download | [eleitorado-2026](https://dadosabertos.tse.jus.br/dataset/eleitorado-2026) | ⚠ alternativa à BD; código TSE exige de-para |
| INEP — Censo Escolar | download | [microdados do Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) | ⚠ alternativa à BD |
| DATASUS (PySUS) | pacote | [pypi.org/project/PySUS](https://pypi.org/project/PySUS/) | ✓ |
| MapBiomas / GEE | `earthengine-api` | [brasil.mapbiomas.org/downloads](https://brasil.mapbiomas.org/downloads/) | ⚠ asset da Coleção 11 a confirmar (auth GEE) |
| SEEG | download | [plataforma.seeg.eco.br](https://plataforma.seeg.eco.br/) | ✓ sem API |
| FAPESPA | web / PDF | [estatística municipal](https://www.fapespa.pa.gov.br/estatistica-municipal/) | ✓ |
| Atlas da Violência (IPEA) | via IPEADATA | [ipea.gov.br/atlasviolencia](https://www.ipea.gov.br/atlasviolencia/) | ✓ |
| World Bank Pink Sheet | download | [Commodity Markets](https://www.worldbank.org/en/research/commodity-markets) | ✓ fallback ferro 1985–91 |
| CadÚnico / CECAD 2.0 (MDS) | download manual | — | ⚠ sem API |
| Senatran | download via dados.gov.br | [dados.gov.br](https://dados.gov.br) | ⚠ sem API paramétrica |
| IDSC (Instituto Cidades Sustentáveis) | download | [idsc.cidadessustentaveis.org.br](https://idsc.cidadessustentaveis.org.br/) | ✓ link abre; base do TD 3146; relatório/arquivo |
| CODEC/SEGUP-PA (violência) | consulta / exportação | [codec.segup.pa.gov.br](https://codec.segup.pa.gov.br/) | ⚠ alternativa estadual (a avaliar); p/ ano corrente, não a série longa |
| DETRAN-PA (frota) | painel | [dashboard-frota.detran.pa.gov.br](https://dashboard-frota.detran.pa.gov.br/) | ⚠ alternativa estadual (a avaliar); Senatran segue principal |
