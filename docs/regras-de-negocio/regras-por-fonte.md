# Regras por fonte

Regras e ressalvas específicas de uma fonte. As regras gerais de acesso, procedência e credenciais estão em [consumo-de-fontes.md](consumo-de-fontes.md). Legenda de status e siglas das fontes: [README](README.md).

Os códigos de agregado, de série e de tabela que aparecem aqui são identificadores citados nas fontes de decisão e fazem parte da regra.

### RN-FNT-01: População estimada pelo IBGE SIDRA
- **Status:** DECIDIDA
- **Regra:** A população anual deve ser obtida do IBGE SIDRA, agregado 6579 (estimativas), com a variável e a unidade fixadas, e não deve ser misturada com o Censo.
- **Motivo:** É a fonte primária por API, não exige credencial e prova a arquitetura inteira por ser o primeiro indicador ponta a ponta.
- **Exemplo:** Estimativa de 2025, variável 9324, unidade pessoas: Canaã dos Carajás 89.524 e Parauapebas 305.771; os 12 municípios retornaram valor (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: API do IBGE).
- **Exceções:** Os valores ainda precisam ser comparados com a tabela publicada pelo IBGE antes de alimentar um gráfico (VAL-15/10).
- **Fonte:** DECISÕES §Rotas de coleta por fonte, §Pré-requisitos e pendências (Ordem recomendada); BLOCOS §Bloco 1; VAL-15/10 §Matriz operacional, §Rodada adicional.
- **Relacionadas:** RN-MOD-13, RN-FNT-19

### RN-FNT-02: PIB municipal pelo SIDRA, não pelo IPEADATA
- **Status:** DECIDIDA
- **Regra:** O PIB municipal deve vir do SIDRA, agregado 5938, que traz o valor adicionado bruto por setor, e não do IPEADATA.
- **Motivo:** O IPEADATA achata a informação por setor.
- **Exemplo:** PIB municipal 2010–2023, com VAB de Agropecuária, Indústria e Serviços.
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 2.
- **Relacionadas:** RN-FNT-09, RN-TMP-16

### RN-FNT-03: Censo 2022 pelos agregados do SIDRA
- **Status:** DECIDIDA
- **Regra:** O Censo 2022 deve ser obtido do SIDRA pelos agregados definidos: favelas 9900, entorno 6591, situação do domicílio 9923, saneamento 9922, rendimento 10296 e instrução 10061; "Infraestrutura" não tem agregado próprio e usa 6591 e 9922.
- **Motivo:** A Base dos Dados ainda não publicou o Censo 2022 nesse nível de detalhe.
- **Exemplo:** População residente em favelas vem do agregado 9900.
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 4.
- **Relacionadas:** RN-TMP-08

### RN-FNT-04: Despesa por função pelo SICONFI (DCA)
- **Status:** DECIDIDA
- **Regra:** A despesa por função deve vir da DCA do SICONFI, Anexo I-E (`DCA-Anexo I-E`), filtrada pelo `id_ente` (código IBGE de 7 dígitos) e pelo exercício, com as funções no campo `conta`.
- **Motivo:** É a fonte primária por API para as finanças municipais de 2013 em diante.
- **Exemplo:** O exercício 2025 retornou 337 linhas na primeira página, que é o tamanho da primeira página do teste e não a quantidade final (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Exceções:** Em aberto: o(s) demonstrativo(s) a usar, as contas e o estágio da despesa, a paginação completa e o tratamento de retificações (RN-TMP-04).
- **Fonte:** DECISÕES §Rotas de coleta por fonte, §Pré-requisitos e pendências; BLOCOS §Bloco 6; LAB-19/10 §4 (SICONFI); VAL-15/10 §Matriz operacional.
- **Relacionadas:** RN-TMP-04, RN-TMP-15, RN-IND-02

### RN-FNT-05: Preços de commodities pelo FRED
- **Status:** DECIDIDA
- **Regra:** Os preços de minério de ferro (`PIORECRUSDM`) e de cobre (`PCOPPUSDM`) devem vir da API do FRED, como séries globais mensais; o ferro tem início em janeiro de 1980 e o período do cobre vigente é 2000–2026.
- **Motivo:** O FRED espelha a série do IMF por API estável, que é o padrão para pipelines.
- **Exemplo:** Em 19/10/2026, as duas séries foram consultadas de jan/1980 a jul/2026 (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Exceções:** A unidade do ferro e o recorte de exibição do ferro estão em aberto (RN-TMP-14, RN-TMP-13).
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (conflito 8); LAB-19/10 §4 (FRED e World Bank Pink Sheet); DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 2.
- **Relacionadas:** RN-FON-10, RN-MOD-19, RN-TMP-13

### RN-FNT-06: Pink Sheet só para anos anteriores a 1980
- **Status:** DECIDIDA
- **Regra:** O Pink Sheet do World Bank só deve ser usado, baixado uma vez e congelado com citação, se for necessário cobrir anos anteriores a 1980.
- **Motivo:** Como o ferro no FRED começa em 1980, o trecho de 1985–1991 previsto por DECISÕES e por BLOCOS deixou de ser necessário.
- **Exemplo:** A planilha anual do Pink Sheet tem 2023–2025 e coincide numericamente com o PDF de outubro de 2026.
- **Exceções:** O rótulo da unidade do ferro diverge entre a planilha e o PDF (RN-TMP-14).
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (conflito 8); LAB-19/10 §4; VAL-15/10 §Matriz operacional (Commodities).
- **Relacionadas:** RN-TMP-13, RN-TMP-14

### RN-FNT-07: Saldo de emprego é derivado
- **Status:** DECIDIDA
- **Regra:** O saldo de emprego formal deve ser derivado como admissões menos desligamentos, e admissões e desligamentos também devem ser indicadores próprios.
- **Motivo:** Não há série municipal pronta de saldo, e derivar rende dois indicadores adicionais.
- **Exemplo:** `ADMISNC` (admissões) − `DESLIGNC` (demissões) do Novo CAGED.
- **Exceções:** A rota de obtenção está em conflito (RN-FNT-20).
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Emprego formal); BLOCOS §Bloco 2.
- **Relacionadas:** RN-FNT-20, RN-MOD-16

### RN-FNT-08: Taxa de homicídio
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve confirmar na fonte se `AVIOL12_THOMIC` corresponde à medida pedida pela oficina, "taxa de homicídio por arma de fogo a cada 100 mil habitantes, 1989–2022", e decidir a fonte e o conceito do indicador.
- **Motivo:** Os documentos divergem na fonte, e BLOCOS chama o indicador apenas de "taxa de homicídio", sem "arma de fogo", sem justificar a mudança.
- **Exemplo:** DECISÕES indica `AVIOL12_THOMIC` municipal de 1989 a 2022 (IPEADATA e Atlas da Violência).
- **Fonte:** Versão A: DECISÕES §Rotas de coleta por fonte, §Estratégia de fontes e acesso; BLOCOS §Bloco 4 (IPEADATA/Atlas, 04/10/2026, última edição 20/10/2026). Versão B: CONSUMO §Sociedade (CODEC/SEGUP principal e SIM alternativa, 02/10/2026). Versão C: PLANO §Bloco 4 (SIM via Base dos Dados, 30/09/2026). A conferência na fonte foi pedida pelo mantenedor em 24/10/2026 (DECISÃO-MANTENEDOR, resposta à pergunta 8).
- **Relacionadas:** RN-FNT-15, RN-TMP-09, RN-FON-20

### RN-FNT-09: IPEADATA para PIB e população só como plano B
- **Status:** DECIDIDA
- **Regra:** Se o IPEADATA vier a servir de reserva para PIB e população, o código da série (`SERCODIGO`) não deve ser fixado, e a série deve ser resolvida em execução por nome, nível municipal e fim mais recente.
- **Motivo:** Os códigos mudam com o ano-base.
- **Exemplo:** O IPEADATA não é a rota primária de PIB e população; é só reserva.
- **Fonte:** DECISÕES §Rotas de coleta por fonte.
- **Relacionadas:** RN-FNT-02, RN-TMP-01

### RN-FNT-10: IDH-M fora do plano
- **Status:** DECIDIDA
- **Regra:** O IDH-M não deve ser tratado como indicador do plano; se for incluído, a fonte é o Atlas Brasil, por download.
- **Motivo:** O IDH-M é decenal (parado em 2010) e a série `ADH_IDHM` do IPEADATA não retornou recorte municipal.
- **Exemplo:** O IDH-M não aparece nas tabelas dos blocos de BLOCOS.
- **Fonte:** DECISÕES §Rotas de coleta por fonte, §Verificação de procedência.
- **Relacionadas:** RN-FNT-09

### RN-FNT-11: Tabelas da Base dos Dados usadas pelo projeto
- **Status:** DECIDIDA
- **Regra:** O projeto deve usar as tabelas da Base dos Dados já conferidas: `br_ibge_populacao.municipio`, `br_ibge_pib.municipio`, `br_me_caged.microdados_movimentacoes`, `br_me_rais.microdados_vinculos`, `br_inep_ideb.municipio`, `br_ms_sim.municipio_causa` e `br_me_siconfi` (com demonstrativo escolhido), e a tabela `microdados_antigos` do CAGED, que vai só até cerca de 2019, não deve ser usada para dados atuais.
- **Motivo:** Os nomes completos e os anos mais recentes foram conferidos no catálogo em out/2026.
- **Exemplo:** RAIS (vínculos), ano mais recente 2025; Novo CAGED, 2026-08 (conforme DECISÕES).
- **Exceções:** A via Base dos Dados para RAIS, IDEB e eleitorado está em disputa (RN-FNT-21). Em aberto: a coluna de município nas tabelas do CAGED e do IDEB, e o `table_id` técnico do eleitorado (TSE) e do Censo Escolar (tabela `escola`).
- **Fonte:** DECISÕES §Tabelas da Base dos Dados confirmadas, §Pré-requisitos e pendências; BLOCOS §Bloco 4.
- **Relacionadas:** RN-FON-03, RN-FON-19, RN-TMP-03

### RN-FNT-12: Frota de veículos
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir a fonte da frota de veículos, entre Senatran e DETRAN-PA.
- **Motivo:** As fontes divergem, e o painel do DETRAN-PA não tem exportação municipal confirmada.
- **Exemplo:** Em 17/10/2026, após reparo da cadeia de certificados, o painel do DETRAN-PA devolveu HTTP 502 (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** Versão A: DECISÕES §Rotas de coleta por fonte e BLOCOS §Bloco 4 (Senatran via dados.gov.br, com DETRAN-PA como alternativa a avaliar; PLANO §Bloco 4 também; 04/10/2026, última edição 20/10/2026). Versão B: MAPA-TEMAS §Sociedade; CONSUMO §Sociedade, serviços e segurança (DETRAN-PA, 02/10/2026).
- **Relacionadas:** RN-TMP-02, RN-FON-20

### RN-FNT-13: Uso do solo pelo MapBiomas
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir se o uso do solo do MapBiomas é obtido pelo Google Earth Engine ou por download das estatísticas municipais da Coleção 11, e testar o asset antes de assumir a rota.
- **Motivo:** As fontes divergem, e o asset ainda não foi testado porque depende do projeto Google Cloud.
- **Exemplo:** O Earth Engine ficou PENDENTE em 17/10/2026 por falta de `GEE_PROJECT` (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** Versão A: DECISÕES §Rotas de coleta por fonte e BLOCOS §Bloco 5 (Google Earth Engine, com download como alternativa; 04/10/2026, última edição 20/10/2026). Versão B: MAPA-TEMAS §Meio ambiente e CONSUMO §Meio ambiente (download das estatísticas da Coleção 11; 02/10/2026). PLANO §Bloco 5 (30/09/2026) também aponta download.
- **Relacionadas:** RN-TMP-05, RN-TMP-07, RN-PRI-09, RN-FON-20

### RN-FNT-14: Emissões do SEEG por download
- **Status:** DECIDIDA
- **Regra:** As emissões de CO₂ do SEEG devem ser obtidas por download de planilha por edição, porque a fonte não tem API confirmada.
- **Motivo:** Não há rota automatizável.
- **Exemplo:** Série municipal do SEEG, com gás, setor e edição.
- **Exceções:** Se a planilha baixada pode ser guardada no repositório, e com que licença, está **EM ABERTO** (conflito 16).
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 5; DECISÃO-MANTENEDOR de 24/10/2026 (conflito 16 em aberto).
- **Relacionadas:** RN-FON-15, RN-PRI-06, RN-TMP-11

### RN-FNT-15: Não calcular homicídio a partir do SIM cru
- **Status:** DECIDIDA
- **Regra:** A taxa de homicídio não deve ser calculada a partir dos microdados crus do SIM, e os demais indicadores de saúde devem vir dos microdados do DATASUS (SIM, SINASC, SIH, SIA e CNES), agregados por município.
- **Motivo:** Muitas mortes entram como "causa indeterminada"; o Atlas da Violência redistribui essas mortes e publica a taxa corrigida.
- **Exemplo:** O SIM serve a indicadores de saúde, mas a taxa de homicídio usa a série corrigida do Atlas.
- **Exceções:** A fonte e o conceito da taxa de homicídio estão em aberto (RN-FNT-08).
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Homicídios); BLOCOS §Bloco 4.
- **Relacionadas:** RN-FNT-08, RN-TMP-10, RN-TER-12

### RN-FNT-16: CadÚnico sem rota automatizada
- **Status:** DECIDIDA
- **Regra:** Os dados de pobreza do CadÚnico (CECAD 2.0) devem ser obtidos por download manual, e o observatório não deve tentar automatizar a obtenção.
- **Motivo:** Não há API.
- **Exemplo:** Pobreza e percentual de famílias pobres, com data-base e definição registradas.
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 4.
- **Relacionadas:** RN-PRI-08

### RN-FNT-17: FAPESPA, IDSC e CLP
- **Status:** PROPOSTA
- **Regra:** Dados da FAPESPA obtidos por PDF não devem ser a única via de um indicador que possa ser recalculado das fontes federais, e IDSC e ranking da CLP devem ser tomados como arquivo da edição publicada, com cobertura dos municípios confirmada.
- **Motivo:** Depender de PDF estadual é o elo mais frágil da cadeia.
- **Exemplo:** O Barômetro da FAPESPA e o ranking da CLP entram congelados (RN-IND-04).
- **Fonte:** PLANO §Riscos e cuidados, §Bloco 6; CONSUMO §Finanças públicas e índices.
- **Relacionadas:** RN-IND-04, RN-FON-06, RN-PRI-05

### RN-FNT-18: Ler cada arquivo da ANM conforme seu formato real
- **Status:** DECIDIDA
- **Regra:** Cada arquivo da ANM deve ser lido conforme o formato real: a autuação com separador `;` e município por nome, a arrecadação com `CodigoMunicipio`, a distribuição com `CodigoEnte` e o AMB com separador vírgula.
- **Motivo:** O metadado da ANM nem sempre corresponde ao arquivo real.
- **Exemplo:** O metadado do AMB diz ponto e vírgula, mas o arquivo usa vírgula.
- **Fonte:** DECISÕES §Rotas de coleta por fonte, §Autuações da CFEM, §Bloco 3; BLOCOS §Bloco 3; LAB-19/10 §4 (ANM CFEM; ANM AMB).
- **Relacionadas:** RN-FON-18, RN-CFE-22

### RN-FNT-19: Conferir que a resposta identifica o município pedido
- **Status:** PROPOSTA
- **Regra:** Em consultas ao SIDRA, o código e o nome do município devolvidos devem ser conferidos contra o município pedido antes de aceitar o valor.
- **Motivo:** Garante que o valor pertence ao município esperado.
- **Exemplo:** Um pedido em lote de dois municípios retornou HTTP 500, e o script consulta cada município separadamente e confere código e nome (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** SCRIPTS (`probe_ibge_sidra`); VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-FNT-01, RN-TER-05

### RN-FNT-20: Rota do emprego formal
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir a rota do emprego formal entre IPEADATA, microdados do MTE e Base dos Dados, e como obter o IPEADATA sem baixar a série inteira.
- **Motivo:** As fontes divergem, e o filtro do IPEADATA não limitou a resposta.
- **Exemplo:** Uma consulta com filtro de município e limite de uma linha anunciou 63.685.034 bytes e começou por outro município (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** Versão A: DECISÕES §Estratégia de fontes e acesso e BLOCOS §Bloco 2 (IPEADATA primário, séries "confirmadas por município, 2020–2026"; 04/10/2026, última edição 20/10/2026). Versão B: MAPA-TEMAS §Economia e CONSUMO §Economia (microdados MTE/PDET; 02/10/2026). Versão C: PLANO §Bloco 2 (Novo CAGED via Base dos Dados; 30/09/2026). Evidência: VAL-15/10 §Matriz operacional, §Rodada adicional (15/10/2026); LAB-19/10 §4 (só `ADMISNC` testado; 19/10/2026).
- **Relacionadas:** RN-FNT-07, RN-FON-20

### RN-FNT-21: Base dos Dados ou arquivo oficial para RAIS, IDEB, TSE e Censo Escolar
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir, para RAIS, IDEB, eleitorado (TSE) e Censo Escolar, se a via é a Base dos Dados ou o arquivo oficial do órgão.
- **Motivo:** DECISÕES e BLOCOS indicam a Base dos Dados; CONSUMO e MAPA-TEMAS indicam arquivos oficiais com leitura por edição; e a Base dos Dados nunca é fonte primária.
- **Exemplo:** O IDEB aparece como `br_inep_ideb.municipio` em DECISÕES e como arquivo do INEP por edição em CONSUMO.
- **Fonte:** Versão A: DECISÕES §Estratégia de fontes e acesso e BLOCOS §Bloco 4 (04/10/2026, última edição 20/10/2026). Versão B: CONSUMO §Sociedade, §Economia e MAPA-TEMAS §Sociedade (02/10/2026).
- **Relacionadas:** RN-FON-03, RN-FON-20
