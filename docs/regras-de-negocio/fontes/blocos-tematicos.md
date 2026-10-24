# Observatório RI Carajás — Blocos Temáticos

Oct 4, 2026 · @Daniel Rond

> Exportado do Claude Docs em 24/10/2026 (revisão 29). Conteúdo mantido como no original.

Os seis blocos temáticos do observatório: indicadores, fonte e método de coleta de cada um. A arquitetura, a justificativa das escolhas, o status de verificação dos links e as pendências estão no Registro de Decisões.

## Bloco 1 — Dinâmica Populacional

Inteiramente automatizável pela API de agregados do IBGE, e o melhor ponto de partida para o primeiro pipeline: não depende de credencial nem de download. Endpoint `servicodados.ibge.gov.br/api/v3/agregados`, com a localidade `N6[código do município]`.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Evolução da população: Canaã e Parauapebas vs. RI Carajás | IBGE SIDRA (Censo 2022) | Base dos Dados (`br_ibge_populacao.municipio`) | API |
| Série populacional 1980–2022 | IBGE SIDRA (censos + estimativas) | Base dos Dados | API |
| Características da população 2022 (idade, sexo, raça) | IBGE SIDRA (Censo 2022) | Microdados do Censo | API |
| Número de eleitores (total e por gênero) | TSE via Base dos Dados (Eleições Brasileiras) | TSE dados abertos (download) | BigQuery |

**Série longa precisa de nota de rodapé.** Censos anteriores a 2000 vêm de tabelas SIDRA distintas, e Canaã dos Carajás só foi criada em 1994 — antes disso o território pertencia a Parauapebas e Marabá. A série "desde 1980" tem de explicar isso.

**Primeiro pipeline.** A população pelo SIDRA é o indicador escolhido para testar o fluxo completo (coleta, esquema único, validação, publicação e agendamento), por não exigir credencial.

**Número de eleitores.** Total e por gênero — guardar os dois, decidir na exibição. Vem da tabela de perfil do eleitorado por município na Base dos Dados, já com código IBGE (`table_id` a confirmar). Alternativa: download do TSE, que usa código próprio e exige de-para. Atualização bianual.

## Bloco 2 — Economia e Mercado de Trabalho

Três naturezas: PIB e renda pela API do IBGE, emprego formal pela série do IPEADATA (com a Base dos Dados como alternativa), e preços de commodities pela API do FRED.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| PIB municipal 2010–2023 | IBGE SIDRA (agregado 5938, VAB por setor) | Base dos Dados (`br_ibge_pib.municipio`) | API |
| % PIB RI-Carajás per capita | Calculado: PIB ÷ população | — | Derivado |
| Preço do minério de ferro USD 1992–2025 | FRED (`PIORECRUSDM`) | World Bank Pink Sheet (1985–91) | API |
| Preço do cobre USD 2000–2026 | FRED (`PCOPPUSDM`) | IMF; World Bank | API |
| Evolução do emprego formal | IPEADATA Regional (`ADMISNC` − `DESLIGNC`) | Novo CAGED via Base dos Dados | API |

**Commodities.** Séries globais (sem recorte municipal) pela API do FRED. Os anos 1985–1991 do minério de ferro vêm do Pink Sheet do World Bank, baixados uma vez.

**Emprego.** Saldo = admissões (`ADMISNC`) − demissões (`DESLIGNC`), do IPEADATA; as duas séries estão confirmadas por município (Canaã e Parauapebas, 2020–2026). Alternativa: Novo CAGED na Base dos Dados. O painel BI do MTE serve só para conferência manual.

**As quebras finas de trabalho estão no Bloco 4.** Emprego por setor, remuneração e escolaridade vêm da RAIS (via BigQuery), não do CAGED — e aparecem no bloco de Sociedade.

## Bloco 3 — Mineração e CFEM

A CFEM (royalty da mineração) é uma das maiores receitas de Canaã e Parauapebas. Os dados vêm da ANM em CSVs de download direto, nacionais, filtrados por município. CFEM arrecadada, CFEM recebida e autuação são indicadores distintos e nunca são somados.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| CFEM arrecadada por município (série) | ANM, CSV de arrecadação | — | Download (CSV) |
| CFEM recebida por município (distribuição) | ANM, CSV de distribuição | — | Download (CSV) |
| CFEM per capita | Calculado: CFEM ÷ população | — | Derivado |
| Comparação com outros municípios mineradores | ANM (mesmo arquivo nacional) | — | Derivado |
| Autuações da CFEM (valor, processo e titular) | ANM, CSV de autuação | — | Download (CSV) |
| VPM — valor da produção mineral | ANM, AMB (produção bruta/beneficiada) | CFEM como proxy | Download (só por UF — contexto estadual) |

**CFEM.** O CSV vem por mês: guardar mensal, exibir anual. Arrecadada = gerada no município de origem (filtro `CodigoMunicipio`); recebida = repasse ao município (arquivo de distribuição, filtro `CodigoEnte`). A comparação com outros municípios mineradores é configurável no manifesto — padrão: os N maiores em CFEM recebida.

**Cálculo.** CFEM = base de cálculo (faturamento da venda, menos os tributos sobre a comercialização) × alíquota por substância (Lei 13.540/2017; minério de ferro na faixa de 3,5% — conferir na lei). O CSV já traz o valor arrecadado pronto.

**VPM.** Valor da produção mineral, base da CFEM, publicado pela ANM no AMB (`dadosabertos.anm.gov.br/AMB/`, arquivos de produção bruta e beneficiada, separador vírgula). Confirmado só por UF: o arquivo não tem coluna de município. Por isso não entra como indicador de Canaã e Parauapebas — fica como contexto estadual opcional, e a CFEM serve de proxy da produção municipal.

**Autuações.** Cada autuação é guardada como evento, e a série deriva dela. O CSV traz processo, data de publicação (lavratura), titular (`NomeTitular`), município (por nome — exige de-para com o IBGE), substância e valor; não traz a situação do processo nem o fato gerador. A validação "série não encolheu" fica desligada (autuações caem em recurso), e o nome da empresa é guardado com exibição adiada.

## Bloco 4 — Sociedade

O bloco mais heterogêneo: Censo 2022 pelo SIDRA; emprego detalhado pela RAIS e educação pelo Censo Escolar, ambos via Base dos Dados; saúde pelo PySUS; e homicídio pelo IPEADATA.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Emprego formal como % da população | Calculado: RAIS ÷ população | — | Derivado |
| % de emprego por setor | RAIS (CNAE) via Base dos Dados | — | BigQuery |
| Remuneração média total e por sexo | RAIS via Base dos Dados | FAPESPA | BigQuery |
| Vínculos por escolaridade | RAIS via Base dos Dados | FAPESPA | BigQuery |
| Canaã — emprego por gênero 2022 | RAIS via Base dos Dados | — | BigQuery |
| Rendimento domiciliar per capita | IBGE SIDRA (agregado 10296) | — | API |
| Nível de instrução por sexo | IBGE SIDRA (agregado 10061) | — | API |
| Notas do IDEB | Base dos Dados (`br_inep_ideb.municipio`) | Portal do INEP | BigQuery |
| Matrícula por etapa e por gênero | Censo Escolar (INEP) via Base dos Dados, tabela `escola` | INEP (download) | BigQuery |
| Infraestrutura escolar (água, energia, internet, acessibilidade) | Censo Escolar (INEP) via Base dos Dados, tabela `escola` | INEP (download) | BigQuery |
| Distorção idade-série | INEP, painel de indicadores | FAPESPA | Download |
| Indicadores de saúde | DATASUS via PySUS | FAPESPA | API (PySUS) |
| Pobreza / famílias pobres (%) | Observatório do CadÚnico / CECAD 2.0 | Portal MDS | Download |
| Taxa de homicídio | IPEADATA / Atlas da Violência (`AVIOL12_THOMIC`) | SIM/DATASUS via Base dos Dados | API |
| Violência 2023 | Atlas da Violência (IPEA) | CODEC/SEGUP-PA (estadual, a avaliar); FAPESPA; SIM | API |
| Número de veículos | Senatran via dados.gov.br | DETRAN-PA (estadual, a avaliar); FAPESPA | Download |
| Infraestrutura 2022 | IBGE SIDRA (6591 / 9922) | — | API |
| População residente em favelas | IBGE SIDRA (agregado 9900) | — | API |
| Características do entorno | IBGE SIDRA (agregado 6591) | — | API |
| População por situação do domicílio | IBGE SIDRA (agregado 9923) | — | API |

**Agregados do Censo 2022:** favelas 9900, entorno 6591, situação do domicílio 9923, saneamento 9922, rendimento 10296, instrução 10061. "Infraestrutura" não tem agregado próprio — usa 6591/9922.

**Homicídios.** Taxa corrigida do Atlas da Violência (`AVIOL12_THOMIC`, municipal, 1989–2022), em vez de calcular a partir do SIM — o motivo está no Registro de Decisões.

**Outras notas.** A distorção idade-série vem do painel do INEP (não existe pronta na Base dos Dados). Falta confirmar a coluna de município nas tabelas do CAGED e do IDEB na Base dos Dados.

**Censo Escolar.** Foco em matrícula por etapa e por gênero e, principalmente, em infraestrutura escolar (água, energia, esgoto, internet, laboratórios, acessibilidade), já agregadas por município na tabela `escola` da Base dos Dados (`table_id` a confirmar). Alternativa: download do INEP. Recortes por aluno ou professor (`matricula`, `docente`) só vão até 2020.

## Bloco 5 — Meio Ambiente e Saneamento

Quase tudo vem do MapBiomas, pela via do Google Earth Engine (a mesma credencial do BigQuery), que elimina o download manual anual. O saneamento sai do Censo 2022 (SIDRA).

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Uso do solo — área urbana (%) 1985–2025 | MapBiomas (GEE) | estatísticas por município (download) | API (GEE) |
| Cobertura florestal | MapBiomas (GEE) | INPE/PRODES | API (GEE) |
| Uso da terra = % de floresta (RI e Canaã) | MapBiomas (GEE) | PRODES/TerraBrasilis | API (GEE) |
| Dinâmica de uso do solo de Canaã (transição) | MapBiomas (GEE) | — | API (GEE) |
| Área de mineração × cobertura florestal | Calculado sobre o MapBiomas (GEE) | — | Derivado |
| Emissão de CO₂ | SEEG (XLSX/CSV) | SIRENE (MCTI) | Download |
| Saneamento 2022 | IBGE SIDRA (agregado 9922) | SNIS | API |

**MapBiomas pelo GEE.** Coleção 11 (1985–2025), sem API tabular; o asset é localizado em execução, sem cravar o nome. Ainda não testado — depende do projeto Google Cloud. A cota gratuita do GEE cobre os dois municípios.

**Transição de uso do solo.** O arquivo é enorme: filtrar por município antes de qualquer tabulação.

**Mineração × floresta.** Cruzamento das classes de mineração e de floresta do MapBiomas, por município e ano — cálculo próprio, sem fonte nova.

**CO₂.** O SEEG não tem API: download de planilha, guardada no repositório.

## Bloco 6 — Finanças Públicas

Todas as despesas e receitas vêm da API do SICONFI — um dos blocos mais fáceis de automatizar, apesar de ser o mais numeroso. Os indicadores compostos do fim são a exceção: são índices publicados em PDF ou paper, congelados com citação.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Despesa per capita por função (Educação, Saúde, Saneamento, Segurança, Agricultura, Urbanismo) 2013–2025 | SICONFI (DCA, Anexo I-E) ÷ população | Base dos Dados (`br_me_siconfi`) | API |
| Despesa per capita por função (consolidado) | SICONFI | — | API |
| Repasse e participação do ICMS | SICONFI | SEFA-PA | API/Download |
| Impostos como % do PIB | Calculado: SICONFI ÷ PIB IBGE | — | Derivado |
| Impostos como % da receita corrente | SICONFI | — | API |
| Composição das receitas correntes de Canaã (%) | SICONFI | — | API |
| Barômetro da Sustentabilidade | FAPESPA | — | Congelado (PDF) |
| Ranking de competitividade (Canaã) | CLP | — | Congelado (PDF) |
| Receita per capita × IDSC (relações AA/AB/BA/BB) | IPEA, TD 3146 | Recalcular com SICONFI + IDSC | Congelado, promovível |

**SICONFI por API.** Endpoint `apidatalake.tesouro.gov.br/ords/siconfi/tt/dca`; filtros `id_ente` (código IBGE de 7 dígitos), `an_exercicio` e `no_anexo=DCA-Anexo I-E` para a despesa por função. As funções vêm no campo `conta`; o último ano fechado é 2025.

**Finanças históricas (pré-2013).** Se precisar da série longa, o IPEADATA tem o FINBRA organizado (`FINBRA_DESP`, `FINBRA_REC`); para 2013 em diante, ficar no SICONFI.

**Compostos.** Entram congelados, com citação da fonte e do ano. Só a relação do IPEA (TD 3146) é candidata a recalcular, depois que o SICONFI estiver rodando.

## Glossário

Siglas, fontes e termos citados nos blocos.

| Termo | Significado |
| --- | --- |
| agregado (SIDRA) | Tabela temática do SIDRA, identificada por número (ex.: 9900 = favelas). |
| AMB | Anuário Mineral Brasileiro (ANM) — fonte do valor da produção mineral (VPM). |
| ANM | Agência Nacional de Mineração. |
| arrecadação (CFEM) | Royalty gerado pela extração no município de origem (distinto da distribuição e da autuação). |
| Atlas da Violência | Estudo do IPEA que publica a taxa de homicídio corrigida. |
| autuação | Cobrança que a ANM lança por recolhimento a menor de CFEM. |
| `AVIOL12_THOMIC` | Código da série de taxa de homicídio no IPEADATA. |
| Barômetro da Sustentabilidade | Índice de sustentabilidade da FAPESPA (metodologia Prescott-Allen). |
| Base dos Dados (BD) | Iniciativa que espelha dados públicos no BigQuery; prefixo `br_`. Nunca é fonte primária. |
| BigQuery | Banco de dados do Google onde a BD hospeda as tabelas; exige credencial. |
| CadÚnico / CECAD 2.0 | Cadastro Único e seu portal (MDS); fonte de pobreza, sem API. |
| CAGED / Novo CAGED | Cadastro Geral de Empregados e Desempregados — admissões e demissões. |
| Censo Escolar | Levantamento anual do INEP sobre escolas, matrículas, docentes e infraestrutura escolar. |
| CFEM | Compensação Financeira pela Exploração de Recursos Minerais — o royalty da mineração. |
| CLP | Centro de Liderança Pública; publica o ranking de competitividade. |
| CNAE | Classificação Nacional de Atividades Econômicas — usada no emprego por setor. |
| CODEC/SEGUP-PA | Estatísticas de segurança pública do Pará; alternativa estadual para violência. |
| Coleção 11 | Versão mais recente do MapBiomas (uso do solo, 1985–2025). |
| DATASUS | Órgão de dados do Ministério da Saúde; mantém o SIM. |
| DCA / Anexo I-E | Declaração de Contas Anuais do SICONFI; o Anexo I-E traz a despesa por função. |
| DETRAN-PA | Departamento de Trânsito do Pará; alternativa estadual para a frota. |
| distribuição (CFEM) | Parcela da CFEM repassada a cada município (CFEM recebida), distinta da arrecadada na origem. |
| EECU | Earth Engine Compute Unit — cota de processamento do GEE. |
| FAPESPA | Órgão estatístico do Pará; define a RI Carajás. |
| fato gerador | Ano em que o débito de CFEM se originou (contraste com lavratura). |
| FINBRA | Base histórica de finanças municipais do Tesouro, organizada no IPEADATA. |
| FRED | Federal Reserve Economic Data — API das séries de commodities. |
| GEE (Google Earth Engine) | Plataforma do Google para dados geoespaciais; rota do MapBiomas. |
| id\_ente | Parâmetro do SICONFI que recebe o código IBGE do município. |
| IDEB | Índice de Desenvolvimento da Educação Básica. |
| IDSC | Índice de Desenvolvimento Sustentável das Cidades. |
| INEP | Instituto Nacional de Estudos e Pesquisas Educacionais; produz o Censo Escolar e o IDEB. |
| IPEA | Instituto de Pesquisa Econômica Aplicada. |
| IPEADATA | Base de séries do IPEA; o ambiente Regional traz dados a nível municipal. |
| lavratura | Ano em que a ANM emitiu a autuação (contraste com fato gerador). |
| MapBiomas | Mapeamento anual de uso e cobertura do solo do Brasil. |
| N6 | Parâmetro do SIDRA que recorta o resultado a nível municipal. |
| Pink Sheet | Planilha mensal de preços de commodities do World Bank (só download). |
| PySUS | Biblioteca Python que baixa e converte microdados do DATASUS. |
| RAIS | Relação Anual de Informações Sociais — vínculos formais (setor, sexo, escolaridade). |
| RI Carajás | Região de Integração Carajás — 12 municípios do Pará. |
| SEEG | Sistema de Estimativas de Emissões de Gases de Efeito Estufa — fonte de CO₂. |
| Senatran | Secretaria Nacional de Trânsito — frota de veículos. |
| SICONFI | Sistema de Informações Contábeis e Fiscais do Setor Público. |
| SIDRA | Sistema IBGE de Recuperação Automática — API de agregados do IBGE. |
| SIM | Sistema de Informações sobre Mortalidade (DATASUS). |
| SNIS | Sistema Nacional de Informações sobre Saneamento. |
| TD 3146 | Texto para Discussão 3146 do IPEA — relação receita per capita × IDSC. |
| TSE | Tribunal Superior Eleitoral — fonte do número de eleitores. |
| VAB | Valor Adicionado Bruto — componente setorial do PIB. |
| VPM | Valor da Produção Mineral — base econômica de onde a CFEM deriva (publicado pela ANM no AMB). |
