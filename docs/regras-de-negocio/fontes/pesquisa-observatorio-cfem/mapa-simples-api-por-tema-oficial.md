# Mapa simples: há API para cada tema do Observatório?

**Objetivo:** apresentar, de forma direta, como os dados dos temas oficiais da oficina podem ser obtidos. Este documento é um resumo de consumo de dados, não uma especificação da plataforma.

**Critério da coluna “Tem API?”** — “Sim” significa que foi identificada uma API oficial documentada adequada ao dado citado. “Não” significa que não foi identificada API pública documentada para aquele dado específico. A fonte ainda pode oferecer arquivo CSV/XLSX/TXT, tabela, painel ou exportação. Isso pode permitir automação, mas não transforma o método em API.

**Consulta às fontes:** 2 de outubro de 2026. A disponibilidade pode mudar; revalidar antes de iniciar integrações.

## Resultado em uma frase

Há APIs oficiais úteis principalmente para dados do IBGE e do SICONFI. Para CFEM, trabalho, preços de commodities, CadÚnico agregado, FAPESPA, segurança, uso da terra, emissões e índices, o caminho identificado é arquivo, tabela ou exportação — não uma API pública documentada para os indicadores listados.

## Tema central do Observatório: CFEM

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| Arrecadação, distribuição e autuações da CFEM | **NÃO — ANM** | Baixar os arquivos CSV oficiais de arrecadação, distribuição e autuações. São arquivos grandes; armazenar e processar no backend, não no navegador. Distinguir município arrecadador de município recebedor. [Dados abertos CFEM](https://dadosabertos.anm.gov.br/CFEM/) |

## 1. Dinâmica populacional

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| População de Canaã dos Carajás e Parauapebas comparada à Região de Integração Carajás; evolução municipal 1980–2022 ou mais recente; características da população da região em 2022 | **SIM — IBGE** | Consultar API de Agregados/SIDRA e API de Localidades. Para tabelas não cobertas, baixar a tabela oficial. Fixar códigos IBGE e composição da região. [Documentação das APIs IBGE](https://servicodados.ibge.gov.br/api/docs/) |

## 2. Economia e mercado de trabalho

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| PIB municipal (2010–2023); PIB per capita e participação da Região de Integração Carajás; produção agrícola | **SIM — IBGE** | Usar API SIDRA/Agregados quando tabela e variável estiverem disponíveis. Produção agrícola deve vir da tabela apropriada da PAM. Alguns arquivos de apoio podem exigir download. [Documentação IBGE](https://servicodados.ibge.gov.br/api/docs/) |
| Preço do minério de ferro (1985–2025) e do cobre (2000–2026) em USD | **NÃO — para a série Pink Sheet usada** | Baixar a planilha mensal oficial do World Bank Commodity Markets e processar o histórico; registrar série, unidade e mês da edição. Não é preço local de venda. [World Bank Commodity Markets](https://www.worldbank.org/en/research/commodity-markets) |
| Evolução do emprego CAGED; emprego formal como proporção da população; emprego por setor na RI em 2025; remuneração média por sexo em 2023; vínculos por escolaridade; emprego por gênero em Canaã em 2022 | **NÃO — MTE/PDET** | Baixar microdados públicos RAIS/CAGED em TXT e agregar, ou usar consulta/exportação PDET quando houver credencial autorizada. CAGED mede fluxo; RAIS, estoque anual. [Microdados RAIS e CAGED](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged) |
| Rendimento domiciliar mensal per capita; nível de instrução por sexo | **SIM — IBGE, para tabelas disponíveis** | Consultar SIDRA/API de Agregados. Confirmar se a tabela oferece o município, período e cruzamentos desejados; quando não oferecer, usar arquivo oficial. Não interpolar anos sem dado como se fossem observações. [Documentação IBGE](https://servicodados.ibge.gov.br/api/docs/) |

## 3. Sociedade

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| IDEB 2023 e distorção idade-série 2023 | **NÃO — INEP, para os arquivos consultados** | Baixar planilhas/arquivos oficiais por edição e validar município, etapa e rede. Resultado não divulgado não significa valor zero. [Resultados do IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) |
| Indicador de saúde 2023 | **NÃO — para o indicador FAPESPA ainda não especificado** | Primeiro identificar nome, fórmula e fonte original. A FAPESPA publica perfis/tabelas; para indicadores do SUS, consultar TABNET ou arquivos de dados. A existência de serviços de integração em saúde não significa API pública apropriada para este indicador agregado. [FAPESPA](https://www.fapespa.pa.gov.br/estatistica-municipal/) · [DATASUS/TABNET](https://datasus.saude.gov.br/informacoes-de-saude-tabnet/) |
| Pobreza e percentual de famílias pobres, data-base julho de 2026 | **NÃO — CECAD público agregado** | Fazer consulta agregada no CECAD e guardar filtro, definição e data-base. Não automatizar acesso restrito nem usar dados identificados. Não foi identificada API pública documentada para essa consulta agregada. [CECAD](https://cecad.cidadania.gov.br/) |
| Taxa de homicídio por arma de fogo por 100 mil habitantes (1989–2022); violência 2023 | **NÃO — SEGUP/CODEC e FAPESPA** | Consultar e exportar a tabela pública CODEC/SEGUP por ano; usar FAPESPA como tabela de apoio. A série completa desde 1989 ainda precisa de confirmação. DATASUS/SIM é alternativa com conceito diferente, que não deve ser misturado sem nota metodológica. [CODEC/SEGUP](https://codec.segup.pa.gov.br/) · [FAPESPA](https://www.fapespa.pa.gov.br/estatistica-municipal/) |
| Número de veículos em 2023 | **NÃO — DETRAN-PA/FAPESPA** | Consultar o relatório municipal no painel de frota do DETRAN-PA e confirmar se permite baixar os valores; usar FAPESPA como conferência. Não foi identificada API pública documentada do painel. [Painel de frota DETRAN-PA](https://dashboard-frota.detran.pa.gov.br/) |
| Infraestrutura do Censo 2022; população residente em favelas/comunidades urbanas; características do entorno; população por situação do domicílio | **SIM — IBGE, para tabelas disponíveis** | Consultar SIDRA/API de Agregados; usar arquivos oficiais nos recortes não cobertos. Verificar se cada variável pode ser agregada ao município e observar mudanças de nomenclatura entre censos. [Documentação IBGE](https://servicodados.ibge.gov.br/api/docs/) |

## 4. Meio ambiente e saneamento

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| Área urbana/uso do solo (1983–2024); cobertura florestal em 1985 e 2023; percentual de floresta; uso da terra até 2025; dinâmica de uso do solo em Canaã | **NÃO — MapBiomas, para a coleção consultada** | Baixar estatísticas municipais ou mapas GeoTIFF da Coleção 11 e processar por município/classe. A série consultada cobre 1985–2025; 1983 não está coberto por essa coleção. [Mapas para download](https://brasil.mapbiomas.org/downloads/mapas-para-download-geotiff/) |
| Emissões de CO₂/CO₂e | **NÃO — SEEG, para os dados municipais consultados** | Baixar planilhas/CSV municipais por edição e setor. Registrar método, edição, gás e possíveis estimativas por proxy. [Dados SEEG](https://seeg.eco.br/dados/) |
| Saneamento do Censo 2022 | **SIM — IBGE, para tabelas disponíveis** | Consultar API SIDRA/Agregados ou baixar tabela oficial. Não misturar automaticamente dados censitários com registros administrativos de prestadores. [Documentação IBGE](https://servicodados.ibge.gov.br/api/docs/) |

## 5. Finanças públicas e indicadores de síntese

| Tema e itens da oficina | Tem API? | Caminho direto para obter os dados |
|---|---|---|
| Despesa per capita por função (educação, saúde, saneamento, segurança, agricultura e urbanismo), 2013–2024; despesa por função | **SIM — SICONFI/Tesouro** | Consultar API de Dados Abertos do SICONFI. Definir estágio da despesa e denominador populacional; tratar declarações retificadas. [Documentação e API SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/) |
| Repasse/participação do ICMS em 2023; composição das receitas correntes de Canaã; impostos como proporção do PIB e da receita corrente | **SIM — SICONFI e IBGE, para componentes disponíveis** | Consumir os componentes fiscais pela API SICONFI e os componentes do PIB pela API IBGE. Como alternativa de conferência, a FAPESPA publica tabelas HTML/arquivos, que não são API. Calcular proporções só depois de fixar exercício, componentes e unidades comparáveis. [API SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/) · [API IBGE](https://servicodados.ibge.gov.br/api/docs/) · [FAPESPA](https://www.fapespa.pa.gov.br/estatistica-municipal/) |
| Barômetro da Sustentabilidade 2024 | **NÃO — FAPESPA** | Baixar a publicação ou planilha da edição, guardar metodologia e conferir transcrição. [Barômetro FAPESPA](https://www.fapespa.pa.gov.br/barometro-da-sustentabilidade/) |
| IDSC-BR | **NÃO — para API pública documentada identificada** | Usar arquivos/relatórios expressamente publicados pelo provedor; conferir edição e licença antes de republicar. [IDSC](https://idsc.cidadessustentaveis.org.br/) |
| Ranking de Competitividade dos Municípios 2025 | **NÃO — CLP** | Baixar a planilha e o relatório da edição; confirmar presença de cada município e preservar o arquivo original. [Materiais CLP 2025](https://conteudo.clp.org.br/relatorios-tecnicos-2025) |
| Receita per capita e IDSC; classificações AA, BB, BA e AB (IPEA, Texto para Discussão 3146/2025) | **NÃO — publicação/estudo** | Usar o estudo e as bases citadas como referência metodológica; reproduzir o cálculo somente se houver dados, definições e pontos de corte disponíveis. [IPEA, TD 3146](https://doi.org/10.38116/td3146-port) |

## Resumo para apresentação

| Resultado | Síntese |
|---|---|
| **Com API oficial identificada** | IBGE (para tabelas e variáveis disponíveis) e SICONFI (para declarações e componentes cobertos). |
| **Sem API pública documentada para o dado específico** | ANM/CFEM, MTE/PDET, World Bank Pink Sheet, INEP, FAPESPA, CECAD agregado, SEGUP/CODEC, DETRAN-PA, MapBiomas, SEEG, CLP, IDSC, Barômetro e estudo IPEA. |
| **O que fazer quando não há API** | Preferir arquivo oficial; depois tabela/exportação oficial; por último, extração assistida de PDF com revisão. Guardar a fonte, edição, data de coleta e filtros. Nunca contornar login ou controle de acesso. |

**Importante:** “Não” nesta tabela não quer dizer “dado indisponível”. Quer dizer apenas que o consumo identificado é por arquivo, consulta, tabela ou exportação — e não por API pública documentada. Alguns itens ainda dependem de definição metodológica ou confirmação de cobertura antes de serem publicados.
