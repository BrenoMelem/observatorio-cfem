# Análise de consumo de dados por tópico do Observatório CFEM

**Finalidade:** servir de base para decidir como obter, tratar, versionar e entregar cada indicador do observatório de Canaã dos Carajás e Parauapebas. **Escopo:** somente consumo e publicação de dados; este documento não especifica nem implementa o produto, a hospedagem ou uma stack. **Consulta às fontes:** 2 de outubro de 2026.

Este documento consolida a tabela de disponibilidade de API enviada pelo usuário, a lista de indicadores da oficina e a pesquisa técnica anterior sobre o Observatório CFEM. Usa também como referência de contrato o [modelo OpenAPI genérico](../../../api/openapi.yaml), sem alterá-lo: ele ainda contém campos de exemplo e não deve ser entendido como API do observatório.

**Validação complementar de 15/10/2026:** a [rodada registrada no relatório](relatorio-validacao-e-proximos-passos-2026-10-15.md) confirmou valores da estimativa populacional 2025 para 12/12 municípios no IBGE/SIDRA e filtrou os arquivos integrais de arrecadação, distribuição e autuação da ANM. A distribuição de maio de 2025 foi reconciliada em três municípios com PDF da ANM. O CSV de distribuição não contém julho de 2025 em nenhuma linha nacional, apesar de a ANM ter publicado o repasse; por isso, o total anual de 2025 está bloqueado. Ausência de linha municipal não significa valor zero. Esta nota atualiza a evidência de consumo, sem alterar a classificação de meio de acesso A/B/C/D abaixo.

## Conclusão executiva

Não existe um único tipo de integração para todos os tópicos. A estratégia viável é híbrida: API documentada quando existe; arquivo oficial ou tabela HTML quando a fonte publica dados estruturados; exportação autorizada e processamento em lote para sistemas sem API; extração de PDF com conferência humana quando não há alternativa estruturada; e nenhum contorno de acesso restrito. “Sem API” não significa “sem automação”, mas também não autoriza depender de endpoints internos de painéis ou de raspagem frágil.

As principais correções à tabela inicial são:

- **MTE/RAIS/CAGED:** não há uma API REST pública simples identificada, mas existem microdados não identificados em TXT delimitado por ponto e vírgula. A consulta interativa PDET permite exportações, porém requer senha individual; portanto, são dois caminhos de acesso diferentes. [Microdados MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged) e [Acesso Online PDET](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/estatisticas-trabalho/acesso-online)
- **FAPESPA:** não é apenas PDF. Além dos perfis municipais, há páginas de anuário com tabelas HTML por indicador — inclusive receita corrente e repasse de ICMS. Elas são candidatas a ingestão automatizada com validação de estrutura, mas não equivalem a uma API nem dispensam conferência de licença e versão. [Estatística Municipal](https://www.fapespa.pa.gov.br/estatistica-municipal/) e [exemplo de tabela de ICMS](https://fapespa.pa.gov.br/sistemas/anuario2024/tabelas/economia/2.6-financas-publicas/tab-2.6.1-repasse-de-icms-dos-municipios-do-para-2019-a-2023.htm)
- **CadÚnico/CECAD:** há consulta pública agregada e série histórica, com defasagem indicada de cerca de dois meses. O módulo “sem Bolsa Família” é restrito a gestores e técnicos; não se deve dizer que todos os dados são fechados nem tratar a área restrita como bypass. Não foi identificada API pública documentada. [Sobre o CECAD](https://cecad.cidadania.gov.br/sobre.php) e [painel CECAD](https://cecad.cidadania.gov.br/)
- **Segurança pública:** além do painel de transparência da SEGUP, o portal estatístico CODEC/SEGUP permite consulta pública e download de tabelas; a consulta é feita por intervalos de até um ano e os registros podem ser revistos. Isso viabiliza extração anual assistida, mas ainda não comprova a série de homicídios por arma de fogo desde 1989. [Metodologia do painel SEGUP](https://sistemas.segup.pa.gov.br/transparencia/metodologia-dashboard/) e [CODEC/SEGUP](https://codec.segup.pa.gov.br/)
- **Frota:** o DETRAN-PA mantém um painel público de frota com filtros municipais e emissão de relatório. Não foi identificada API pública documentada; confirmar se a saída pode ser baixada em formato estruturado. [Painel de frota DETRAN-PA](https://dashboard-frota.detran.pa.gov.br/)
- **MapBiomas:** a Coleção 11 para cobertura e uso da terra cobre 1985–2025 e oferece estatísticas por classe e arquivos GeoTIFF. Assim, o ponto de 1983 não é atendido por essa coleção; exige outra fonte explicitamente compatível ou deve ser retirado/renegociado. MapBiomas e PRODES não são séries intercambiáveis. [Cobertura 30 m, Coleção 11](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-30m/cobertura/)
- **CLP:** a edição de 2025 disponibiliza relatório e planilha de dados, não apenas PDF. A extração pode ser automatizada como arquivo versionado, após confirmar se cada município aparece no universo daquela edição. [Materiais do Ranking 2025](https://conteudo.clp.org.br/relatorios-tecnicos-2025)

## Classificação de consumo

| Nível | Significado | Forma de consumo adequada |
|---|---|---|
| A — API documentada | A fonte publica rotas e parâmetros suportados. | Consultas programadas, paginação, limites e resposta bruta preservada. |
| B — arquivo ou tabela estruturada | CSV, XLSX, TXT, GeoTIFF ou tabela HTML publicada oficialmente, sem API documentada. | Download/exportação por versão; registrar URL, data, checksum e validar esquema antes de atualizar. |
| C — exportação assistida | Painel público ou PDF que exige seleção, exportação, parser ou transcrição. | Usar recurso oficial; colocar resultado em staging; revisar e reconciliar antes de publicar. Automatizar somente a parte estável e permitida. |
| D — acesso condicionado ou lacuna | Requer credencial, autorização, cooperação, ou não há série/cobertura confirmada. | Solicitar acesso/dado agregado; não raspar ou contornar autenticação; manter indicador como pendente quando necessário. |

O nível mede a forma de acesso, não a qualidade substantiva do indicador. Uma fonte B pode ser mais confiável que uma API A, e uma fonte C pode ser suficiente para uma publicação anual, desde que a extração fique auditável.

## Matriz de consumo por tópico

### CFEM e receitas minerais

| Indicadores da plataforma | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| Arrecadação, distribuição e autuações de CFEM por município, período, substância e dimensões publicadas | ANM: arquivos abertos CSV de arrecadação, distribuição e autuação; o observatório/painel ANM é útil para conferência, mas os arquivos são melhores para ingestão reproduzível. [Dados abertos CFEM](https://dadosabertos.anm.gov.br/CFEM/) · [Dicionário de dados](https://app.anm.gov.br/dadosabertos/arrecadacao/Dicion%C3%A1rio%20de%20Dados%20-%20CFEM.pdf) · [Painel ANM](https://www.gov.br/anm/pt-br/assuntos/acesso-a-sistemas/portal-sigmine/destaques-sigmine/painel-interativo-da-cfem/) | B; captura em lote, versionada, com agregação no servidor | Separar local de extração/arrecadação do local e ente recebedor da distribuição. A arrecadação das empresas em um município não equivale ao valor posteriormente distribuído a esse município. Guardar edição e dicionário; não entregar arquivos integrais de centenas de MB ao navegador. [Diferença entre arrecadação e distribuição](https://www.gov.br/anm/pt-br/assuntos/noticias/cfem-entenda-a-diferenca-entre-arrecadacao-e-distribuicao-dos-recursos-aos-municipios) |

### Dinâmica populacional

| Indicadores da oficina | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| Evolução de população de Canaã e Parauapebas frente à RI Carajás; série municipal 1980–2022 ou mais atual; características da população da RI em 2022 | IBGE/SIDRA e API de Agregados/Localidades. Selecionar tabela, variável, período e nível geográfico; usar arquivos tabulados oficiais quando a tabela específica não estiver na API. [Documentação das APIs IBGE](https://servicodados.ibge.gov.br/api/docs/) | A para agregados/documentação cobertos; B para arquivos complementares | Fixar códigos IBGE e a composição/limite territorial da RI. Não misturar Censo, estimativa anual e projeção sem identificar a série e a quebra metodológica. A soma da RI deve ser reproduzível pela lista de municípios e não por nomes digitados livremente. |

### Economia e mercado de trabalho

| Indicadores da oficina | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| PIB municipal 2010–2023; PIB per capita e participação da RI Carajás; produção agrícola, se entrar no escopo | IBGE/SIDRA/API de Agregados e tabelas das Contas Regionais/Municipais; perfil/anuário FAPESPA como consolidação ou contingência. Produção agrícola usa a tabela apropriada da PAM/SIDRA, não o PIB. [IBGE APIs](https://servicodados.ibge.gov.br/api/docs/) | A quando tabela e variável estiverem cobertas; B/C para planilha ou perfil | A lista precisa ser conferida contra os anos efetivamente publicados: o perfil FAPESPA consultado traz determinadas séries só até anos anteriores a 2023. PIB per capita é derivado: registrar numerador, população/ano usados e unidade monetária; não calcular percentuais da RI com denominadores de anos diferentes. |
| Preço do minério de ferro (1985–2025) e cobre (2000–2026) em USD | World Bank Commodity Markets/Pink Sheet, arquivo XLS mensal. O portal publicava o arquivo mensal de setembro de 2026 na consulta desta análise. [Commodity Markets](https://www.worldbank.org/en/research/commodity-markets) | B; download mensal automatizável se a localização do arquivo for descoberta pelo portal e o formato for validado | São preços globais de referência, não preço realizado no Pará ou preço de venda de uma empresa. Preservar nome da série, unidade (ex.: USD por tonelada), frequência, média anual eventualmente calculada e mês da edição. Não contratar API paga sem requisito de baixa latência. |
| Evolução do emprego CAGED; emprego formal/ população e composição setorial da RI em 2025; emprego por gênero em Canaã em 2022 | MTE/PDET: microdados não identificados TXT por competência/ano ou consulta online exportada (com senha individual). [Microdados](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged) · [Acesso Online](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/estatisticas-trabalho/acesso-online) | B para microdados públicos; C/D para consultas dependentes de senha | CAGED/Novo CAGED é fluxo de admissões e desligamentos; RAIS é estoque anual de vínculos. Não somar os dois como se fossem a mesma medida. Para “emprego formal como % da população”, aprovar e publicar o denominador (população total, população em idade ativa ou força de trabalho) e manter a mesma regra entre territórios. Agregar antes de expor, excluir identificadores que não sejam necessários e guardar dicionário/classificações da edição. |
| Remuneração média por sexo (RAIS/FAPESPA, 2023); vínculos por escolaridade; escolaridade por sexo | RAIS/PDET para cálculo reproduzível; tabelas do anuário/perfil FAPESPA para conferência ou série pronta | B/C | Definir se a média usa vínculos, trabalhadores, remuneração nominal ou corrigida e qual universo. Registrar categoria de escolaridade e tratamento de valores ignorados. A tabela FAPESPA não substitui o dicionário da RAIS. |
| Rendimento domiciliar mensal per capita | IBGE, pesquisa/tabela compatível com o nível geográfico e ano pretendidos | A ou B conforme tabela; não presumir API para todo cruzamento | Distinguir Censo de PNAD e renda domiciliar per capita de salário médio formal. Série municipal não deve ser interpolada silenciosamente entre anos censitários. |

### Sociedade, serviços e segurança

| Indicadores da oficina | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| IDEB 2023; distorção idade-série 2023 | INEP: arquivos/planilhas por edição e indicadores do Censo Escolar. [Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) · [Nota informativa do IDEB 2023](https://download.inep.gov.br/ideb/nota_informativa_ideb_2023.pdf) | B; parser por edição | Para 2023, o INEP não divulga nota municipal em certos casos de participação insuficiente. Ausência não é zero. Preservar etapa, rede, edição e motivo de não divulgação. |
| Indicador de saúde 2023; violência 2023; frota de veículos 2023 | FAPESPA, por perfil municipal, anuário e tabelas publicadas; para saúde, identificar o indicador original e consultar a base produtora correspondente (p.ex., DATASUS) antes de automatizar. Para frota, testar o relatório municipal do [painel DETRAN-PA](https://dashboard-frota.detran.pa.gov.br/) e usar anuário/perfil FAPESPA como conferência ou contingência. | B para tabela HTML estável; C para PDF/painel | Não tratar “indicador de saúde” ou “violência” como nome suficiente: exigir fórmula, unidade, população-alvo, sistema de origem, período de referência e nota metodológica. O painel de frota não equivale a API; verificar formato exportado, cobertura histórica e termos de reutilização. A licença/condição de reprodução da FAPESPA deve ser verificada para cada produto antes de republicar. |
| Pobreza 2026; percentual de famílias pobres em julho de 2026 | CECAD 2.0, consulta pública agregada e série histórica municipal; usar a data-base julho de 2026 e registrar a definição exibida pelo sistema. [Sobre o CECAD](https://cecad.cidadania.gov.br/sobre.php) · [Painel público](https://cecad.cidadania.gov.br/) | C; exportação/tabela pública assistida. API pública documentada não identificada. | O CECAD informa defasagem aproximada de dois meses para dados “com Bolsa Família”; o recorte sem Bolsa Família é restrito a gestores/técnicos. A categoria e os limites de renda mudam no tempo: manter definição e quebra metodológica. Não coletar nem publicar registros individuais. |
| Taxa de homicídio por arma de fogo por 100 mil habitantes (1989–2022); violência e mortes violentas | Usar consulta pública e exportação de tabela do [CODEC/SEGUP](https://codec.segup.pa.gov.br/), complementada pelo painel de [metodologia](https://sistemas.segup.pa.gov.br/transparencia/metodologia-dashboard/) e [exportação SEGUP](https://sistemas.segup.pa.gov.br/transparencia/exportar-dados/). O CODEC aceita consultas anuais e download; DATASUS/SIM é alternativa para óbitos por causa externa via [TABNET](https://datasus.saude.gov.br/informacoes-de-saude-tabnet/) e arquivos de transferência. | B/C; extração anual reproduzível; a série 1989–2022 fica condicionada à cobertura confirmada | Consultas CODEC limitadas a um ano por vez podem ser automatizadas em lotes anuais, respeitando os recursos públicos, e os arquivos precisam registrar filtros/data de extração. Os registros policiais podem ser retificados; não presumir que a primeira publicação é definitiva. Confirmar início da série e disponibilidade do “meio empregado”. Não emendar homicídios policiais e óbitos do SIM numa série única sem explicar conceito e localidade de referência. Se usar SIM, documentar transição CID-9/CID-10 e regra para arma de fogo. Denominador anual e fonte populacional devem ser explícitos. “VIGIA–Belém”, citado na oficina, não identifica por si só uma base ou produto: confirmar nome completo e URL com a equipe antes de classificá-lo; não presumir equivalência com SISP ou CODEC. |
| Veículos 2023; infraestrutura censitária; favelas/comunidades urbanas; entorno; situação urbana/rural | Para frota, testar relatório municipal no [painel público DETRAN-PA](https://dashboard-frota.detran.pa.gov.br/) e conferir com FAPESPA; demais itens pelo Censo 2022/IBGE e tabelas/arquivos geográficos apropriados. [IBGE APIs](https://servicodados.ibge.gov.br/api/docs/) | A/B para tabelas do IBGE; C para painel/relatório de frota | Não foi identificada API documentada do painel de frota: verificar se permite exportar valores, não apenas PDF/visualização, e usar automação de navegador somente se compatível com termos e estável. O IBGE passou a usar a terminologia “Favelas e Comunidades Urbanas”; não comparar automaticamente com “aglomerados subnormais” de edição antiga. Algumas variáveis de entorno têm escala de setor censitário: confirmar se existe agregação municipal publicada e proteger grupos muito pequenos. |

### Meio ambiente e saneamento

| Indicadores da oficina | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| Área urbana (1983–2024); floresta em 1985 e 2023; percentual de floresta; uso da terra até 2025; dinâmica de uso do solo em Canaã | MapBiomas Cobertura e Uso da Terra, Coleção 11: estatísticas de área por classe, tabelas baixáveis e mapas anuais GeoTIFF de 30 m; usar primeiro o agregado municipal publicado e só processar raster se o indicador exigir. [Produto e série 1985–2025](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-30m/cobertura/) · [Downloads](https://brasil.mapbiomas.org/downloads/) | B; processamento automatizável por edição e classe | A série da Coleção 11 começa em 1985, logo 1983 é lacuna desta fonte. Definir quais códigos/classes formam “floresta” e “área urbana”, denominador da porcentagem e edição do limite municipal. A cada coleção, congelar a versão, pois revisões podem alterar retrospectivamente a série. PRODES/TerraBrasilis é uma referência de desmatamento, não substituto direto de mapa completo de uso da terra. |
| Emissão de CO₂/CO₂e municipal | SEEG publica CSV por município e planilhas por setor; baixar a coleção/edição e a nota metodológica. [Dados municipais SEEG](https://seeg.eco.br/dados/) · [Metodologia](https://seeg.eco.br/metodologia/) | B; ingestão por edição | Série municipal começa em 2000 e valores podem ser alocados por proxies quando a fonte não oferece desagregação municipal. Mostrar gás/métrica (CO₂, CO₂e GWP/GTP), setor, edição e caráter estimado. Não chamar estimativa alocada de medição direta local. |
| Saneamento do Censo 2022 | IBGE/SIDRA ou arquivos/tabelas do Censo; SNIS/SINISA apenas como fonte administrativa distinta para indicadores posteriores | A/B conforme tabela | Não criar série contínua misturando resposta censitária domiciliar e registro administrativo dos prestadores. Definir cobertura, unidade e denominador. |

### Finanças públicas e índices

| Indicadores da oficina | Fonte e forma de obtenção | Nível e automação | Tratamento e limitações |
|---|---|---|---|
| Despesa per capita 2013–2024 por função (educação, saúde, saneamento, segurança, agricultura e urbanismo) e despesa por função | API SICONFI/Tesouro para demonstrações disponíveis; conferir as rotas e campos na documentação oficial. [Documentação SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/) | A, sujeito a teste de consulta, paginação e versão da API | Fixar demonstrativo, estágio da despesa (empenhada/liquidada/paga), função/subfunção, ente e exercício. Não somar versões retificadas como registros distintos. O gasto per capita é derivado: registrar ano e série populacional do denominador. Publicar nominal e, se necessário, valor real deflacionado com índice explícito. |
| Repasse/participação do ICMS em 2023; composição das receitas correntes de Canaã; impostos como % da receita corrente e do PIB | FAPESPA/anuário tem tabelas HTML municipais de repasses de ICMS, receitas e impostos; SICONFI e IBGE podem ser usados para reproduzir/validar componentes. [Tabela de repasse ICMS 2019–2023](https://fapespa.pa.gov.br/sistemas/anuario2024/tabelas/economia/2.6-financas-publicas/tab-2.6.1-repasse-de-icms-dos-municipios-do-para-2019-a-2023.htm) · [Tabela de receitas correntes](https://fapespa.pa.gov.br/sistemas/anuario2024/tabelas/economia/2.6-financas-publicas/tab-2.6.6-receitas-correntes-para-e-municipios-2019-a-2023.htm) | B para HTML estável; A para partes consultadas no SICONFI | Para imposto/PIB dividir valores do mesmo exercício e manter ambos nominais; para imposto/receita corrente definir os componentes tributários incluídos. A tabela FAPESPA de receita consultada informa valores nominais e pode ter campos ausentes quando município não enviou dados à STN na extração. FAPESPA é uma consolidação útil, mas arquivar a fonte e conferir totais. |
| Barômetro da Sustentabilidade 2024 | Publicação, planilha ou material metodológico da [FAPESPA](https://www.fapespa.pa.gov.br/barometro-da-sustentabilidade/) | B/C; integração por edição, transcrição auditada quando PDF | Índice composto. Registrar fórmula, edição, componentes, valores ausentes e fonte dos indicadores. Não recalcular/atualizar o índice sem reproduzir o método. |
| IDSC-BR | [Site/relatórios do Instituto Cidades Sustentáveis](https://idsc.cidadessustentaveis.org.br/) e arquivos de dados expressamente disponibilizados pelo provedor | C/D; API pública documentada não identificada | Capturar edição, município, indicador e licença. Se não existir download em lote/licença clara, solicitar dataset ou publicar extração manual citada; não depender de endpoint interno do site. |
| Ranking de Competitividade dos Municípios 2025 | Relatório técnico e planilha oficial CLP da edição | B; baixar workbook versionado | Confirmar presença dos municípios na edição e universo comparado. Guardar planilha, glossário e edição; alterações metodológicas limitam comparação direta entre anos. [Materiais CLP 2025](https://conteudo.clp.org.br/relatorios-tecnicos-2025) |
| Receita per capita e IDSC; grupos AA, BB, BA e AB (IPEA, TD 3146/2025) | Texto para Discussão e dados de origem. A publicação é fonte de método/conclusão, não uma API. [IPEA TD 3146](https://doi.org/10.38116/td3146-port) | C; análise reproduzível se fontes e cortes estiverem disponíveis | Guardar ano de referência, definição de receita alta/baixa e IDSC alto/baixo, cortes, deflator e regra de classificação. Marcar como análise derivada, não indicador oficial contínuo. |

## Bypass seguro quando não houver API

O bypass proposto é uma alternativa documentada ao endpoint, não uma evasão de controles:

1. Procurar primeiro dataset/CSV/XLSX/TXT/GeoTIFF ou arquivo histórico oficial; usar tabela HTML oficial se tiver URL e estrutura relativamente estáveis.
2. Se houver painel, usar o comando oficial de exportação. Guardar filtros aplicados e a data de extração junto ao arquivo. Para CODEC/SEGUP, exportar consultas por ano e preservar os filtros; no painel de frota DETRAN, verificar se o relatório municipal pode ser baixado e extraído sem contornar controles. Para CECAD, usar as consultas agregadas públicas e não o módulo restrito.
3. Se só houver PDF, salvar o original, extrair tabelas para área de revisão, conferir amostras e totais contra o documento e registrar página/tabela. A transcrição não deve ir direto para produção.
4. Se depender de login ou cooperação institucional, solicitar credencial/acordo ou pedir uma publicação agregada. Não automatizar login, acessar dados identificados nem imitar chamadas privadas.
5. Se o formato mudar, falhar a validação ou os termos forem ambíguos, interromper a atualização e manter a última edição validada com aviso de data; nunca substituir por dado incompleto sem sinalizar.

Para arquivos grandes, baixar somente a edição necessária, preservar o arquivo bruto, verificar checksum, processar por partições de período/município e projetar apenas colunas necessárias. A ANM publica CSVs de arrecadação, distribuição e autuação; o diretório tem arquivos com centenas de megabytes e a própria documentação descreve campos como ano/mês, município, substância, quantidade e valor recolhido. A recomendação é importar/filtrar no servidor, não baixar a base integral no navegador. [Diretório CFEM da ANM](https://dadosabertos.anm.gov.br/CFEM/) · [Dicionário de Dados CFEM](https://app.anm.gov.br/dadosabertos/arrecadacao/Dicion%C3%A1rio%20de%20Dados%20-%20CFEM.pdf)

## Contrato de dados para o front-end

O front-end deve consultar apenas uma API própria do observatório, alimentada por observações validadas. A fonte externa não deve ser chamada diretamente pelo navegador; assim ficam centralizados cache, transformação, licenças, credenciais, controle de versão e tratamento de falhas.

Campos mínimos de uma observação publicada:

| Campo | Uso |
|---|---|
| `indicator_id` e `definition` | Identificar exatamente a medida e sua fórmula/universo. |
| `geo_id`, `geo_name`, `geo_level` | Código IBGE, nome e nível territorial; guardar a composição da RI usada. |
| `reference_period` e `frequency` | Período do fenômeno e frequência da série, separados da data de coleta. |
| `value`, `unit`, `status` | Valor/unidade e situação: validado, provisório, não divulgado, ausente ou não aplicável. Zero não substitui ausência. |
| `source`, `source_url`, `source_locator` | Produtor, link e tabela/arquivo/consulta/página específica que permite refazer a busca. |
| `source_edition`, `collected_at`, `pipeline_version` | Edição original, instante de ingestão e transformação aplicada. |
| `methodology`, `limitations`, `license` | Fórmula, cobertura/defasagem/ruptura conhecida e regra de reutilização. |

Exemplo conceitual de série:

```json
{
  "indicator_id": "cfem.distribuicao.municipio",
  "geo_id": "codigo-ibge-do-municipio",
  "reference_period": "2025-12",
  "value": 0,
  "unit": "BRL",
  "status": "validated",
  "source": "ANM",
  "source_url": "https://dadosabertos.anm.gov.br/CFEM/",
  "source_edition": "arquivo capturado em 2026-10-01",
  "collected_at": "2026-10-01T00:00:00Z",
  "methodology": "Valor de distribuição por município conforme dicionário da ANM",
  "limitations": ["Distribuição não equivale à arrecadação no município de origem"],
  "license": "validar termos do conjunto antes da redistribuição"
}
```

O zero do exemplo é ilustrativo de formato; uma publicação real precisa vir de uma observação validada, e um zero real não deve ser inventado para representar dado ausente. A API deve ainda expor filtros e exportações CSV/JSON com os metadados junto dos valores. Para o assistente de IA, a regra é: consultar somente a camada publicada; responder com fonte, período e limitações; se não houver observação compatível, dizer que não há dado validado e explicar a lacuna.

## Ordem recomendada para prova de consumo

1. **Primeiro lote de menor risco:** IBGE (uma população e uma tabela censitária), ANM (arrecadação versus distribuição em separado), SICONFI (uma função fiscal), MapBiomas (uma estatística municipal por classe) e SEEG (um setor/ano).
2. **Segundo lote com transformações:** RAIS/CAGED agregado, PIB/renda e percentuais derivados, incluindo denominadores e comparabilidade.
3. **Terceiro lote assistido:** CECAD público, CODEC/SEGUP (consultas anuais), relatório do painel DETRAN, FAPESPA HTML/PDF, INEP IDEB e CLP/IDSC/Barômetro, com revisor e evidência de fonte por valor.
4. **Gates antes de prometer indicador:** confirmar cobertura e conceito da série CODEC/SEGUP de homicídio por arma de fogo desde 1989; validar formato de saída e histórico do painel DETRAN; obter os anos finais do PIB que não aparecem na tabela FAPESPA usada; verificar edição/licença das publicações FAPESPA/IDSC; validar valores ausentes e municípios na planilha CLP; decidir definição de pobreza e população denominadora; resolver a cobertura MapBiomas anterior a 1985; identificar precisamente o produto referido como “VIGIA–Belém”.

## Saída desta análise

Com os dados atuais, o que pode ser prometido com maior segurança é: um catálogo metodológico completo; ingestão automática de APIs e arquivos oficiais aprovados; séries selecionadas e versionadas; exportação pelo backend próprio; e indicação explícita de lacunas. Não se deve prometer cobertura integral, atualização em tempo real, API pública de cada produtor, ou automação sem revisão para todos os indicadores.

O próximo produto técnico, após aprovação deste mapa, é uma planilha de inventário operacional com uma linha por indicador e campos para responsável, URL/tabela exata, regra de coleta, frequência, teste de qualidade, licença e estado de homologação. A implementação permanece fora deste documento.

## Documentos-base relacionados

- [Relatório de pesquisa e viabilidade do Observatório CFEM](LEIA-ME.md) — síntese anterior de fontes, arquitetura de ingestão, riscos e escopo.
- [Modelo OpenAPI genérico do workflow](../../../api/openapi.yaml) — referência estrutural para discutir contrato HTTP; ainda não está adaptado ao CFEM.
- [ADRs do workflow](../../../adr/) — registro genérico de decisões; não foram alterados nesta análise.
