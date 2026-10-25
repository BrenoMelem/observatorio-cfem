# Observatório RI Carajás — Plano de Integração de Dados

Sep 30, 2026 · @Daniel Rond

> Convertido do PDF original em 24/10/2026. O diagrama de arquitetura foi transcrito em texto.

## Visão geral

O observatório publica indicadores de Canaã dos Carajás (IBGE 1502152), Parauapebas (IBGE 1505536) e da Região de Integração Carajás numa base organizada e reutilizável. Este documento define de onde vem cada dado, como estruturá-lo, o que pode ser automatizado por API e o que exige download manual.

A RI Carajás é um recorte do governo do Pará, não do IBGE. Todo indicador regional precisa ser agregado a partir dos municípios que a compõem — por isso a lista oficial desses municípios é o primeiro pré-requisito.

São 6 blocos temáticos e cerca de 45 indicadores, vindos de 11 fontes distintas com frequências e formatos diferentes. O desafio central não é obter um dado, é manter os 45 atualizados sem manutenção constante.

## Arquitetura e fluxo geral

**Diagrama (transcrito): tudo converge para uma camada única de dados tratados.**

- **Fontes**, de três tipos:
  - APIs públicas — IBGE SIDRA, SICONFI — atualização automática.
  - BigQuery — RAIS, CAGED, SIM, IDEB — exige credencial.
  - Arquivos e PDFs — MapBiomas, SEEG, INEP, CadÚnico, FAPESPA — download manual.
- **ETL em Python** — um adaptador por fonte; normaliza ao esquema único; calcula per capita e razões; valida antes de publicar.
- **Agendador** — cron por fonte: mensal, anual ou sob demanda. Dispara o ETL.
- **Camada de dados tratados** — JSON e CSV versionados e padronizados (município, ano, indicador, valor, fonte); poucos MB no total.
- **Consumo** — painéis, relatórios, análises; sempre o mesmo formato de entrada.

O princípio é um só: quem consome os dados nunca conversa diretamente com as fontes. Entre as duas pontas existe uma camada intermediária de dados já tratados, padronizados e versionados.

Isso resolve três problemas de uma vez. Uma fonte fora do ar não quebra nada, porque o último dado bom continua disponível. Trocar a origem de um indicador não afeta quem o consome, já que o formato de saída é sempre o mesmo. E os dados ficam utilizáveis em qualquer destino — painel, relatório, análise ou um site futuro.

O agendador é o motor da atualização: roda o ETL na frequência definida para cada fonte, grava os arquivos tratados e registra a nova versão. GitHub Actions é a opção mais simples por ser gratuita e já integrada ao repositório, mas qualquer agendador serve. As fontes manuais entram na mesma camada, só que depositadas à mão e documentadas.

## Pré-requisitos

Quatro itens travam o resto do projeto e devem ser resolvidos antes de escrever código.

| # | Pré-requisito | Por que trava | Como resolver |
| --- | --- | --- | --- |
| 1 | Lista oficial dos municípios da RI Carajás | Nenhum gráfico regional fecha sem ela | Buscar a definição no governo do Pará (SEPLAD/FAPESPA) |
| 2 | Confirmação dos `dataset_id.table_id` na Base dos Dados | Nomes de tabela vindos de pesquisa podem estar errados | Conferir no catálogo; o CAGED indicado estava desatualizado |
| 3 | Ano mais recente real de cada fonte | RAIS, SIM e IDEB têm defasagem maior que a informada | Consultar cada fonte; o pipeline deve descobrir isso em tempo de execução |
| 4 | Projeto Google Cloud + credencial BigQuery | Único ponto de autenticação do projeto | Criar projeto, gerar service account, salvar como secret no GitHub |

O item 4 é gratuito no volume previsto, mas é a única peça que não funciona "de graça e sem conta". Se for um obstáculo, há plano B: usar as fontes federais primárias (IBGE e SICONFI por API) onde possível e baixar RAIS/CAGED manualmente.

## Bloco 1 — Dinâmica Populacional

Bloco inteiramente automatizável pela API de agregados do IBGE. É o melhor ponto de partida para o primeiro pipeline, porque não depende de credencial nem de download.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Evolução da população: Canaã e Parauapebas vs. RI Carajás | IBGE SIDRA (Censo 2022) | Base dos Dados `br_ibge_populacao` | API |
| Série populacional 1980–2022 | IBGE SIDRA (censos + estimativas) | Base dos Dados | API |
| Características da população na RI Carajás 2022 (idade, sexo, raça) | IBGE SIDRA (Censo 2022) | Microdados do Censo | API |

Endpoint: `https://servicodados.ibge.gov.br/api/v3/agregados`, com o parâmetro de localidade `N6[código do município]`.

Atenção à série longa: censos anteriores a 2000 vêm de tabelas SIDRA distintas, e Canaã dos Carajás só foi criada em 1994 — antes disso o território pertencia a Parauapebas e Marabá. A série "desde 1980" precisa de uma nota de rodapé explicando isso.

## Bloco 2 — Economia e Mercado de Trabalho

Bloco dividido em três naturezas: PIB e renda pela API do IBGE, emprego formal pelo BigQuery, e preços de commodities por download.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| PIB municipal 2010–2023 | IBGE SIDRA | Base dos Dados `br_ibge_pib.municipio` | API |
| % PIB RI-Carajás per capita | Calculado: PIB ÷ população | — | Derivado |
| Preço do minério de ferro USD 1985–2025 | World Bank Pink Sheet | IMF Primary Commodity Prices (tem API); Trading Economics | Download |
| Preço do cobre USD 2000–2026 | World Bank Pink Sheet | IMF; LME | Download |
| Evolução do emprego formal | Novo CAGED via Base dos Dados | Painel do Novo CAGED (MTE) | BigQuery |
| Emprego formal como % da população | Calculado: RAIS ÷ população | — | Derivado |
| % de emprego por setor | RAIS (CNAE) | — | BigQuery |
| Remuneração média total e por sexo | RAIS | FAPESPA (agregado pronto) | BigQuery |
| Vínculos por escolaridade | RAIS | FAPESPA | BigQuery |
| Rendimento domiciliar per capita | IBGE SIDRA (Censo 2022) | — | API |
| Nível de instrução por sexo | IBGE SIDRA (Censo 2022) | — | API |
| Canaã — emprego por gênero 2022 | RAIS | — | BigQuery |

Correção importante: a tabela `br_me_caged.microdados_antigos` cobre apenas até cerca de 2019. Para dados atuais é preciso usar a tabela do Novo CAGED.

As tabelas de RAIS e CAGED são grandes demais para download pela interface da Base dos Dados. O acesso tem de ser por consulta SQL filtrando os municípios de interesse, nunca baixando a tabela inteira.

Preços de commodities são a única fonte global do projeto e não têm recorte municipal. O Pink Sheet do World Bank é uma planilha mensal; o IMF oferece API e pode ser a escolha melhor se a automação for prioridade.

## Bloco 4 — Sociedade

O bloco mais heterogêneo. Todo o pacote do Censo 2022 (infraestrutura, favelas, entorno, domicílios) sai do SIDRA, não da Base dos Dados — ela ainda não publicou o Censo 2022 nesse nível de detalhe.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Notas do IDEB 2023 | Base dos Dados `br_inep_ideb` | Portal do INEP (download direto) | BigQuery |
| Distorção idade-série 2023 | INEP, painel de indicadores educacionais | FAPESPA (agregado) | Download |
| Indicador de saúde 2023 | DATASUS (TabNet / PySUS) | FAPESPA | Download |
| Pobreza 2026 | Observatório do CadÚnico | CECAD 2.0; Portal de Dados Abertos MDS | Download |
| Famílias pobres (%) | Observatório do CadÚnico | CECAD 2.0 | Download |
| Taxa de homicídio por arma de fogo 1989–2022 | SIM/DATASUS via Base dos Dados | Atlas da Violência (IPEA) | BigQuery |
| Violência 2023 | Atlas da Violência (IPEA) | FAPESPA; SIM | Misto |
| Número de veículos 2023 | Senatran, via dados.gov.br | FAPESPA | Download |
| Infraestrutura 2022 | IBGE SIDRA (Censo 2022) | — | API |
| População residente em favelas | IBGE SIDRA (Censo 2022) | — | API |
| Características do entorno | IBGE SIDRA (Censo 2022) | — | API |
| População por situação do domicílio | IBGE SIDRA (Censo 2022) | — | API |

A distorção idade-série não existe pronta na Base dos Dados: eles publicam taxas de rendimento (aprovação, reprovação, abandono), que são outra coisa. O indicador clássico vem do painel próprio do INEP.

A série de homicídios desde 1989 pode exigir duas fontes emendadas, porque o SIM na Base dos Dados começa em 1996. O Atlas da Violência cobre o período mais longo e é a alternativa para os anos iniciais.

## Bloco 5 — Meio Ambiente e Saneamento

Quase tudo vem do MapBiomas, que não tem API tabular simples. A boa notícia é que é um dado anual: basta um download por ano.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Uso do solo — área urbana (%) 1983–2024 | MapBiomas, estatísticas por município | Google Earth Engine (API) | Download |
| Cobertura florestal 1985 e 2023 | MapBiomas | GEE; INPE/PRODES | Download |
| Uso da terra = % de floresta (RI e Canaã) | MapBiomas | PRODES/TerraBrasilis | Download |
| Percentual de uso da terra 2025 | MapBiomas (coleção mais recente) | — | Download |
| Dinâmica de uso do solo de Canaã | MapBiomas, tabela de transição | GEE | Download |
| Emissão de CO₂ | SEEG (XLSX/CSV) | SIRENE (MCTI) | Download |
| Saneamento 2022 | IBGE SIDRA (Censo 2022) | SNIS | API |

O arquivo de transição de uso do solo do MapBiomas é enorme. Ele precisa ser filtrado por código de município em Python antes de qualquer tentativa de abrir ou tabular.

Se a automação total do MapBiomas virar prioridade, o caminho é a API do Google Earth Engine — mais trabalhosa de configurar, mas elimina o download manual anual.

## Bloco 6 — Finanças Públicas

Todas as despesas e receitas vêm de uma única API — a do SICONFI. Isso torna o bloco um dos mais fáceis de automatizar, apesar de ser o mais numeroso. Os indicadores compostos do fim da lista são a exceção: são índices publicados em PDF ou em papers.

| Indicador | Fonte primária | Alternativa | Método |
| --- | --- | --- | --- |
| Despesa per capita por função: Educação, Saúde, Saneamento, Segurança, Agricultura, Urbanismo (2013–2024) | SICONFI (DCA) ÷ população | Base dos Dados `br_me_siconfi` | API |
| Despesa per capita por função (consolidado) | SICONFI | — | API |
| Repasse e participação do ICMS 2023 | SICONFI | SEFA-PA (índice de participação dos municípios) | API/Download |
| Impostos como % do PIB 2023 | Calculado: SICONFI ÷ PIB IBGE | — | Derivado |
| Impostos como % da receita corrente 2023 | SICONFI | — | API |
| Composição das receitas correntes de Canaã (%) | SICONFI | — | API |
| Barômetro da Sustentabilidade 2024 | FAPESPA | — | Manual (PDF) |
| IDSC | ICS / Instituto Cidades Sustentáveis | — | Download |
| Canaã — ranking de competitividade 2025 | CLP, Ranking de Competitividade dos Municípios | — | Manual |
| Receita per capita × IDSC (relações AA, BB, BA, AB) | IPEA, Texto para Discussão 3146 (2025) | Recalcular com SICONFI + IDSC | Manual |
| Receita per capita alta e IDSC baixo (faixa AB) | IPEA, TD 3146 | Recalcular | Manual |

Endpoint do SICONFI: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/`.

As duas últimas linhas são análises de um paper, não séries publicadas. Há duas saídas: extrair os números do texto uma vez e congelá-los com a citação, ou reproduzir a metodologia do IPEA com dados próprios do SICONFI e do IDSC. A segunda é mais trabalhosa, mas deixa o indicador atualizável.

Os indicadores da FAPESPA em geral podem ser recalculados a partir das fontes federais. Vale avaliar caso a caso: depender de PDF estadual é o elo mais frágil de todo o observatório.

## Resumo por método de acesso

Cerca de metade dos indicadores roda sozinha por API; a outra metade se divide entre consulta SQL, download anual e extração manual.

| Método | Fontes | Indicadores | Esforço de manutenção |
| --- | --- | --- | --- |
| API pública | IBGE SIDRA, SICONFI | População, Censo 2022 inteiro, PIB, todas as finanças públicas | Baixo — escrever uma vez, roda por anos |
| BigQuery (Base dos Dados) | RAIS, Novo CAGED, SIM, IDEB | Emprego, remuneração, escolaridade, homicídios, IDEB | Médio — exige credencial, depois é estável |
| Download de arquivo | MapBiomas, SEEG, INEP, Senatran, CadÚnico, commodities | Meio ambiente, distorção idade-série, veículos, pobreza, preços | Médio — script de parsing que quebra quando o layout muda |
| Manual (PDF) | FAPESPA, CLP, IPEA TD 3146 | Barômetro, competitividade, relações receita × IDSC | Alto por item, mas raro — uma vez ao ano |
| Derivado | Cálculo sobre os anteriores | Per capita, percentuais, razões | Nenhum — é código próprio |

A regra que orienta as escolhas: automatizar onde há API, aceitar download onde a fonte publica arquivo estável, e documentar como manual onde só há PDF. Um scraper de PDF frágil dá mais trabalho do que baixar o arquivo uma vez por ano.

## Sugestões para facilitar a integração

Sete decisões de projeto que reduzem muito o custo de manter 45 indicadores de 11 fontes.

1. **Um formato único de saída para todos os indicadores.** Independentemente da origem, todo dado tratado vira o mesmo esquema: `municipio_id`, `municipio_nome`, `ano`, `indicador`, `valor`, `unidade`, `fonte`, `atualizado_em`. O site passa a ler sempre a mesma coisa, e trocar a fonte de um indicador não quebra o gráfico.
2. **Um arquivo de manifesto descrevendo cada indicador.** Um único `indicadores.yaml` com id, nome, bloco, fonte, método, frequência e script responsável. Ele vira a fonte da verdade: documentação, agenda de atualização e configuração do pipeline no mesmo lugar.
3. **Separar `raw` de `processed`.** O download bruto fica em `data/raw/` (ignorado pelo git quando grande), o resultado tratado em `data/processed/` (versionado). Se um parsing der errado, dá para reprocessar sem baixar tudo de novo.
4. **Um adaptador por fonte, não por indicador.** Um módulo para o IBGE, um para o SICONFI, um para a Base dos Dados. Os indicadores viram configuração chamando esses adaptadores. Isso evita 45 scripts quase idênticos.
5. **Metadados de proveniência embutidos no dado.** Cada arquivo processado carrega quando foi gerado, de qual fonte e de qual ano-base. O site pode exibir "atualizado em" automaticamente, e fica óbvio quando algo parou de atualizar.
6. **Validação antes de publicar.** Checagens simples: o município existe, o valor não é nulo, a série não encolheu em relação à versão anterior, o número está numa faixa plausível. Se falhar, o pipeline mantém o dado antigo e abre uma issue em vez de publicar lixo.
7. **Uma agenda por fonte, não uma só.** Mensal para CAGED, veículos e commodities. Anual para Censo, PIB, SICONFI, INEP, MapBiomas e SEEG. Sob demanda para FAPESPA e CadÚnico. Cada um com seu próprio workflow agendado.

Duas sugestões extras que valem considerar: um painel simples de status mostrando a última atualização de cada indicador (ajuda a perceber silêncio de fonte), e disponibilizar os dados tratados em CSV aberto — baixo custo e aumenta a credibilidade do observatório.

## Riscos e cuidados

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Cravar o ano no código | O gráfico some ou trava quando a fonte publica novo ano | Sempre consultar o ano mais recente disponível em tempo de execução |
| Fonte muda o layout do arquivo | Parsing quebra em silêncio | Validação de esquema + falha explícita, nunca publicação silenciosa |
| Defasagem maior que a esperada | Gráfico anunciando dado que não existe | Exibir sempre o ano de referência junto do número |
| Dependência de PDF da FAPESPA | Elo mais frágil da cadeia | Recalcular das fontes federais onde for possível |
| Microdados grandes no repositório | Repositório inchado e lento | Versionar só o agregado; bruto fica fora do git |
| Base dos Dados não é fonte primária | Questionamento sobre procedência | Citar sempre a fonte original (IBGE, RAIS, SICONFI) |
| Credencial do BigQuery vazada | Acesso indevido ao projeto Google Cloud | Guardar como secret do GitHub, nunca no código |

O risco mais subestimado é o primeiro. Um observatório que mostra 2023 quando já existe 2024 perde credibilidade mais rápido do que um que mostra menos indicadores.

## Próximos passos

A ordem importa: os três primeiros itens destravam o resto, e o quarto prova a arquitetura inteira com um indicador só.

1. Obter a lista oficial dos municípios da RI Carajás e fixá-la em arquivo de configuração.
2. Confirmar no catálogo da Base dos Dados os `dataset_id.table_id` e o ano mais recente real de cada tabela.
3. Criar o projeto no Google Cloud e gerar a credencial de serviço para o BigQuery.
4. Implementar um indicador ponta a ponta — população pelo SIDRA é o melhor candidato — passando por todas as etapas: coleta, tratamento, validação, publicação e agendamento.
5. Replicar o padrão para o restante do bloco 1 e para o bloco 6, que são os de API.
6. Resolver o bloco 2 (BigQuery) e o bloco 4 em seguida.
7. Montar os downloads anuais do bloco 5 e documentar os itens manuais.

O passo 4 é o mais importante: se um indicador atravessar o fluxo inteiro e chegar tratado e validado à camada de dados, todo o resto é repetição.
