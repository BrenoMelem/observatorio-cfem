# Pendências

Lista única do que ainda precisa de decisão nesta documentação: as regras EM ABERTO, os itens abertos dentro de regras decididas, as divergências entre fontes, as lacunas e as regras PROPOSTAS aguardando confirmação, com links para as regras. Legenda de status e siglas das fontes: [README](README.md).

Datas das fontes usadas nas divergências: PLANO, 30/09/2026; CONSUMO e MAPA-TEMAS, consulta de 02/10/2026; DECISÕES e BLOCOS, 04/10/2026, última edição em 20/10/2026 (exportados em 24/10/2026, revisões 72 e 29); VAL-15/10, 15/10/2026; LAB-19/10, 19/10/2026 (execução do notebook em 17/10/2026, com o FRED reexecutado em 19/10/2026).

## 1. Regras com status EM ABERTO

| Regra | O que falta decidir | Arquivo |
| --- | --- | --- |
| RN-MOD-24 | Valor real: índice de correção, ano-base e forma de publicação (hoje só nominal, RN-MOD-26) | [modelo-de-dados.md](modelo-de-dados.md) |
| RN-CFE-08 | Recuperar julho de 2025 e liberar o total anual de 2025 | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-09 | Causa da ausência de São Domingos do Araguaia nos arquivos | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-10 | Modalidades de distribuição que compõem a CFEM recebida | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-16 | Tratamento das autuações sem ano de publicação (88 de 176 linhas) | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-CFE-20 | Se a CFEM pode ser apresentada como proxy da produção municipal (conflito 12) | [mineracao-cfem.md](mineracao-cfem.md) |
| RN-IND-03 | Corte exato do IPEA TD 3146 | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-IND-07 | Denominador de "emprego formal como % da população" (conflito 13) | [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) |
| RN-PRI-06 | Licença de redistribuição de cada fonte (FAPESPA, IDSC, SEEG) | [privacidade-e-licencas.md](privacidade-e-licencas.md) |

## 2. Itens em aberto dentro de regras DECIDIDAS

Estas regras estão decididas no essencial, mas um ponto delas continua sem decisão.

| Regra | Ponto em aberto |
| --- | --- |
| [RN-TER-09](territorio.md) | Valor de N, período do ranking e modalidade de distribuição usados na comparação com mineradores |
| [RN-CFE-18](mineracao-cfem.md) | Decisão final de exibir ou não o nome da empresa autuada, após revisão jurídica |
| [RN-TMP-13](temporalidade-e-atualizacao.md), [RN-FNT-05](regras-por-fonte.md) e [RN-FNT-06](regras-por-fonte.md) | Recorte de exibição da série do ferro: desde jan/1980 ou desde 1985, como pediu a oficina. Início real da série do ferro no FRED: jan/1980 ou jan/1992 (divergência 17) |
| [RN-TMP-15](temporalidade-e-atualizacao.md) | Emenda entre SICONFI (2013 em diante) e FINBRA (pré-2013) numa mesma série |
| [RN-FNT-04](regras-por-fonte.md) | Demonstrativo(s), contas e estágio da despesa do SICONFI; a paginação foi conferida em 30/10/2026 (resposta completa em uma página para Canaã), e o nome do anexo muda em 2013 |
| [RN-FNT-11](regras-por-fonte.md) | Coluna de município nas tabelas do CAGED e do IDEB; `table_id` do eleitorado (TSE) e do Censo Escolar |
| [RN-FNT-01](regras-por-fonte.md) | Comparação dos valores da população com a tabela publicada pelo IBGE antes de alimentar um gráfico |
| [RN-FON-15](consumo-de-fontes.md) e [RN-FNT-14](regras-por-fonte.md) | Se a planilha do SEEG pode ficar no repositório e o que conta como dado bruto "grande" (conflito 16) |
| [RN-IND-09](indicadores-derivados-e-compostos.md) | Base da participação da RI Carajás no PIB (PIB do Pará, da RI ou outra) e nomes finais dos dois indicadores no manifesto |
| [RN-ENT-08](entrega-dos-dados.md) | Metas numéricas de cada critério de avaliação do assistente |

## 3. Divergências entre fontes

Cada divergência registra as duas (ou mais) versões com a data de cada fonte. Nada foi escolhido, exceto onde há decisão do mantenedor de 24/10/2026 (DECISÃO-MANTENEDOR).

| # | Tema | Versões | Situação |
| --- | --- | --- | --- |
| 1 | Esquema de dados | DECISÕES (04/10): `municipio_id, municipio_nome, ano, mes, indicador, valor, unidade, fonte, atualizado_em`, com `mes` pendente de aceite. PLANO (30/09): o mesmo, sem `mes`. CONSUMO (02/10) e VAL-15/10 §Marco 1 (15/10): `indicator_id, geo_id, reference_period, value, unit, status, source_edition…` | DECIDIDO em 30/10/2026 (RN-MOD-03): campos em português a partir de DECISÕES, metadados no manifesto; o mês entra no esquema comum (RN-MOD-04) e o idioma é português (RN-MOD-27). Tabela de equivalência em [modelo-de-dados.md](modelo-de-dados.md) |
| 2 | Forma de entrega | PLANO e DECISÕES: camada de arquivos JSON e CSV. VAL-15/10 e CONSUMO: API própria | DECIDIDO em 30/10/2026 (RN-ENT-02): API própria. DECISÕES e PLANO precisam ser atualizados |
| 3 | Emprego | DECISÕES e BLOCOS: IPEADATA (`ADMISNC` − `DESLIGNC`) para o saldo e RAIS via Base dos Dados para as quebras. PLANO: Novo CAGED via Base dos Dados. MAPA-TEMAS e CONSUMO: microdados MTE/PDET. VAL-15/10: filtros do IPEADATA não limitaram a resposta; LAB-19/10: só `ADMISNC` testado | DECIDIDO em 30/10/2026 (RN-FNT-20): Novo CAGED via Base dos Dados; IPEADATA e microdados do MTE como alternativas |
| 4 | Homicídios | DECISÕES e BLOCOS: `AVIOL12_THOMIC` (IPEADATA e Atlas), 1989–2022. PLANO: SIM via Base dos Dados. CONSUMO: CODEC/SEGUP principal e SIM alternativa. A oficina pede "por arma de fogo"; BLOCOS diz "taxa de homicídio" | DECIDIDO em 30/10/2026 (RN-FNT-08): taxa geral pelo Atlas/IPEADATA; arma de fogo pelo SIM via Base dos Dados (tabela a conferir) |
| 5 | Frota | PLANO, DECISÕES e BLOCOS: Senatran. MAPA-TEMAS e CONSUMO: DETRAN-PA | DECIDIDO em 28/10/2026 (RN-FNT-12): Senatran, DETRAN-PA reserva |
| 6 | Uso do solo | DECISÕES e BLOCOS: Google Earth Engine. PLANO, MAPA-TEMAS e CONSUMO: download das estatísticas da Coleção 11 | DECIDIDO em 30/10/2026 (RN-FNT-13): Earth Engine para números e mapas, download como alternativa; depende de RN-FON-09 e RN-PRI-09 |
| 7 | Credencial do Google Cloud | DECISÕES e PLANO: conta de serviço com chave guardada como segredo; BLOCOS §Bloco 5: o Earth Engine usa a mesma credencial do BigQuery. LAB-19/10 §5.3 e VAL-15/10: não usar chave, autenticar com a conta de quem executa | DECIDIDO em 30/10/2026 (RN-FON-09): conta de serviço no pipeline e conta de quem executa nos testes manuais; escopo mínimo em RN-PRI-10 |
| 8 | Commodities | DECISÕES e BLOCOS: FRED com ferro desde 1992 e Pink Sheet 1985–1991. PLANO e MAPA-TEMAS: Pink Sheet. LAB-19/10: FRED com ferro desde jan/1980 | DECIDIDO (DECISÃO-MANTENEDOR): FRED é a rota, o ferro começa em jan/1980 e o Pink Sheet só vale antes de 1980 (RN-TMP-13, RN-FNT-05, RN-FNT-06). Unidade do ferro decidida em 26/10/2026 (`$/dmt`, RN-TMP-14). Em aberto: recorte de exibição. Reaberto em 25/10/2026: ver divergência 17 |
| 9 | Base dos Dados × fonte oficial | DECISÕES e BLOCOS: RAIS, IDEB, eleitorado e Censo Escolar via Base dos Dados. CONSUMO e MAPA-TEMAS: arquivos oficiais MTE, INEP e TSE | DECIDIDO em 30/10/2026 (RN-FNT-21): Base dos Dados, arquivo oficial como alternativa; depende de RN-FON-09 |
| 10 | Cobertura da arrecadação | DECISÕES: `CFEM_Arrecadacao.csv`. SCRIPTS e VAL-15/10: `CFEM_Arrecadacao_2022_2026.csv`, 744.244 linhas | DECIDIDO (DECISÃO-MANTENEDOR, 27/10/2026): arquivo completo `CFEM_Arrecadacao.csv`, série desde 2003 (RN-CFE-22) |
| 11 | Valor nulo × ausente | DECISÕES: validação exige "valor não nulo". CONSUMO: status "ausente" é válido | RESOLVIDO por DECISÃO-MANTENEDOR (RN-MOD-06, RN-MOD-11, RN-VPU-02) |
| 12 | VPM × CFEM | DECISÕES e BLOCOS: a CFEM "serve de proxy da produção municipal". LAB-19/10: analisar a CFEM sem renomeá-la como VPM. VAL-15/10: buscar fonte alternativa antes de prometer VPM municipal | EM ABERTO (RN-CFE-20) |
| 13 | Denominador do emprego | PLANO e BLOCOS: "RAIS ÷ população", sem especificar. CONSUMO: aprovar o denominador | EM ABERTO (RN-IND-07) |
| 14 | Datação de DECISÕES e BLOCOS | O cabeçalho dos dois diz 04/10/2026, com revisões 72 e 29 exportadas em 24/10/2026. LAB-19/10 é de 19/10/2026 e traz a correção do ferro no FRED e a orientação sobre a chave | RESOLVIDO por DECISÃO-MANTENEDOR: DECISÕES e BLOCOS foram editados pela última vez em 20/10/2026 e não incorporaram LAB-19/10 nesses dois pontos; nesses pontos LAB-19/10 é mais recente. Nos demais, DECISÕES e BLOCOS são a referência de decisões |
| 15 | Períodos dos indicadores | PLANO: ferro 1985–2025, uso do solo 1983–2024, despesa 2013–2024, IDEB 2023. BLOCOS: ferro 1992–2025, uso do solo 1985–2025, despesa 2013–2025, IDEB sem ano | DECIDIDO (DECISÃO-MANTENEDOR): BLOCOS prevalece sobre PLANO, exceto o início do ferro (conflito 8) (RN-TMP-16). IDEB decidido em 27/10/2026: todas as edições disponíveis (RN-TMP-17) |
| 16 | SEEG no repositório | BLOCOS §Bloco 5: planilha "guardada no repositório". README e `.gitignore`: dado baixado fora do Git. DECISÕES: bruto fora do Git "quando grande", sem definir o limite | EM ABERTO (RN-FON-15, RN-FNT-14, RN-PRI-06), junto da licença de redistribuição do SEEG |
| 17 | Início da série do ferro no FRED | LAB-19/10 (execução de 19/10/2026) e DECISÃO-MANTENEDOR (24/10/2026): `PIORECRUSDM` de jan/1980 a jul/2026. DECISÕES e BLOCOS: ferro desde 1992. Consulta à API do FRED em 25/10/2026: linhas de jan/1980 a set/2026, com valor ausente de jan/1980 a dez/1991 e primeiro valor em jan/1992; o mesmo vale para o cobre (`PCOPPUSDM`); metadados do FRED: início em 1992-01-01 | EM ABERTO: o mantenedor deve reconfirmar a decisão do conflito 8 (início em jan/1980 e Pink Sheet só antes de 1980). Se o início real for 1992, vale o que DECISÕES e BLOCOS diziam e o Pink Sheet cobre 1985–1991. Afeta RN-TMP-13, RN-FNT-05, RN-FNT-06 e a tabela de períodos em [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md) |

### Divergências menores

- Pré-requisitos: PLANO lista 4 pré-requisitos travantes e DECISÕES, 3 (a descoberta do ano mais recente passou a ser regra de execução, RN-TMP-01).
- Estado de TSE, DETRAN-PA e SEEG: DECISÕES (04/10) registra TSE e DETRAN-PA bloqueados (HTTP 403 e erro de SSL); VAL-15/10 (15/10) registra SEEG com 403; LAB-19/10 (19/10) registra TSE e SEEG com a página aberta e o DETRAN-PA com HTTP 502. É evolução da evidência, não de regra.
- VAL-15/10 descreve o repositório como em `master` e sem commits; em 24/10/2026 a branch principal é `main`.
- A frota aparece como mensal na agenda de DECISÕES enquanto sua fonte está em conflito (conflito 5).

## 4. Lacunas e premissas desta documentação

- **Fontes ausentes.** `docs/api/openapi.yaml` e `adr/`, citados por CONSUMO, não existem neste repositório; não foi possível comparar com eles. Quando existirem e contradisserem as regras, a divergência deve ser registrada aqui.
- **Evidências ausentes.** A pasta `output/` está fora do Git por decisão do projeto. Os exemplos que dependem dela foram marcados como "transcrito do relatório, não conferido no JSON". Em 25/10/2026, os exemplos da CFEM (arrecadação, distribuição, autuação, reconciliação de maio de 2025 e importador) e a população do IBGE foram reproduzidos; a única diferença foi o número de linhas do arquivo de arrecadação (RN-CFE-22). O FRED foi consultado com chave e o resultado diverge do relatório (divergência 17). Seguem não reproduzidos: o lote de dois municípios do IBGE que retornou HTTP 500, a página de 337 linhas do SICONFI, IPEADATA, Pink Sheet, AMB, Base dos Dados e Earth Engine (estes dois dependem de credenciais Google Cloud).
- **Tratamento de PLANO.** PLANO não consta entre as fontes que geram DECIDIDA (resposta 1 de 24/10/2026). Regras que aparecem só em PLANO foram marcadas como PROPOSTA; quando a mesma regra aparece também em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10, as duas fontes foram citadas. O mantenedor deve confirmar essa leitura.
- **Resposta 8 da Fase 1.** A resposta ao item 8 veio sem a opção marcada; foi registrado apenas o que o mantenedor escreveu (EM ABERTO, conferir `AVIOL12_THOMIC` na fonte).
- **Atualização de DECISÕES e de BLOCOS.** O mantenedor informou que atualizará os dois documentos com as decisões de 24/10/2026. Até lá, as regras citam "DECISÃO-MANTENEDOR de 24/10/2026" como fonte.
- **Obsoletas.** Nenhuma regra está obsoleta nesta versão.

## 5. Regras PROPOSTAS aguardando confirmação

Estas 36 regras foram deduzidas ou vêm só de fontes históricas (CONSUMO, MAPA-TEMAS, PESQUISA, PLANO), do notebook ou dos scripts. Não são decisão do projeto: cada uma espera confirmação do mantenedor para virar DECIDIDA ou ser descartada. A coluna "Origem" diz de onde a regra vem.

### Território (4)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-TER-04](territorio.md) | Código tratado como texto | NOTEBOOK (célula 1); SCRIPTS (`build_cfem_distribution_municipal`, `validate_anm_cfem`) |
| [RN-TER-07](territorio.md) | Comparação de nomes sem acento e sem diferença de caixa, apenas para o Pará | SCRIPTS (`validate_anm_cfem`, rotina de normalização e filtro de UF). Deduzida do código |
| [RN-TER-11](territorio.md) | Guardar a composição territorial usada | CONSUMO §Contrato de dados para o front-end (campos `geo_id`, `geo_level`) |
| [RN-TER-12](territorio.md) | Declarar se o indicador usa residência ou ocorrência | VAL-15/10 §Como repetir os testes (item sobre PySUS); CONSUMO §Sociedade (localidade de referência). Dedução: nenhuma das duas fontes fixa a regra |

### Modelo de dados (6)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-MOD-12](modelo-de-dados.md) | Preservar o motivo da não divulgação | CONSUMO §Sociedade (IDEB) |
| [RN-MOD-14](modelo-de-dados.md) | Não misturar projeção | CONSUMO §Dinâmica populacional |
| [RN-MOD-15](modelo-de-dados.md) | Não interpolar anos sem dado | MAPA-TEMAS §Economia e mercado de trabalho; CONSUMO §Economia e mercado de trabalho |
| [RN-MOD-16](modelo-de-dados.md) | Fluxo e estoque não se somam | CONSUMO §Economia e mercado de trabalho; VAL-15/10 §Matriz operacional (RAIS, CAGED, emprego: "validar fluxo versus estoque") |
| [RN-MOD-17](modelo-de-dados.md) | Razões registram numerador, denominador e ano | CONSUMO §Economia e mercado de trabalho, §Finanças públicas e índices |
| [RN-MOD-18](modelo-de-dados.md) | Razão regional como soma sobre soma | Dedução, por coerência com DECISÕES §Municípios da RI Carajás e RN-MOD-17. Nenhuma fonte fixa essa fórmula |

### Consumo de fontes (6)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-FON-01](consumo-de-fontes.md) | Níveis de acesso medem a forma, não a qualidade | CONSUMO §Classificação de consumo; MAPA-TEMAS (critério da coluna "Tem API?") |
| [RN-FON-05](consumo-de-fontes.md) | Não contornar login nem usar endpoints internos de painéis | CONSUMO §Conclusão executiva, §Bypass seguro quando não houver API; MAPA-TEMAS §Resumo para apresentação |
| [RN-FON-06](consumo-de-fontes.md) | PDF só entra por área de revisão | CONSUMO §Bypass seguro quando não houver API (item 3). Dedução complementar: DECISÕES §Estratégia ("documentar como manual onde só há PDF") trata do mesmo risco, sem prever a revisão |
| [RN-FON-12](consumo-de-fontes.md) | Teto de bytes por consulta | NOTEBOOK (células 16 e 18); VAL-15/10 §Como repetir os testes (item 7: "O código impõe 100 MiB por consulta"). O valor é do laboratório, não uma decisão para produção |
| [RN-FON-14](consumo-de-fontes.md) | Filtros usados ficam registrados | CONSUMO §Bypass seguro quando não houver API (item 2); SCRIPTS (`reconcile_anm_distribution`) |
| [RN-FON-17](consumo-de-fontes.md) | Fontes manuais entram na mesma camada | PLANO §Arquitetura e fluxo geral |

### Regras por fonte (2)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-FNT-17](regras-por-fonte.md) | FAPESPA, IDSC e CLP | PLANO §Riscos e cuidados, §Bloco 6; CONSUMO §Finanças públicas e índices |
| [RN-FNT-19](regras-por-fonte.md) | Conferir que a resposta identifica o município pedido | SCRIPTS (`probe_ibge_sidra`); VAL-15/10 §Rodada adicional |

### Temporalidade e atualização (6)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-TMP-04](temporalidade-e-atualizacao.md) | Retificações do SICONFI | CONSUMO §Finanças públicas e índices (despesa per capita). VAL-15/10 §Matriz operacional cita "reconciliar totais retificados" como pendência, sem fixar a regra |
| [RN-TMP-06](temporalidade-e-atualizacao.md) | Congelar a versão a cada coleção do MapBiomas | CONSUMO §Meio ambiente e saneamento |
| [RN-TMP-08](temporalidade-e-atualizacao.md) | Mudança de nomenclatura entre censos | CONSUMO §Sociedade, serviços e segurança; MAPA-TEMAS §Sociedade |
| [RN-TMP-09](temporalidade-e-atualizacao.md) | Registros policiais podem ser retificados | CONSUMO §Sociedade, serviços e segurança |
| [RN-TMP-10](temporalidade-e-atualizacao.md) | Transição CID-9 e CID-10 no SIM | CONSUMO §Sociedade, serviços e segurança |
| [RN-TMP-11](temporalidade-e-atualizacao.md) | Estimativa por proxy não é medição direta | CONSUMO §Meio ambiente e saneamento |

### Entrega dos dados (4)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-ENT-05](entrega-dos-dados.md) | Exportações levam os metadados junto dos valores | CONSUMO §Contrato de dados para o front-end |
| [RN-ENT-07](entrega-dos-dados.md) | O assistente responde só com a camada publicada | CONSUMO §Contrato de dados para o front-end. VAL-15/10 §Resposta ao orientador (item 2) lista como critério de avaliação a "recusa de inventar número ausente", sem fixar a regra |
| [RN-ENT-08](entrega-dos-dados.md) | Critérios de avaliação do assistente | VAL-15/10 §Resposta ao orientador (item 2). O próprio VAL-15/10 chama os critérios de "propostos" |
| [RN-ENT-09](entrega-dos-dados.md) | Primeiros gráficos | VAL-15/10 §Resposta ao orientador (item 3), que é uma recomendação do relatório e não uma decisão de DECISÕES ou de BLOCOS; BLOCOS §Bloco 1 (população como primeiro pipeline) |

### Mineração (CFEM) (2)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-CFE-11](mineracao-cfem.md) | Agregação por município, ano, mês e modalidade | SCRIPTS (`build_cfem_distribution_municipal`). Deduzida do código |
| [RN-CFE-12](mineracao-cfem.md) | Controle de escala com o total nacional | VAL-15/10 §Rodada adicional (apresentado como controle, não como regra) |

### Indicadores derivados e compostos (2)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-IND-05](indicadores-derivados-e-compostos.md) | Derivado ou composto é marcado como análise derivada | CONSUMO §Finanças públicas e índices (receita per capita e IDSC) |
| [RN-IND-08](indicadores-derivados-e-compostos.md) | Não recalcular o Barômetro sem reproduzir o método | CONSUMO §Finanças públicas e índices (Barômetro da Sustentabilidade 2024) |

### Privacidade e licenças (4)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-PRI-02](privacidade-e-licencas.md) | Registros individuais não são coletados nem publicados | CONSUMO §Sociedade, serviços e segurança (Pobreza) |
| [RN-PRI-03](privacidade-e-licencas.md) | Agregar microdados antes de expor | CONSUMO §Economia e mercado de trabalho |
| [RN-PRI-04](privacidade-e-licencas.md) | Proteger grupos muito pequenos | CONSUMO §Sociedade, serviços e segurança (Veículos, infraestrutura censitária, favelas, entorno) |
| [RN-PRI-08](privacidade-e-licencas.md) | Não usar a área restrita do CECAD | CONSUMO §Sociedade, serviços e segurança (Pobreza); MAPA-TEMAS §Sociedade. DECISÕES §Rotas de coleta por fonte registra apenas "sem API; só download manual" |
