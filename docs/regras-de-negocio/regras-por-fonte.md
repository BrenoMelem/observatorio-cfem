# Regras por fonte

Regras e ressalvas específicas de uma fonte. As regras gerais de acesso, procedência e credenciais estão em [consumo-de-fontes.md](consumo-de-fontes.md). Legenda de status e siglas das fontes: [README](README.md).

Os códigos de agregado, de série e de tabela que aparecem aqui são identificadores citados nas fontes de decisão e fazem parte da regra.

### RN-FNT-01: População estimada pelo IBGE SIDRA
- **Status:** DECIDIDA
- **Regra:** A população anual deve ser obtida do IBGE SIDRA, agregado 6579 (estimativas), com a variável e a unidade fixadas, e não deve ser misturada com o Censo.
- **Motivo:** É a fonte primária por API, não exige credencial e prova a arquitetura inteira por ser o primeiro indicador ponta a ponta.
- **Exemplo:** Estimativa de 2025, variável 9324, unidade pessoas: Canaã dos Carajás 89.524 e Parauapebas 305.771; os 12 municípios retornaram valor (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: API do IBGE).
- **Exceções:** Cada nova edição deve ser comparada com tabela publicada pelo IBGE antes de alimentar um gráfico. Para 2025 e 2026, os 12 municípios foram reconciliados sem divergência em 30/10/2026, conforme referências em `data/referencia-populacao-2025.json` e `data/referencia-populacao-2026.json`.
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
- **Evidência datada:** no fim deste arquivo, em [Notas de evidência](#notas-de-evidência), sob RN-FNT-04.
- **Exceções:** O estágio da despesa está decidido: empenhada, liquidada e paga são publicadas como três indicadores separados (DECISÃO-MANTENEDOR de 30/10/2026). A paginação foi conferida na evidência acima. Em aberto: o(s) demonstrativo(s) a usar, as contas, se o escopo fica em função e subfunção (o mantenedor considerou esse nível adequado em 30/10/2026, mas não registrou como decisão) e o tratamento de retificações (RN-TMP-04).
- **Fonte:** DECISÕES §Rotas de coleta por fonte, §Pré-requisitos e pendências; BLOCOS §Bloco 6; LAB-19/10 §4 (SICONFI); VAL-15/10 §Matriz operacional.
- **Relacionadas:** RN-TMP-04, RN-TMP-15, RN-IND-02

### RN-FNT-05: Preços de commodities pelo Pink Sheet do World Bank
- **Status:** DECIDIDA
- **Regra:** Os preços de minério de ferro e de cobre devem vir do Pink Sheet do World Bank, como séries globais mensais (planilha `CMO-Historical-Data-Monthly`, colunas `Iron ore, cfr spot` e `Copper`). A coleta é mensal, localiza o endereço do arquivo na página do World Bank (o endereço traz um código que muda a cada edição) e guarda cada edição datada, com o endereço de origem e a identificação do arquivo. Se a coluna ou o endereço não forem achados, a coleta deve falhar com aviso e manter a edição anterior. O FRED (`PIORECRUSDM` e `PCOPPUSDM`) fica só como reserva: é usado apenas se o Pink Sheet não estiver disponível, com a fonte registrada em cada observação, e nunca emendado com o Pink Sheet numa mesma série.
- **Motivo:** O ferro do FRED só coincide com o Pink Sheet a partir de dez/2008 (RN-TMP-13), e o Pink Sheet traz as duas séries desde 1960 em uma fonte só.
- **Exemplo:** Em 10/11/2026 a página do World Bank (`worldbank.org/en/research/commodity-markets`) listava os arquivos anual e mensal; a planilha mensal baixou com HTTP 200 e User-Agent de navegador, e o cobre vai de jan/1960 a out/2026 (reproduzido em 10/11/2026). O relatório LAB-19/10 consultou o FRED (`PIORECRUSDM`, `PCOPPUSDM`) e dizia jan/1980; isso foi contradito em 25/10 e em 10/11/2026.
- **Exceções:** A unidade do ferro é `$/dmt` (RN-TMP-14); o cobre é `$/mt`. A planilha pode mudar de layout (a linha do cabeçalho é a 5 na mensal e a 8 na anual), por isso as colunas são achadas pelo nome. O Pink Sheet pode corrigir valores antigos; guardar cada edição permite ver a mudança. Contraria a decisão de 24/10/2026 (FRED como rota). O ferro do FRED só coincide com o Pink Sheet a partir de dez/2008 (RN-TMP-13); a reserva não cobre o ferro antes disso. O cobre coincide nas duas fontes desde 1995, nas datas testadas.
- **Fonte:** DECISÃO-MANTENEDOR de 10/11/2026 (conflitos 8 e 17); LAB-19/10 §4 (FRED e World Bank Pink Sheet); DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 2.
- **Relacionadas:** RN-FON-10, RN-MOD-19, RN-TMP-13, RN-FNT-06

### RN-FNT-06: Pink Sheet como fonte única de ferro e cobre
- **Status:** DECIDIDA
- **Regra:** O Pink Sheet do World Bank é a fonte única dos preços de ferro e cobre (RN-FNT-05), sem emenda com outra fonte; o FRED é só reserva (RN-FNT-05). O trecho do ferro em que o Pink Sheet repete o valor anual em cada mês é exibido com aviso.
- **Motivo:** A emenda com o FRED criaria um salto artificial (razão de 2,31 de 1992 a 2005 entre as duas séries do ferro).
- **Exemplo:** No arquivo mensal, o ferro vale 26,6 em todos os meses de 1985 e 34,8 em todos os de 1991 (reproduzido em 10/11/2026). A planilha anual coincide numericamente com o PDF de outubro de 2026 em 2023–2025.
- **Exceções:** O rótulo da unidade do ferro diverge entre a planilha (`$/dmtu`) e o PDF (`$/dmt`); vale `$/dmt` (RN-TMP-14). Substitui a decisão de 24/10/2026 (Pink Sheet só para anos anteriores a 1980).
- **Fonte:** DECISÃO-MANTENEDOR de 10/11/2026 (conflitos 8 e 17); LAB-19/10 §4; VAL-15/10 §Matriz operacional (Commodities); DECISÕES e BLOCOS (Pink Sheet 1985–1991).
- **Relacionadas:** RN-TMP-13, RN-TMP-14, RN-FNT-05

### RN-FNT-07: Saldo de emprego é derivado
- **Status:** DECIDIDA
- **Regra:** O saldo de emprego formal deve ser derivado como admissões menos desligamentos, e admissões e desligamentos também devem ser indicadores próprios.
- **Motivo:** Não há série municipal pronta de saldo, e derivar rende dois indicadores adicionais.
- **Exemplo:** `ADMISNC` (admissões) − `DESLIGNC` (demissões) do Novo CAGED.
- **Exceções:** A rota de obtenção está em RN-FNT-20 (Novo CAGED via Base dos Dados); `ADMISNC` e `DESLIGNC` são as séries do IPEADATA, rota alternativa.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Emprego formal); BLOCOS §Bloco 2.
- **Relacionadas:** RN-FNT-20, RN-MOD-16

### RN-FNT-08: Taxa de homicídio
- **Status:** DECIDIDA
- **Regra:** A taxa de homicídio em geral vem da série `AVIOL12_THOMIC` (IPEADATA e Atlas da Violência), sem o rótulo "por arma de fogo". As mortes por arma de fogo, pedidas pela oficina, vêm do SIM via Base dos Dados, que é a rota primária para esse recorte; o IPEADATA é a rota reserva.
- **Motivo:** A série do IPEADATA mede homicídio em geral e não separa arma de fogo; o SIM, por trazer a causa do óbito, pode separá-la. Manter a taxa geral no Atlas respeita RN-FNT-15 (a taxa corrigida da causa indeterminada).
- **Exemplo:** DECISÕES indica `AVIOL12_THOMIC` municipal de 1989 a 2022 (IPEADATA e Atlas da Violência).
- **Evidência datada:** no fim deste arquivo, em [Notas de evidência](#notas-de-evidência), sob RN-FNT-08.
- **Exceções:** Depende da conta do Google Cloud (RN-FON-09). Não foi verificado se a tabela do SIM na Base dos Dados traz o município e a causa que separa arma de fogo, nem como tratar a causa indeterminada nesse recorte; a série do IPEADATA não respondeu a consultas de valores em 30/10/2026 (tempo esgotado), e não se sabe se tem dados municipais.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; Versão A: DECISÕES §Rotas de coleta por fonte, §Estratégia de fontes e acesso; BLOCOS §Bloco 4 (IPEADATA/Atlas, 04/10/2026, última edição 20/10/2026). Versão C (arma de fogo): PLANO §Bloco 4 (SIM via Base dos Dados, 30/09/2026). Não adotada: CONSUMO §Sociedade (CODEC/SEGUP principal e SIM alternativa, 02/10/2026).
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
- **Exceções:** A via Base dos Dados para RAIS, IDEB e eleitorado foi decidida em RN-FNT-21, com a credencial decidida em RN-FON-09. Em aberto: a coluna de município nas tabelas do CAGED e do IDEB, e o `table_id` técnico do eleitorado (TSE) e do Censo Escolar (tabela `escola`).
- **Fonte:** DECISÕES §Tabelas da Base dos Dados confirmadas, §Pré-requisitos e pendências; BLOCOS §Bloco 4.
- **Relacionadas:** RN-FON-03, RN-FON-19, RN-TMP-03

### RN-FNT-12: Frota de veículos
- **Status:** DECIDIDA
- **Regra:** A fonte primária da frota de veículos é a Senatran. O DETRAN-PA é fonte reserva e só entra se tiver exportação municipal confirmada. A forma de obter os dados da Senatran ainda deve ser verificada.
- **Motivo:** Três documentos indicam a Senatran; o painel do DETRAN-PA não tem exportação municipal confirmada.
- **Exemplo:** Em 17/10/2026, após reparo da cadeia de certificados, o painel do DETRAN-PA devolveu HTTP 502 (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Evidência datada:** no fim deste arquivo, em [Notas de evidência](#notas-de-evidência), sob RN-FNT-12.
- **Fonte:** DECISÃO-MANTENEDOR de 28/10/2026; Versão A: DECISÕES §Rotas de coleta por fonte e BLOCOS §Bloco 4 (Senatran via dados.gov.br, com DETRAN-PA como alternativa a avaliar; PLANO §Bloco 4 também; 04/10/2026, última edição 20/10/2026). Versão B: MAPA-TEMAS §Sociedade; CONSUMO §Sociedade, serviços e segurança (DETRAN-PA, 02/10/2026).
- **Relacionadas:** RN-TMP-02, RN-FON-20

### RN-FNT-13: Uso do solo pelo MapBiomas
- **Status:** DECIDIDA
- **Regra:** O uso do solo do MapBiomas, tanto os números por município quanto os mapas, é obtido pelo Google Earth Engine. O download das estatísticas municipais da Coleção 11 fica como alternativa para os números. A coleta depende da criação da conta e do cadastro de uso não comercial (RN-FON-09 e RN-PRI-09).
- **Motivo:** O mantenedor quer exibir mapas, e as planilhas de estatística trazem só números; o Earth Engine fornece o dado de imagem e permite recortar por município, numa única rota.
- **Exemplo:** O Earth Engine ficou PENDENTE em 17/10/2026 por falta de `GEE_PROJECT` (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Exceções:** Vale RN-TMP-05 (nome do asset não fixado). A credencial está decidida (RN-FON-09), mas a conta e o projeto ainda não foram criados, e o asset ainda não foi testado. As classes estão em RN-IND-11, e o denominador e o limite municipal em RN-IND-13.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026 (substitui a decisão do mesmo dia pelo download primário); Versão adotada: DECISÕES §Rotas de coleta por fonte e BLOCOS §Bloco 5 (Google Earth Engine, com download como alternativa; 04/10/2026, última edição 20/10/2026). Versão como alternativa: MAPA-TEMAS §Meio ambiente e CONSUMO §Meio ambiente (download das estatísticas da Coleção 11; 02/10/2026); PLANO §Bloco 5 (30/09/2026).
- **Relacionadas:** RN-TMP-05, RN-TMP-07, RN-PRI-09, RN-FON-20

### RN-FNT-14: Emissões do SEEG por download
- **Status:** DECIDIDA
- **Regra:** As emissões de CO₂ do SEEG devem ser obtidas por download de planilha por edição, porque a fonte não tem API confirmada.
- **Motivo:** Não há rota automatizável.
- **Exemplo:** Série municipal do SEEG, com gás, setor e edição.
- **Exceções:** Se a planilha baixada pode ser guardada no repositório está **EM ABERTO** (conflito 16), agora só pelo tamanho (RN-FON-15).
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 5; DECISÃO-MANTENEDOR de 24/10/2026 (conflito 16 em aberto).
- **Relacionadas:** RN-FON-15, RN-TMP-11

### RN-FNT-15: Não calcular homicídio a partir do SIM cru
- **Status:** DECIDIDA
- **Regra:** A taxa de homicídio não deve ser calculada a partir dos microdados crus do SIM, e os demais indicadores de saúde devem vir dos microdados do DATASUS (SIM, SINASC, SIH, SIA e CNES), agregados por município.
- **Motivo:** Muitas mortes entram como "causa indeterminada"; o Atlas da Violência redistribui essas mortes e publica a taxa corrigida.
- **Exemplo:** O SIM serve a indicadores de saúde, mas a taxa de homicídio usa a série corrigida do Atlas.
- **Exceções:** A taxa em geral segue o Atlas, como esta regra diz; só o recorte por arma de fogo usa o SIM, conforme RN-FNT-08, e a causa indeterminada nesse recorte ainda deve ser tratada.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Homicídios); BLOCOS §Bloco 4.
- **Relacionadas:** RN-FNT-08, RN-TMP-10, RN-TER-12

### RN-FNT-16: CadÚnico sem rota automatizada
- **Status:** DECIDIDA
- **Regra:** Os dados de pobreza do CadÚnico (CECAD 2.0) devem ser obtidos por download manual, e o observatório não deve tentar automatizar a obtenção.
- **Motivo:** Não há API.
- **Exemplo:** Pobreza e percentual de famílias pobres, com data-base e definição registradas.
- **Fonte:** DECISÕES §Rotas de coleta por fonte; BLOCOS §Bloco 4.
- **Relacionadas:** nenhuma ativa (RN-PRI-08 ficou obsoleta)

### RN-FNT-17: FAPESPA, IDSC e CLP
- **Status:** PROPOSTA
- **Regra:** Dados da FAPESPA obtidos por PDF não devem ser a única via de um indicador que possa ser recalculado das fontes federais, e IDSC e ranking da CLP devem ser tomados como arquivo da edição publicada, com cobertura dos municípios confirmada.
- **Motivo:** Depender de PDF estadual é o elo mais frágil da cadeia.
- **Exemplo:** O Barômetro da FAPESPA e o ranking da CLP entram congelados (RN-IND-04).
- **Fonte:** PLANO §Riscos e cuidados, §Bloco 6; CONSUMO §Finanças públicas e índices.
- **Relacionadas:** RN-IND-04, RN-FON-06

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
- **Status:** DECIDIDA
- **Regra:** O emprego formal (admissões e desligamentos, base do saldo de RN-FNT-07) é obtido pelo Novo CAGED via Base dos Dados. O IPEADATA e os microdados do MTE são alternativas.
- **Motivo:** Decisão do mantenedor entre três rotas das fontes; usa a mesma via da RAIS (RN-FNT-21) e evita baixar a série inteira do IPEADATA, cujo filtro não limitou a resposta.
- **Exemplo:** Uma consulta ao IPEADATA com filtro de município e limite de uma linha anunciou 63.685.034 bytes e começou por outro município (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Exceções:** Depende da credencial e da conta do Google Cloud (RN-FON-09). A coluna de município e as tabelas do Novo CAGED ainda não foram conferidas. As séries `ADMISNC` e `DESLIGNC` do IPEADATA só valem se essa rota for usada como alternativa.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; Versão adotada: PLANO §Bloco 2 (Novo CAGED via Base dos Dados; 30/09/2026). Versões como alternativa: DECISÕES §Estratégia de fontes e acesso e BLOCOS §Bloco 2 (IPEADATA; 04/10/2026, última edição 20/10/2026); MAPA-TEMAS §Economia e CONSUMO §Economia (microdados MTE/PDET; 02/10/2026). Evidência: VAL-15/10 §Matriz operacional, §Rodada adicional (15/10/2026); LAB-19/10 §4 (só `ADMISNC` testado; 19/10/2026).
- **Relacionadas:** RN-FNT-07, RN-FON-20

### RN-FNT-21: Base dos Dados ou arquivo oficial para RAIS, IDEB, TSE e Censo Escolar
- **Status:** DECIDIDA
- **Regra:** RAIS, IDEB, eleitorado (TSE) e Censo Escolar são obtidos pela Base dos Dados, sempre citados com a origem (RN-FON-03). O arquivo oficial do órgão fica como alternativa.
- **Motivo:** Decisão do mantenedor entre as duas versões das fontes; a Base dos Dados já traz as tabelas padronizadas.
- **Exemplo:** O IDEB é consumido como `br_inep_ideb.municipio` (DECISÕES), e não como arquivo do INEP por edição (CONSUMO).
- **Exceções:** Essa via usa a credencial decidida em RN-FON-09 e o escopo mínimo de RN-PRI-10; enquanto a conta e o projeto do Google Cloud não forem criados, nenhuma dessas quatro bases pode ser coletada por ela. Nenhuma das quatro foi testada de ponta a ponta por nenhuma das vias.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; Versão adotada: DECISÕES §Estratégia de fontes e acesso e BLOCOS §Bloco 4 (04/10/2026, última edição 20/10/2026). Versão como alternativa: CONSUMO §Sociedade, §Economia e MAPA-TEMAS §Sociedade (02/10/2026).
- **Relacionadas:** RN-FON-03, RN-FON-20

## Notas de evidência

Evidência datada que sustenta ou qualifica as regras acima. Cada nota é o texto original, movido sem alteração das regras; nenhuma delas muda o status da regra. Ordem: a das regras.

#### RN-FNT-04: Despesa por função pelo SICONFI (DCA)

- **Evidência de 30/10/2026 (consulta à API do SICONFI para Canaã dos Carajás, `id_ente` 1502152, só agregados):** o exercício 2025 retornou 337 linhas e o 2024 retornou 329, ambos com `hasMore` falso e limite de 5.000, ou seja, a resposta veio completa em uma página; a nota acima sobre a "primeira página" não se confirmou para essa consulta. Cada linha traz `exercicio`, `instituicao`, `cod_ibge`, `uf`, `anexo`, `rotulo`, `coluna`, `cod_conta`, `conta`, `valor` e `populacao` (75.433 nos dois anos). As colunas são cinco: despesas empenhadas, liquidadas e pagas, e inscrição de restos a pagar processados e não processados, de modo que o estágio da despesa está disponível na própria resposta. A `conta` traz 17 funções (por exemplo, "12 - Educação" e "10 - Saúde"), subfunções (por exemplo, "10.301 - ...") e a linha "Despesas Exceto Intraorçamentárias". Em 2025 a soma das 17 funções fecha com essa linha nos três estágios (pagas: R$ 1.617.558.438,04; empenhadas: R$ 1.962.905.755,76; liquidadas: R$ 1.669.925.792,85), e o mesmo ocorre em 2024. Não há linhas duplicadas por coluna e conta. A resposta não traz campo de retificação, então RN-TMP-04 ainda não pode ser conferida. Os exercícios de 2014 a 2025 retornaram dados com o nome de anexo `DCA-Anexo I-E`. O exercício de 2013 retornou 0 linhas com esse nome; sem filtro de anexo, ele trouxe o `Anexo I-E` (171 linhas), sem o rótulo e sem a linha "Despesas Exceto Intraorçamentárias", com colunas de restos a pagar nomeadas de outro modo. A seleção de contas e a abrangência função/subfunção continuam em aberto.
- **Evidência de 31/10/2026 (MSC orçamentária, classe 6, movimento mensal, API pública do SICONFI, 12 municípios da RI Carajás, 2022–2026, só agregados; coleta de teste):** a coleta gravou 299.635 linhas, lendo todas as páginas da resposta (a primeira coleta, que lia só a primeira página, gravou 294.512). Cobertura de meses: 12 meses em todos os municípios de 2023 a 2025 e em 2022, exceto Piçarra em 2022 (11 meses, de janeiro a novembro); em 2026 há dados até agosto em 7 municípios (Brejo Grande do Araguaia, Curionópolis, Eldorado do Carajás, Piçarra, São Domingos do Araguaia, São Geraldo do Araguaia e São João do Araguaia), até setembro em 3 (Canaã dos Carajás, Marabá e Parauapebas), até junho em Palestina do Pará e até maio em Bom Jesus do Tocantins. O código de fonte tem 4 dígitos em todas as linhas, de 2022 a 2026, no mesmo padrão (2022 também usa 1xxx e 2xxx; o campo `ano_fonte_recursos` vale 1 ou 2 e não é o ano do exercício). A fonte `1708` aparece em 2022 em Bom Jesus do Tocantins, Canaã dos Carajás, Curionópolis, Eldorado do Carajás, Marabá e Parauapebas; em 2023 não aparece em Brejo Grande do Araguaia; Piçarra tem `1708` desde 2024, São João do Araguaia desde 2024 e São Domingos do Araguaia desde 2025; Brejo Grande do Araguaia tem `1708` desde 2024. A `2708` só aparece em Brejo Grande do Araguaia em 2026. Palestina do Pará e São Geraldo do Araguaia não têm `1708` nem `2708` em nenhum ano; Brejo Grande do Araguaia em 2022 tem `1707` e `2707`, e Piçarra em 2023 tem `1707` (o significado desses códigos não foi verificado). A ausência da `1708` nesses casos pode indicar que o município não registrou a CFEM com esse código, que a recebeu sob outro código ou que o valor foi nulo; a causa não foi verificada. Fatia da fonte `1708` sobre o total de cada par (conta contábil, natureza D ou C), sem somar D com C e sem escolher qual conta corresponde a qual estágio (o mapeamento das contas contábeis para empenhada, liquidada e paga não foi confirmado): por exemplo, na conta `622110000` natureza D, a fatia de 2022 a 2026 foi de 73,6%, 45,0%, 44,1%, 42,8% e 44,8% em Canaã dos Carajás; 43,8%, 38,0%, 30,9%, 31,1% e 30,9% em Parauapebas; 12,0%, 9,4%, 7,4%, 10,7% e 13,7% em Marabá ; e 18,0%, 14,0%, 18,1%, 21,5% e 18,3% em Curionópolis (valores calculados sobre o CSV local em `tmp/`, não versionado; as demais contas variam bastante entre si e entre anos). Limites: o mapeamento de estágios e a conciliação com a DCA não foram feitos, e a leitura de que `1708` identifica a CFEM vem da Portaria STN 710/2021 (citada em AGENTS.md), não de verificação nesta consulta. O demonstrativo e as contas continuam em aberto; o status da regra não mudou. Os números desta nota foram refeitos em 02/11/2026 com a coleta completa; as fatias e a presença da fonte `1708` por município e ano não mudaram em relação à primeira coleta.
- **Evidência de 03/11/2026 (nova consulta à API, sem dados pessoais):** a DCA de 2024 retornou 2.537 linhas para os 12 municípios. Em 2025, foram lidas 2.534 linhas; Bom Jesus do Tocantins (`1501576`) retornou zero linhas para o Anexo I-E, bloqueando a cobertura do lote. Essas contagens são da resposta completa com as cinco colunas e não representam valores homologados.

#### RN-FNT-08: Taxa de homicídio

- **Evidência de 28/10/2026:** os metadados do IPEADATA para `AVIOL12_THOMIC` dão o nome "Taxa de homicídios (100.000 Habitantes)", fonte MS/SVS/CGIAE (SIM), atualização de 08/07/2026, sem menção a arma de fogo. O comentário da série cita códigos CID de lesões autoprovocadas (X60-X84), o que parece inconsistente com o nome; a causa não foi confirmada. A decisão de fonte e conceito segue em aberto.

#### RN-FNT-12: Frota de veículos

- **Evidência de 28/10/2026:** o arquivo "Frota por município e tipo" de setembro de 2026, baixado da página da Senatran no gov.br, tem 5.572 linhas de município em 27 UFs, uma linha por UF e município (sem repetição), e a soma dos municípios (133.337.839) fecha com o total do cabeçalho. A frota é um estoque mensal por tipo de veículo (`AUTOMOVEL`, `MOTOCICLETA`, `CAMINHAO` e outros). O Pará tem 144 municípios, entre eles Parauapebas, Canaã dos Carajás, Marabá e Curionópolis. O arquivo não traz código IBGE: o município vem só como nome em maiúsculas e sem acento, com um erro de grafia ("BARAO D0 MONTE ALTO"). A identificação por código IBGE exigiria cruzar o nome com a lista oficial de municípios, e essa regra de cruzamento ainda não foi decidida. A Senatran publica arquivos até setembro de 2026.
