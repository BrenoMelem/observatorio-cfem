# Glossário

Termos e siglas usados nesta documentação. Os termos de domínio vêm do REG (§Glossário) e do BT (§Glossário); os termos próprios da documentação estão na segunda tabela. Legenda de status e siglas das fontes: [README](README.md).

## Termos próprios desta documentação

| Termo | Significado |
| --- | --- |
| status da regra | Situação da regra nesta documentação: DECIDIDA, PROPOSTA ou EM ABERTO. Não se confunde com a natureza do valor nem com o estado de validação |
| DECIDIDA | Regra que vem de REG, BT, L19 ou R15, ou de decisão do mantenedor registrada em 24/10/2026 |
| PROPOSTA | Regra deduzida, vinda só de ANA, MAPA, LEIA, PLN ou do código, sem decisão registrada |
| EM ABERTO | Ponto sem decisão, ou com fontes em conflito; todos constam em [pendencias.md](pendencias.md) |
| DM | Decisão do mantenedor, de 24/10/2026, dada nas respostas da Fase 1 |
| observação | Um valor de um indicador para um município e um período, com unidade, natureza, estado de validação, fonte e proveniência |
| natureza do valor | O que o valor é: informado, zero real, ausente, não divulgado ou não aplicável (RN-MOD-06) |
| estado de validação | Se o valor já passou pelas validações e reconciliações: validado ou provisório (RN-MOD-07) |
| informado | Natureza do valor: a fonte informou um valor diferente de zero |
| zero real | Natureza do valor: a fonte informou explicitamente o valor zero |
| ausente | Natureza do valor: a fonte não tem o valor, ou não há linha para o município e o período. Não é zero |
| não divulgado | Natureza do valor: a fonte tem o valor, mas não o divulga. Não é zero |
| não aplicável | Natureza do valor: a medida não faz sentido para o município ou o período |
| provisório | Estado de validação de um valor publicado antes de o conjunto estar fechado ou reconciliado |
| validado | Estado de validação de um valor que passou pelas checagens e pela reconciliação exigidas |
| homologado | Dado que passou por validação e reconciliação e pode alimentar gráficos |
| lote | Conjunto de dados coletado e tratado numa execução, que é validado e publicado, ou barrado, como um todo |
| camada publicada | O conjunto de dados tratados e validados que o front-end, as exportações e o assistente consomem. Pode ser entregue como arquivos, como API própria ou como ambos (conflito 2) |
| camada tratada | Os dados já padronizados e versionados entre as fontes e o consumo |
| proveniência | Origem do dado: URL, edição da fonte, checksum, data de coleta, filtros e versão do tratamento |
| tabela de equivalência (de-para) | Tabela que liga um identificador de uma fonte (nome de município, código do TSE) ao código IBGE |
| manifesto | Descrição única de cada indicador (identificação, bloco, fonte, método, frequência, estratégia) e da lista de municípios de comparação |
| congelado | Indicador composto que entra com o valor publicado pela entidade, com citação, atualizado à mão a cada edição |
| promovível | Marca de um indicador congelado que pode virar cálculo recalculado pelo observatório |
| derivado | Indicador calculado pelo observatório a partir de outros |
| evento | Registro individual guardado com todos os campos (como a autuação), do qual a série é derivada |
| modalidade de distribuição | Tipo de repasse da CFEM na coluna de tipo de distribuição do arquivo da ANM (por exemplo, `Produtor`) |
| ensaio de custo | Estimativa do processamento de uma consulta ao BigQuery sem executá-la (dry run) |
| issue | Registro de pendência aberto quando uma validação falha |
| ano de referência | Ano a que o dado se refere, distinto da data de coleta |

## Termos de domínio

| Termo | Significado |
| --- | --- |
| agregado (SIDRA) | Tabela temática do SIDRA, identificada por número (por exemplo, 9900 = favelas) |
| AMB | Anuário Mineral Brasileiro (ANM), fonte do valor da produção mineral (VPM) |
| ANM | Agência Nacional de Mineração |
| arrecadação (CFEM) | Royalty gerado pela extração no município de origem; distinto da distribuição e da autuação |
| Atlas da Violência | Estudo do IPEA que publica a taxa de homicídio corrigida |
| autuação | Cobrança que a ANM lança por recolhimento a menor de CFEM; é acusação com valor, não dinheiro em caixa |
| `AVIOL12_THOMIC` | Código da série de taxa de homicídio no IPEADATA |
| Barômetro da Sustentabilidade | Índice de sustentabilidade da FAPESPA (metodologia Prescott-Allen) |
| Base dos Dados (BD) | Iniciativa que espelha dados públicos no BigQuery; nunca é fonte primária; o prefixo `br_` nas tabelas é dela |
| BigQuery | Banco de dados do Google onde a Base dos Dados hospeda as tabelas; exige credencial |
| CadÚnico / CECAD 2.0 | Cadastro Único e seu portal (MDS), fonte de pobreza, sem API |
| CAGED / Novo CAGED | Cadastro Geral de Empregados e Desempregados: admissões e demissões formais (fluxo) |
| Censo Escolar | Levantamento anual do INEP sobre escolas, matrículas, docentes e infraestrutura escolar |
| CFEM | Compensação Financeira pela Exploração de Recursos Minerais, o royalty da mineração |
| CLP | Centro de Liderança Pública; publica o ranking de competitividade |
| CNAE | Classificação Nacional de Atividades Econômicas |
| CODEC/SEGUP-PA | Estatísticas de segurança pública do Pará |
| Coleção 11 | Versão mais recente do MapBiomas (1985–2025) |
| DATASUS | Órgão de dados do Ministério da Saúde; mantém o SIM |
| DCA / Anexo I-E | Declaração de Contas Anuais do SICONFI; o Anexo I-E traz a despesa por função |
| DETRAN-PA | Departamento de Trânsito do Pará; alternativa estadual para a frota |
| distribuição (CFEM) | Parcela da CFEM repassada a cada município (CFEM recebida), distinta da arrecadada na origem |
| EECU | Earth Engine Compute Unit, cota de processamento do GEE |
| FAPESPA | Órgão estatístico do Pará; define a RI Carajás |
| fato gerador | Ano em que o débito de CFEM se originou (contraste com lavratura) |
| FINBRA | Base histórica de finanças municipais do Tesouro, organizada no IPEADATA |
| FRED | Federal Reserve Economic Data, API das séries de commodities |
| GEE (Google Earth Engine) | Plataforma do Google para dados geoespaciais; rota do MapBiomas |
| `id_ente` | Parâmetro do SICONFI que recebe o código IBGE do município |
| IDEB | Índice de Desenvolvimento da Educação Básica |
| IDH-M | Índice de Desenvolvimento Humano Municipal |
| IDSC | Índice de Desenvolvimento Sustentável das Cidades |
| INEP | Instituto Nacional de Estudos e Pesquisas Educacionais |
| IPEA | Instituto de Pesquisa Econômica Aplicada |
| IPEADATA | Base de séries do IPEA; o ambiente Regional traz dados municipais |
| lavratura | Ano em que a ANM emitiu a autuação (contraste com fato gerador) |
| MapBiomas | Mapeamento anual de uso e cobertura do solo do Brasil |
| N6 | Parâmetro do SIDRA que recorta o resultado a nível municipal |
| Pink Sheet | Planilha mensal de preços de commodities do World Bank (só download) |
| PySUS | Biblioteca que baixa e converte microdados do DATASUS, citada pelo REG como rota de saúde |
| RAIS | Relação Anual de Informações Sociais: vínculos formais (estoque), com quebras por setor, sexo e escolaridade |
| RI Carajás | Região de Integração Carajás: 12 municípios do Pará |
| SEEG | Sistema de Estimativas de Emissões de Gases de Efeito Estufa |
| Senatran | Secretaria Nacional de Trânsito; frota de veículos |
| SICONFI | Sistema de Informações Contábeis e Fiscais do Setor Público |
| SIDRA | Sistema IBGE de Recuperação Automática; API de agregados do IBGE |
| SIM | Sistema de Informações sobre Mortalidade (DATASUS) |
| TD 3146 | Texto para Discussão 3146 do IPEA: relação receita per capita × IDSC |
| TSE | Tribunal Superior Eleitoral; fonte do número de eleitores |
| VAB | Valor Adicionado Bruto, componente setorial do PIB |
| VPM | Valor da Produção Mineral, base da CFEM, publicado pela ANM no AMB; só existe por UF |
