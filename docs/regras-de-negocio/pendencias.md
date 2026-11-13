# Pendências

Lista única do que ainda precisa de decisão nesta documentação: as regras EM ABERTO, os itens abertos dentro de regras decididas, as divergências entre fontes, as lacunas, as regras PROPOSTAS aguardando confirmação e os conflitos com o Product Backlog, com links para as regras. Legenda de status e siglas das fontes: [README](README.md).

Datas das fontes usadas nas divergências: PLANO, 30/09/2026; CONSUMO e MAPA-TEMAS, consulta de 02/10/2026; DECISÕES e BLOCOS, 04/10/2026, última edição em 20/10/2026 (exportados em 24/10/2026, revisões 72 e 29); VAL-15/10, 15/10/2026; LAB-19/10, 19/10/2026 (execução do notebook em 17/10/2026, com o FRED reexecutado em 19/10/2026).

## 1. Regras com status EM ABERTO

| Regra | O que falta decidir | Arquivo |
| --- | --- | --- |
| RN-CFE-08 | Recuperar julho de 2025 e liberar o total anual de 2025 (em 31/10/2026, em 09/11/2026 e em 12/11/2026 o mês segue ausente no CSV; o PDF não foi achado; adiado pelo mantenedor em 12/11/2026) | [mineracao-cfem.md](mineracao-cfem.md) |

## 2. Itens em aberto dentro de regras DECIDIDAS

Estas regras estão decididas no essencial, mas um ponto delas continua sem decisão.

| Regra | Ponto em aberto |
| --- | --- |
| [RN-ENT-08](entrega-dos-dados.md) | Metas numéricas de cada critério de avaliação do assistente. Adiado por prioridade em 11/11/2026: o assistente é etapa posterior ao tratamento dos dados; fixar critérios e metas quando ela começar |

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
| 8 | Commodities | DECISÕES e BLOCOS: FRED com ferro desde 1992 e Pink Sheet 1985–1991. PLANO e MAPA-TEMAS: Pink Sheet. LAB-19/10: FRED com ferro desde jan/1980 | DECIDIDO em 10/11/2026 (RN-TMP-13, RN-FNT-05, RN-FNT-06): Pink Sheet do World Bank para ferro e cobre, em toda a série, com ferro exibido desde 1985; o FRED fica só como reserva. Em 11/11/2026 a aba `Description` da planilha confirmou as unidades e mostrou que a coluna do ferro muda de medida: o ferro passou a duas séries separadas, contrato em ¢/dmtu (1985–2005) e spot em `$/dmt` (dez/2008 em diante) (RN-TMP-13, RN-TMP-14). A decisão de 24/10/2026 (FRED como rota, início em jan/1980) foi superada pela divergência 17 |
| 9 | Base dos Dados × fonte oficial | DECISÕES e BLOCOS: RAIS, IDEB, eleitorado e Censo Escolar via Base dos Dados. CONSUMO e MAPA-TEMAS: arquivos oficiais MTE, INEP e TSE | DECIDIDO em 30/10/2026 (RN-FNT-21): Base dos Dados, arquivo oficial como alternativa; depende de RN-FON-09 |
| 10 | Cobertura da arrecadação | DECISÕES: `CFEM_Arrecadacao.csv`. SCRIPTS e VAL-15/10: `CFEM_Arrecadacao_2022_2026.csv`, 744.244 linhas | DECIDIDO (DECISÃO-MANTENEDOR, 27/10/2026): arquivo completo `CFEM_Arrecadacao.csv`, série desde 2003 (RN-CFE-22) |
| 11 | Valor nulo × ausente | DECISÕES: validação exige "valor não nulo". CONSUMO: status "ausente" é válido | RESOLVIDO por DECISÃO-MANTENEDOR (RN-MOD-06, RN-MOD-11, RN-VPU-02) |
| 12 | VPM × CFEM | DECISÕES e BLOCOS: a CFEM "serve de proxy da produção municipal". LAB-19/10: analisar a CFEM sem renomeá-la como VPM. VAL-15/10: buscar fonte alternativa antes de prometer VPM municipal | DECIDIDO em 10/11/2026 (RN-CFE-20): a CFEM é exibida só como CFEM, sem rótulo de produção; o VPM fica só no nível do Pará (RN-CFE-19). Contraria DECISÕES e BLOCOS |
| 13 | Denominador do emprego | PLANO e BLOCOS: "RAIS ÷ população", sem especificar. CONSUMO: aprovar o denominador | DECIDIDO em 02/11/2026 (RN-IND-07): dois indicadores, população total e idade ativa de 15 a 64 anos pelo Censo 2022 |
| 14 | Datação de DECISÕES e BLOCOS | O cabeçalho dos dois diz 04/10/2026, com revisões 72 e 29 exportadas em 24/10/2026. LAB-19/10 é de 19/10/2026 e traz a correção do ferro no FRED e a orientação sobre a chave | RESOLVIDO por DECISÃO-MANTENEDOR: DECISÕES e BLOCOS foram editados pela última vez em 20/10/2026 e não incorporaram LAB-19/10 nesses dois pontos; nesses pontos LAB-19/10 é mais recente. Nos demais, DECISÕES e BLOCOS são a referência de decisões |
| 15 | Períodos dos indicadores | PLANO: ferro 1985–2025, uso do solo 1983–2024, despesa 2013–2024, IDEB 2023. BLOCOS: ferro 1992–2025, uso do solo 1985–2025, despesa 2013–2025, IDEB sem ano | DECIDIDO (DECISÃO-MANTENEDOR): BLOCOS prevalece sobre PLANO, exceto o início do ferro (conflito 8) (RN-TMP-16). IDEB decidido em 27/10/2026: todas as edições disponíveis (RN-TMP-17) |
| 16 | SEEG no repositório | BLOCOS §Bloco 5: planilha "guardada no repositório". README e `.gitignore`: dado baixado fora do Git. DECISÕES: bruto fora do Git "quando grande", sem definir o limite | DECIDIDO em 10/11/2026 (RN-FON-15, RN-FNT-14): a planilha bruta do SEEG fica fora do Git (229 MB em 10/11/2026, acima do limite de 100 MB do push), arquivada numa Release; no Git, só o recorte dos 12 municípios e os metadados. Contraria BLOCOS §Bloco 5 |
| 17 | Início da série do ferro no FRED | LAB-19/10 (execução de 19/10/2026) e DECISÃO-MANTENEDOR (24/10/2026): `PIORECRUSDM` de jan/1980 a jul/2026. DECISÕES e BLOCOS: ferro desde 1992. Consulta à API do FRED em 25/10/2026: linhas de jan/1980 a set/2026, com valor ausente de jan/1980 a dez/1991 e primeiro valor em jan/1992; o mesmo vale para o cobre (`PCOPPUSDM`); metadados do FRED: início em 1992-01-01 | DECIDIDO em 10/11/2026: o início real do ferro no FRED é jan/1992 (418 linhas no gráfico público), e o ferro do FRED só coincide com o Pink Sheet a partir de dez/2008 (de 1992 a 2005 a razão é 2,31 constante). Por isso o Pink Sheet passou a ser a fonte do ferro e do cobre (RN-TMP-13, RN-FNT-05, RN-FNT-06) |

### Divergências menores

- Pré-requisitos: PLANO lista 4 pré-requisitos travantes e DECISÕES, 3 (a descoberta do ano mais recente passou a ser regra de execução, RN-TMP-01).
- Estado de TSE, DETRAN-PA e SEEG: DECISÕES (04/10) registra TSE e DETRAN-PA bloqueados (HTTP 403 e erro de SSL); VAL-15/10 (15/10) registra SEEG com 403; LAB-19/10 (19/10) registra TSE e SEEG com a página aberta e o DETRAN-PA com HTTP 502. É evolução da evidência, não de regra.
- VAL-15/10 descreve o repositório como em `master` e sem commits; em 24/10/2026 a branch principal é `main`.
- A frota aparece como mensal na agenda de DECISÕES enquanto sua fonte está em conflito (conflito 5).

## 4. Lacunas e premissas desta documentação

- **RN-FNT-01, comparação da população: resolvida para 2025 e 2026 em 30/10/2026.** Os 12 códigos do SIDRA foram consultados e comparados, sem divergência, com as tabelas municipais independentes do IBGE. As referências versionadas estão em `data/referencia-populacao-2025.json` e `data/referencia-populacao-2026.json`; a reconciliação de cada nova edição continua obrigatória. O SIDRA já disponibiliza 2026, portanto 2025 deixou de ser o ano mais recente.

- **Arrecadação de Bom Jesus do Tocantins em 2025 (RN-CFE-23, proposta).** O briefing de 30/10/2026 dizia que faltava o município em 2025. A leitura do CSV completo atual da ANM encontrou linha em janeiro, mas nenhuma de fevereiro a dezembro. A causa dos 11 meses ausentes não foi confirmada em publicação independente. Não fechar total anual municipal nem converter ausência em zero. Em 2026, o arquivo nacional tem janeiro a outubro e não há linha de Bom Jesus nem de Brejo Grande nesses meses; também requer investigação.
- **Duplicatas na arrecadação (RN-VPU-11).** Na leitura local de 30/10/2026 do arquivo completo `CFEM_Arrecadacao.csv` da ANM (325.147.685 bytes, 2.433.952 linhas), 129 linhas do recorte dos 12 municípios repetem todos os campos de outra linha. Inclui 2025/09 para Parauapebas e 2026/01–03 para Marabá. O lote está bloqueado; revisar a origem antes de definir tratamento. O relatório em `output/observatorio/tratado/cfem/relatorio.json` contém contagens por município, ano e mês, sem CPF/CNPJ.
- **Rastreamento de despesa financiada por CFEM (RN-CFE-24, proposta).** Os agregados da ANM e do SICONFI não identificam a despesa paga com CFEM. Os códigos de fonte de recursos `17080000` e `1708000` apareceram em consultas distintas, mas não foram confirmados na despesa executada. Falta verificar classificação, cobertura e extração reproduzível nos portais municipais antes de criar esse indicador. CFEM recebida e despesa por função podem ser apresentadas lado a lado, sem afirmar financiamento direto.

- **Perguntas pendentes à ANM (RN-CFE-08, RN-CFE-09 e RN-CFE-10).** Três perguntas aguardam envio, sem canal nem responsável definidos (não será por e-mail): (1) se houve repasse em julho de 2025, por que ele não consta do arquivo de distribuição e onde está o relatório desse mês; (2) por que São Domingos do Araguaia (1507151) não aparece nos arquivos da ANM, se a MSC do SICONFI registra CFEM do município desde 2024; (3) por que a receita registrada por Marabá (R$ 221,5 milhões em 2025, sem julho) é maior que o `Produtor` do arquivo (R$ 188,9 milhões) e qual o significado das modalidades `Produtor`, `Afetado` e `-`. Enquanto não houver resposta, RN-CFE-08 segue EM ABERTO, com a evidência registrada. RN-CFE-09 (ausente, causa não confirmada) e RN-CFE-10 (CFEM recebida = `Produtor`) foram decididas em 09/11/2026; as perguntas 2 e 3 só servem para confirmar as causas (inclusive a diferença de Marabá).
- **Contrato da API.** `docs/api/openapi.yaml` agora descreve somente as rotas do protótipo local e é um esboço, não um contrato aprovado. O ADR-005 registra somente o protótipo local de população e não decide a arquitetura de produção. Qualquer divergência entre o esboço e as regras deve ser registrada aqui.
- **Evidências ausentes.** A pasta `output/` está fora do Git por decisão do projeto. Os exemplos que dependem dela foram marcados como "transcrito do relatório, não conferido no JSON". Em 25/10/2026, os exemplos da CFEM (arrecadação, distribuição, autuação, reconciliação de maio de 2025 e importador) e a população do IBGE foram reproduzidos; a única diferença foi o número de linhas do arquivo de arrecadação (RN-CFE-22). O FRED foi consultado com chave e o resultado diverge do relatório (divergência 17). Em 03/11/2026, a página de 337 linhas da DCA de Canaã dos Carajás foi reproduzida, assim como a cobertura da DCA de 2024 e a ausência de Bom Jesus do Tocantins em 2025. Seguem não reproduzidos: o lote de dois municípios do IBGE que retornou HTTP 500, IPEADATA, Pink Sheet, AMB, Base dos Dados e Earth Engine (estes dois dependem de credenciais Google Cloud).
- **Tratamento de PLANO.** PLANO não consta entre as fontes que geram DECIDIDA (resposta 1 de 24/10/2026). Regras que aparecem só em PLANO foram marcadas como PROPOSTA; quando a mesma regra aparece também em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10, as duas fontes foram citadas. O mantenedor deve confirmar essa leitura.
- **Resposta 8 da Fase 1.** A resposta ao item 8 veio sem a opção marcada; foi registrado apenas o que o mantenedor escreveu (EM ABERTO, conferir `AVIOL12_THOMIC` na fonte).
- **Atualização de DECISÕES e de BLOCOS.** O mantenedor informou que atualizará os dois documentos com as decisões de 24/10/2026. Até lá, as regras citam "DECISÃO-MANTENEDOR de 24/10/2026" como fonte.
- **Divergências com os outros repositórios.** A comparação de 08/11/2026 com `obcefem_api` e `obcefem` (distribuição estimada pela lei, duplicatas, ano parcial, ano da autuação, chave do município, média PA/BR, dados fictícios) está em [divergencias-entre-repositorios.md](divergencias-entre-repositorios.md), com a decisão do mantenedor de 08/11/2026 em cada item. A decisão não mudou o status de nenhuma regra existente; ela criou regras novas e exceções (ver o próximo item).
- **Exceções de 08/11/2026 (mantenha o que a `obcefem_api` diz).** O mantenedor mandou manter o comportamento da API nos itens D2 a D11 de [divergencias-entre-repositorios.md](divergencias-entre-repositorios.md). Isso abriu exceções, anotadas em cada regra, em RN-VPU-11 (duplicatas publicadas), RN-CFE-05 e RN-CFE-06 (ano parcial e critério de volume), RN-CFE-14 e RN-CFE-16 (ano da cobrança e sem faixa "sem ano"), RN-CFE-22 (arquivos por faixa, série desde 2002), RN-TER-03 (chave por nome) e RN-MOD-03 (envelope da API mais observações no esquema comum; a API ainda não faz). Regras novas: RN-CFE-27, RN-CFE-28, RN-TER-13 e RN-ENT-11. Pendentes: medir o efeito em reais das 129 duplicatas; reconfirmar se o lote de arrecadação, citado como bloqueado acima, passa a ser publicado.
- **Obsoletas.** Oito regras ficaram obsoletas em 07/11/2026 por decisão do mantenedor (as fontes são dados abertos, então privacidade e licença não são necessárias): RN-PRI-01 a RN-PRI-06, RN-PRI-08 e RN-ENT-10. Seguem vigentes RN-PRI-07, RN-PRI-09 e RN-PRI-10. RN-CFE-18 passou a permitir exibir o nome e o CPF/CNPJ do titular; sem parecer jurídico, o CPF de pessoa física é risco aceito pelo mantenedor.

## 5. Regras PROPOSTAS aguardando confirmação

Estas 38 regras foram deduzidas ou vêm só de fontes históricas (CONSUMO, MAPA-TEMAS, PESQUISA, PLANO), do notebook, dos scripts ou do briefing operacional de 30/10/2026. Não são decisão do projeto: cada uma espera confirmação do mantenedor para virar DECIDIDA ou ser descartada. A coluna "Origem" diz de onde a regra vem.

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

### Mineração (CFEM) (4)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-CFE-11](mineracao-cfem.md) | Agregação por município, ano, mês e modalidade | SCRIPTS (`build_cfem_distribution_municipal`). Deduzida do código |
| [RN-CFE-12](mineracao-cfem.md) | Controle de escala com o total nacional | VAL-15/10 §Rodada adicional (apresentado como controle, não como regra) |
| [RN-CFE-23](mineracao-cfem.md) | Cobertura parcial de Bom Jesus do Tocantins na arrecadação de 2025 | Briefing operacional de 30/10/2026 §9; leitura do CSV completo atual; falta confronto com publicação independente da ANM |
| [RN-CFE-24](mineracao-cfem.md) | Despesa municipal financiada por CFEM exige fonte de recursos confirmada | Briefing operacional de 30/10/2026 §9; códigos e cobertura ainda não confirmados |

### Indicadores derivados e compostos (2)

| Regra | Título | Origem |
| --- | --- | --- |
| [RN-IND-05](indicadores-derivados-e-compostos.md) | Derivado ou composto é marcado como análise derivada | CONSUMO §Finanças públicas e índices (receita per capita e IDSC) |
| [RN-IND-08](indicadores-derivados-e-compostos.md) | Não recalcular o Barômetro sem reproduzir o método | CONSUMO §Finanças públicas e índices (Barômetro da Sustentabilidade 2024) |

## 6. Conflitos com o Product Backlog

O [Product Backlog](../produto/backlog.md) (retrato de 12/11/2026) diz o que o produto deve entregar; ele não é fonte de regra. Em cinco pontos o texto dos itens contradiz regras vigentes. As duas versões ficam registradas e nada foi escolhido: cada ponto espera decisão do mantenedor. Nenhuma regra mudou de status por causa desta seção.

| # | Ponto | Backlog (12/11/2026) | Regras | Situação |
| --- | --- | --- | --- | --- |
| B1 | Privacidade e LGPD | PB-45: revisar segurança e adequação à LGPD, com política de privacidade e termos de uso. PB-35: proteção de dados e registro de uso no assistente | DECISÃO-MANTENEDOR de 07/11/2026: privacidade e licença não são requisito, porque as fontes são dados abertos (RN-PRI-01 a 06 e RN-PRI-08 obsoletas; RN-CFE-18 permite exibir o titular). Essa decisão tratou dos dados das fontes; o backlog prevê também dados enviados por usuários (perfis de acesso, relatos, comentários, cadastros do marketplace: PB-04, PB-24, PB-25, PB-28, PB-37), sobre os quais não há regra | EM ABERTO |
| B2 | Recorte territorial | PB-06 e PB-22: "os dois municípios" | [RN-TER-01](territorio.md): os 12 municípios da RI Carajás. [RN-TER-13](territorio.md) (08/11/2026): Parauapebas e Canaã dos Carajás em destaque, comparados com os demais | EM ABERTO: falta dizer se o backlog restringe a carga aos dois municípios ou só nomeia os de foco |
| B3 | Período da série da CFEM | PB-06: série histórica de 10 anos de arrecadação e uso | [RN-CFE-22](mineracao-cfem.md) (27/10/2026): arrecadação desde 2003 (desde 2002 na `obcefem_api`, exceção de 08/11/2026). [RN-FNT-04](regras-por-fonte.md): despesa por função de 2013 a 2025. [RN-CFE-24](mineracao-cfem.md) (PROPOSTA): não se afirma que uma despesa foi paga com CFEM sem a fonte de recursos confirmada, o que limita o "uso da CFEM" | EM ABERTO: falta dizer se os 10 anos são o mínimo contratual ou o recorte a exibir |
| B4 | Fontes do orçamento | PB-08: atualizar ANM, TCM-PA e orçamentos municipais | [RN-FNT-04](regras-por-fonte.md) e [RN-TMP-15](temporalidade-e-atualizacao.md): a despesa por função vem só do SICONFI. TCM-PA e os orçamentos municipais não constam da agenda por fonte ([RN-TMP-02](temporalidade-e-atualizacao.md)) nem de [regras-por-fonte.md](regras-por-fonte.md); nenhuma das duas foi testada | EM ABERTO |
| B5 | Dados por bairro | PB-21, PB-22 e PB-23: limites de bairros e distritos, mapa e ficha de indicadores por bairro | Todas as regras tratam de município, RI Carajás, Pará e Brasil ([RN-TER-03](territorio.md): o código IBGE de 7 dígitos identifica o município). Não há regra, fonte nem indicador abaixo do município | EM ABERTO: falta fonte dos limites e dos indicadores por bairro |

Além dos conflitos, 24 dos 48 itens do backlog não têm regra nenhuma (escrita de dados por usuários, gestão de conteúdo, marketplace, front-end, testes e operação). A lista está na [seção 3 do backlog](../produto/backlog.md#3-correspondência-com-a-documentação); se alguma virar regra, ela nasce por decisão do mantenedor.
