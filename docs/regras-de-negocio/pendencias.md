# Pendências

Lista única de tudo o que está EM ABERTO nesta documentação, com links para as regras. Legenda de status e siglas das fontes: [README](README.md).

Datas das fontes usadas nas divergências: PLN, 30/09/2026; ANA e MAPA, consulta de 02/10/2026; REG e BT, 04/10/2026, última edição em 20/10/2026 (exportados em 24/10/2026, revisões 72 e 29); R15, 15/10/2026; L19, 19/10/2026 (execução do notebook em 17/10/2026, com o FRED reexecutado em 19/10/2026).

## 1. Regras com status EM ABERTO

| Regra | O que falta decidir | Arquivo |
| --- | --- | --- |
| RN-MOD-03 | Nomes e campos do esquema (tabela de equivalência dos dois esquemas) | [modelo-de-dados.md](modelo-de-dados.md) |
| RN-MOD-04 | Aceite do campo de mês no esquema comum | [modelo-de-dados.md](modelo-de-dados.md) |
| RN-MOD-24 | Valor nominal ou também real, com índice de correção | [modelo-de-dados.md](modelo-de-dados.md) |
| RN-FON-09 | Como o pipeline se autentica no Google Cloud (conflito 7) | [consumo-de-fontes.md](consumo-de-fontes.md) |
| RN-FON-20 | Fonte e via de acesso nos indicadores em conflito (conflitos 3, 4, 5, 6 e 9) | [consumo-de-fontes.md](consumo-de-fontes.md) |
| RN-TMP-12 | Regra para anos parciais fora da CFEM | [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md) |
| RN-TMP-14 | Unidade do minério de ferro (`$/dmtu` ou `$/dmt`) | [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md) |
| RN-TMP-17 | Ano ou edição do IDEB publicada | [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md) |
| RN-VPU-11 | Tratamento de linhas duplicadas na fonte | [validacao-e-publicacao.md](validacao-e-publicacao.md) |
| RN-VPU-12 | Tolerância da reconciliação independente | [validacao-e-publicacao.md](validacao-e-publicacao.md) |
| RN-ENT-02 | Forma de entrega: arquivos, API própria ou ambos (conflito 2) | [entrega-dos-dados.md](entrega-dos-dados.md) |
| RN-ENT-10 | Regra de reuso das exportações, conforme a licença de cada fonte | [entrega-dos-dados.md](entrega-dos-dados.md) |
| RN-CFE-07 | Critério para classificar a falta de um município num mês existente no arquivo | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-08 | Recuperar julho de 2025 e liberar o total anual de 2025 | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-09 | Causa da ausência de São Domingos do Araguaia nos arquivos | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-10 | Modalidades de distribuição que compõem a CFEM recebida | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-16 | Tratamento das autuações sem ano de publicação (88 de 176 linhas) | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-20 | Se a CFEM pode ser apresentada como proxy da produção municipal (conflito 12) | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-22 | Arquivo e cobertura histórica da arrecadação (conflito 10) | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-IND-03 | Corte exato do IPEA TD 3146 | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-IND-07 | Denominador de "emprego formal como % da população" (conflito 13) | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-IND-09 | O que mede "% PIB RI-Carajás per capita" | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-IND-11 | Classes de floresta, mineração e área urbana, denominador e edição do limite municipal | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-IND-12 | Qual CFEM e qual população entram na CFEM per capita | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-PRI-06 | Licença de redistribuição de cada fonte (FAPESPA, IDSC, SEEG) | [privacidade-e-licencas.md](privacidade-e-licencas.md) |
| RN-PRI-10 | Escopo mínimo de autorização no Google Cloud | [privacidade-e-licencas.md](privacidade-e-licencas.md) |
| RN-FNT-08 | Se `AVIOL12_THOMIC` mede "homicídio por arma de fogo", e qual fonte e conceito do indicador (conflito 4) | [regras-por-fonte.md](regras-por-fonte.md) |
| RN-FNT-12 | Fonte da frota de veículos (conflito 5) | [regras-por-fonte.md](regras-por-fonte.md) |
| RN-FNT-13 | Rota do uso do solo do MapBiomas (conflito 6) | [regras-por-fonte.md](regras-por-fonte.md) |
| RN-FNT-20 | Rota do emprego formal (conflito 3) | [regras-por-fonte.md](regras-por-fonte.md) |
| RN-FNT-21 | Base dos Dados ou arquivo oficial para RAIS, IDEB, TSE e Censo Escolar (conflito 9) | [regras-por-fonte.md](regras-por-fonte.md) |

## 2. Itens em aberto dentro de regras DECIDIDAS

Estas regras estão decididas no essencial, mas um ponto delas continua sem decisão.

| Regra | Ponto em aberto |
| --- | --- |
| [RN-TER-09](territorio.md) | Valor de N, período do ranking e modalidade de distribuição usados na comparação com mineradores |
| [RN-CFE-18](mineracao-cfem.md) | Decisão final de exibir ou não o nome da empresa autuada, após revisão jurídica |
| [RN-TMP-13](temporalidade-e-atualizacao.md) | Recorte de exibição da série do ferro: desde jan/1980 ou desde 1985, como pediu a oficina |
| [RN-TMP-15](temporalidade-e-atualizacao.md) | Emenda entre SICONFI (2013 em diante) e FINBRA (pré-2013) numa mesma série |
| [RN-FNT-04](regras-por-fonte.md) | Demonstrativo(s), contas, estágio da despesa e paginação completa do SICONFI |
| [RN-FNT-11](regras-por-fonte.md) | Coluna de município nas tabelas do CAGED e do IDEB; `table_id` do eleitorado (TSE) e do Censo Escolar |
| [RN-FNT-01](regras-por-fonte.md) | Comparação dos valores da população com a tabela publicada pelo IBGE antes de alimentar um gráfico |
| [RN-FON-15](consumo-de-fontes.md) e [RN-FNT-14](regras-por-fonte.md) | Se a planilha do SEEG pode ficar no repositório e o que conta como dado bruto "grande" (conflito 16) |
| [RN-ENT-08](entrega-dos-dados.md) | Metas numéricas de cada critério de avaliação do assistente |

## 3. Divergências entre fontes

Cada divergência registra as duas (ou mais) versões com a data de cada fonte. Nada foi escolhido, exceto onde há decisão do mantenedor de 24/10/2026 (DM).

| # | Tema | Versões | Situação |
| --- | --- | --- | --- |
| 1 | Esquema de dados | REG (04/10): `municipio_id, municipio_nome, ano, mes, indicador, valor, unidade, fonte, atualizado_em`, com `mes` pendente de aceite. PLN (30/09): o mesmo, sem `mes`. ANA (02/10) e R15 §Marco 1 (15/10): `indicator_id, geo_id, reference_period, value, unit, status, source_edition…` | EM ABERTO (RN-MOD-03, RN-MOD-04). Tabela de equivalência em [modelo-de-dados.md](modelo-de-dados.md) |
| 2 | Forma de entrega | PLN e REG: camada de arquivos JSON e CSV. R15 e ANA: API própria | EM ABERTO (RN-ENT-02). As regras valem para os dois casos |
| 3 | Emprego | REG e BT: IPEADATA (`ADMISNC` − `DESLIGNC`) para o saldo e RAIS via Base dos Dados para as quebras. PLN: Novo CAGED via Base dos Dados. MAPA e ANA: microdados MTE/PDET. R15: filtros do IPEADATA não limitaram a resposta; L19: só `ADMISNC` testado | EM ABERTO (RN-FNT-20) |
| 4 | Homicídios | REG e BT: `AVIOL12_THOMIC` (IPEADATA e Atlas), 1989–2022. PLN: SIM via Base dos Dados. ANA: CODEC/SEGUP principal e SIM alternativa. A oficina pede "por arma de fogo"; o BT diz "taxa de homicídio" | EM ABERTO (RN-FNT-08). Conferir na fonte se a série mede o conceito pedido |
| 5 | Frota | PLN, REG e BT: Senatran. MAPA e ANA: DETRAN-PA | EM ABERTO (RN-FNT-12) |
| 6 | Uso do solo | REG e BT: Google Earth Engine. PLN, MAPA e ANA: download das estatísticas da Coleção 11 | EM ABERTO (RN-FNT-13) |
| 7 | Credencial do Google Cloud | REG e PLN: conta de serviço com chave guardada como segredo; BT §Bloco 5: o Earth Engine usa a mesma credencial do BigQuery. L19 §5.3 e R15: não usar chave, autenticar com a conta de quem executa | EM ABERTO (RN-FON-09, RN-PRI-10). Não decidido pelo mantenedor: ainda não domina a plataforma, mas pretende usá-la. O L19 é mais recente nesse ponto (conflito 14) |
| 8 | Commodities | REG e BT: FRED com ferro desde 1992 e Pink Sheet 1985–1991. PLN e MAPA: Pink Sheet. L19: FRED com ferro desde jan/1980 | DECIDIDO (DM): FRED é a rota, o ferro começa em jan/1980 e o Pink Sheet só vale antes de 1980 (RN-TMP-13, RN-FNT-05, RN-FNT-06). Em aberto: unidade do ferro e recorte de exibição |
| 9 | Base dos Dados × fonte oficial | REG e BT: RAIS, IDEB, eleitorado e Censo Escolar via Base dos Dados. ANA e MAPA: arquivos oficiais MTE, INEP e TSE | EM ABERTO (RN-FNT-21) |
| 10 | Cobertura da arrecadação | REG: `CFEM_Arrecadacao.csv`. SC e R15: `CFEM_Arrecadacao_2022_2026.csv`, 744.244 linhas | EM ABERTO (RN-CFE-22) |
| 11 | Valor nulo × ausente | REG: validação exige "valor não nulo". ANA: status "ausente" é válido | RESOLVIDO por DM (RN-MOD-06, RN-MOD-11, RN-VPU-02) |
| 12 | VPM × CFEM | REG e BT: a CFEM "serve de proxy da produção municipal". L19: analisar a CFEM sem renomeá-la como VPM. R15: buscar fonte alternativa antes de prometer VPM municipal | EM ABERTO (RN-CFE-20) |
| 13 | Denominador do emprego | PLN e BT: "RAIS ÷ população", sem especificar. ANA: aprovar o denominador | EM ABERTO (RN-IND-07) |
| 14 | Datação de REG e BT | O cabeçalho dos dois diz 04/10/2026, com revisões 72 e 29 exportadas em 24/10/2026. L19 é de 19/10/2026 e traz a correção do ferro no FRED e a orientação sobre a chave | RESOLVIDO por DM: REG e BT foram editados pela última vez em 20/10/2026 e não incorporaram o L19 nesses dois pontos; nesses pontos o L19 é mais recente. Nos demais, REG e BT são a referência de decisões |
| 15 | Períodos dos indicadores | PLN: ferro 1985–2025, uso do solo 1983–2024, despesa 2013–2024, IDEB 2023. BT: ferro 1992–2025, uso do solo 1985–2025, despesa 2013–2025, IDEB sem ano | DECIDIDO (DM): o BT prevalece sobre o PLN, exceto o início do ferro (conflito 8) (RN-TMP-16). IDEB EM ABERTO (RN-TMP-17) |
| 16 | SEEG no repositório | BT §Bloco 5: planilha "guardada no repositório". README e `.gitignore`: dado baixado fora do Git. REG: bruto fora do Git "quando grande", sem definir o limite | EM ABERTO (RN-FON-15, RN-FNT-14, RN-PRI-06), junto da licença de redistribuição do SEEG |

### Divergências menores

- Pré-requisitos: o PLN lista 4 pré-requisitos travantes e o REG, 3 (a descoberta do ano mais recente passou a ser regra de execução, RN-TMP-01).
- Estado de TSE, DETRAN-PA e SEEG: o REG (04/10) registra TSE e DETRAN-PA bloqueados (HTTP 403 e erro de SSL); o R15 (15/10) registra SEEG com 403; o L19 (19/10) registra TSE e SEEG com a página aberta e o DETRAN-PA com HTTP 502. É evolução da evidência, não de regra.
- O R15 descreve o repositório como em `master` e sem commits; em 24/10/2026 a branch principal é `main`.
- A frota aparece como mensal na agenda do REG enquanto sua fonte está em conflito (conflito 5).

## 4. Lacunas e premissas desta documentação

- **Fontes ausentes.** `docs/api/openapi.yaml` e `adr/`, citados pela ANA, não existem neste repositório; não foi possível comparar com eles. Quando existirem e contradisserem as regras, a divergência deve ser registrada aqui.
- **Evidências ausentes.** A pasta `output/` está fora do Git por decisão do projeto. Os exemplos que dependem dela foram marcados como "transcrito do relatório, não conferido no JSON".
- **Tratamento do PLN.** O PLN não consta entre as fontes que geram DECIDIDA (resposta 1 de 24/10/2026). Regras que aparecem só no PLN foram marcadas como PROPOSTA; quando a mesma regra aparece também em REG, BT, L19 ou R15, as duas fontes foram citadas. O mantenedor deve confirmar essa leitura.
- **Resposta 8 da Fase 1.** A resposta ao item 8 veio sem a opção marcada; foi registrado apenas o que o mantenedor escreveu (EM ABERTO, conferir `AVIOL12_THOMIC` na fonte).
- **Atualização do REG e do BT.** O mantenedor informou que atualizará os dois documentos com as decisões de 24/10/2026. Até lá, as regras citam "DM de 24/10/2026" como fonte.
- **Obsoletas.** Nenhuma regra está obsoleta nesta versão.
