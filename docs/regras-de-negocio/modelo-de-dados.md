# Modelo de dados

Regras sobre o que é uma observação, como o valor se classifica (natureza do valor e estado de validação), como a proveniência acompanha o dado e quais cuidados valem ao comparar e derivar valores. Legenda de status e siglas das fontes: [README](README.md).

Atenção a duas coisas que não se misturam:
- o **status da regra** (DECIDIDA, PROPOSTA, EM ABERTO) descreve a regra desta documentação;
- a **natureza do valor** e o **estado de validação** descrevem um valor publicado (RN-MOD-06 e RN-MOD-07).

## Requisitos semânticos e equivalência entre os dois esquemas

As fontes descrevem dois esquemas diferentes (conflito 1 em [pendencias.md](pendencias.md)). Esta documentação fixa os requisitos semânticos (RN-MOD-02) e deixa os nomes de campo **EM ABERTO** (RN-MOD-03). A tabela abaixo mostra a equivalência entre as duas versões.

| Requisito semântico | Esquema de DECISÕES (04/10/2026, última edição 20/10/2026) | Esquema de CONSUMO (02/10/2026) e de VAL-15/10 §Marco 1 (15/10/2026) | Observação |
| --- | --- | --- | --- |
| Identificação do indicador | `indicador` | `indicator_id`, `definition` (CONSUMO) | CONSUMO exige também a definição (fórmula e universo) |
| Município (código) | `municipio_id` | `geo_id` | Nos dois casos o código IBGE de 7 dígitos |
| Município (nome) | `municipio_nome` | `geo_name` (CONSUMO) | VAL-15/10 §Marco 1 cita só `geo_id` |
| Nível territorial | sem campo | `geo_level` (CONSUMO) | Município ou RI |
| Período do fenômeno | `ano`, `mes` (opcional) | `reference_period`, `frequency` (CONSUMO) | O mês entra no esquema comum, vazio nos anuais (RN-MOD-04) |
| Valor | `valor` | `value` | |
| Unidade | `unidade` | `unit` | |
| Natureza e validação do valor | sem campo | `status` (lista única: validado, provisório, não divulgado, ausente, não aplicável) | Decidido nesta documentação em dois eixos (RN-MOD-06, RN-MOD-07) |
| Fonte | `fonte` | `source`, `source_url`, `source_locator` (CONSUMO) | CONSUMO exige também o local exato da busca |
| Edição da fonte | sem campo | `source_edition` | |
| Data de coleta | `atualizado_em` | `collected_at` | DECISÕES chama de "atualizado em" |
| Versão do pipeline | sem campo | `pipeline_version` | |
| Metodologia, limitações e licença | sem campo | `methodology`, `limitations`, `license` (CONSUMO) | |

Estado: **EM ABERTO**. Nenhum dos dois conjuntos de nomes é adotado.

### RN-MOD-01: Esquema único de saída
- **Status:** DECIDIDA
- **Regra:** Todo indicador, qualquer que seja a origem, deve ser publicado no mesmo formato de observação.
- **Motivo:** Quem consome os dados lê sempre a mesma coisa, e trocar a origem de um indicador não afeta gráfico, exportação nem assistente.
- **Exemplo:** A população por SIDRA e o PIB por SIDRA saem no mesmo formato que a CFEM da ANM.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados ("Esquema único de saída"); PLANO §Visão geral.
- **Relacionadas:** RN-MOD-02, RN-MOD-03

### RN-MOD-02: Requisitos semânticos mínimos de uma observação
- **Status:** DECIDIDA
- **Regra:** Toda observação publicada deve identificar o indicador, o município, o período do fenômeno, o valor, a unidade, a natureza do valor, o estado de validação, a fonte e a proveniência (edição da fonte, data de coleta e versão do tratamento).
- **Motivo:** Sem esses elementos o valor não pode ser conferido, comparado nem refeito.
- **Exemplo:** População estimada de 2025 de Canaã dos Carajás (1502152): 89.524 pessoas, agregado 6579, variável 9324 (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Exceções:** Os nomes de campo estão em aberto (RN-MOD-03).
- **Fonte:** DECISÕES §Arquitetura e padrões de dados; VAL-15/10 §Marco 1; DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 2).
- **Relacionadas:** RN-MOD-03, RN-MOD-06, RN-MOD-07, RN-MOD-21, RN-MOD-22

### RN-MOD-03: Nomes e campos do esquema
- **Status:** EM ABERTO
- **Regra:** Os nomes de campo, o idioma e a lista de campos da observação devem ser definidos pelo mantenedor antes da implementação do contrato.
- **Motivo:** DECISÕES e CONSUMO e VAL-15/10 definem esquemas diferentes em idioma e em campos (ver tabela acima).
- **Exemplo:** DECISÕES usa `municipio_id`; CONSUMO e VAL-15/10 usam `geo_id`.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (04/10/2026); CONSUMO §Contrato de dados para o front-end (02/10/2026); VAL-15/10 §Marco 1 (15/10/2026).
- **Relacionadas:** RN-MOD-02, RN-MOD-04, RN-ENT-02

### RN-MOD-04: Campo de mês
- **Status:** DECIDIDA
- **Regra:** O mês deve fazer parte do esquema comum de todos os indicadores, preenchido quando a fonte é mensal e vazio nos indicadores anuais.
- **Motivo:** Um esquema único evita dois formatos para consumir, e o mês é necessário para a CFEM (guardar mensal, exibir anual) e para outras séries mensais, como os preços de commodities do FRED.
- **Exemplo:** A distribuição da CFEM de maio de 2025 só pôde ser reconciliada porque o mês foi preservado. Os preços de ferro e cobre do FRED são mensais, e a população do IBGE é anual, com o mês vazio.
- **Exceções:** O nome do campo continua em aberto junto com o resto do esquema (RN-MOD-03).
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026; DECISÕES §Arquitetura e padrões de dados, §Pré-requisitos e pendências; VAL-15/10 §Marco 2; LAB-19/10 §7 (Próximos passos, item 2).
- **Relacionadas:** RN-MOD-03, RN-MOD-05, RN-CFE-04

### RN-MOD-05: Granularidade mais fina da fonte
- **Status:** DECIDIDA
- **Regra:** O dado deve ser guardado na granularidade mais fina que a fonte oferece e só deve ser agregado na saída.
- **Motivo:** Permite reagregar e reconciliar sem nova coleta, e evita perder o detalhe que a validação precisa.
- **Exemplo:** A CFEM é guardada por mês e exibida por ano; o eleitorado guarda total e gênero.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados; BLOCOS §Bloco 3.
- **Relacionadas:** RN-CFE-04, RN-MOD-23

### RN-MOD-06: Natureza do valor
- **Status:** DECIDIDA
- **Regra:** Todo valor publicado deve ter uma natureza, e só pode ser uma destas: informado, zero real, ausente, não divulgado ou não aplicável.
- **Motivo:** Ausência, não divulgação e zero são situações diferentes e uma não pode ser lida como outra.

  | Natureza | Significado |
  | --- | --- |
  | informado | a fonte informou um valor diferente de zero |
  | zero real | a fonte informou explicitamente o valor zero |
  | ausente | a fonte não tem o valor, ou não há linha para o município e o período |
  | não divulgado | a fonte tem o valor, mas não o divulga (por exemplo, participação insuficiente) |
  | não aplicável | a medida não faz sentido para o município ou o período |

- **Exemplo:** A nota do IDEB 2023 de um município sem divulgação por participação insuficiente é "não divulgado", não zero. Julho de 2025 sem nenhuma linha no arquivo de distribuição da CFEM é "ausente", não zero.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 3); VAL-15/10 §Marco 1; CONSUMO §Sociedade, §Contrato de dados para o front-end.
- **Relacionadas:** RN-MOD-07, RN-MOD-08, RN-MOD-09, RN-MOD-10, RN-MOD-11

### RN-MOD-07: Estado de validação
- **Status:** DECIDIDA
- **Regra:** Todo valor publicado deve ter, separado da natureza, um estado de validação: validado ou provisório.
- **Motivo:** O estado de validação diz se o número já passou pelas checagens e reconciliações; a natureza diz o que o valor é. Juntar os dois numa lista única esconderia um deles.
- **Exemplo:** Os meses de 2025 já presentes no arquivo de distribuição são publicados como "provisório" até o ano fechar com os 12 meses (RN-CFE-06).
- **Exceções:** O estado de validação não se confunde com o status da regra desta documentação.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (respostas às perguntas 3 e 5); VAL-15/10 §Resposta 3 ("estado de validação").
- **Relacionadas:** RN-MOD-06, RN-VPU-10, RN-CFE-06

### RN-MOD-08: Ausência não é zero
- **Status:** DECIDIDA
- **Regra:** Um valor ausente não deve ser publicado, somado nem exibido como zero.
- **Motivo:** Zero afirma um fato; a ausência apenas informa que não se sabe. Esconder a lacuna como zero distorce totais e comparações.
- **Exemplo:** O arquivo de distribuição da CFEM não tem julho de 2025, embora a ANM tenha publicado repasse de R$ 478.839.591,45 naquele mês aos estados e municípios produtores (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivo da ANM e notícia da ANM).
- **Fonte:** VAL-15/10 §Marco 1, §Resposta 3, §Rodada adicional; CONSUMO §Contrato de dados para o front-end.
- **Relacionadas:** RN-MOD-06, RN-MOD-10, RN-CFE-05

### RN-MOD-09: Não divulgado não é zero
- **Status:** DECIDIDA
- **Regra:** Um resultado não divulgado pela fonte não deve ser publicado como zero, e o contrato deve distinguir ausência, não divulgação e zero.
- **Motivo:** A fonte pode ter o dado e escolher não divulgá-lo; tratá-lo como zero inverte o sentido.
- **Exemplo:** O INEP não divulga a nota municipal do IDEB 2023 em certos casos de participação insuficiente.
- **Fonte:** VAL-15/10 §Marco 1; MAPA-TEMAS §Sociedade (IDEB); CONSUMO §Sociedade.
- **Relacionadas:** RN-MOD-06, RN-MOD-12

### RN-MOD-10: Ausência de linha municipal não é zero
- **Status:** DECIDIDA
- **Regra:** Quando um município não tem linha no arquivo da fonte, a observação deve ser "ausente" e não deve ser convertida em zero.
- **Motivo:** A falta de linha pode ser lacuna da extração, falta de repasse, ou município sem a atividade; só a investigação diz qual.
- **Exemplo:** São Domingos do Araguaia (1507151) não teve linha no arquivo de arrecadação 2022–2026 nem no de distribuição 2007–2026; 11 dos 12 municípios tiveram linha (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Matriz operacional (CFEM autuações), §Rodada adicional; CONSUMO §Validação complementar de 15/10/2026.
- **Relacionadas:** RN-MOD-06, RN-CFE-09

### RN-MOD-11: Valor nulo só para ausente e não divulgado
- **Status:** DECIDIDA
- **Regra:** A checagem de "valor não nulo" deve valer para observações informadas; a ausência e a não divulgação devem ser registradas pela natureza do valor, e não por um valor nulo sem classificação.
- **Motivo:** Resolve a tensão entre a checagem "valor não nulo" de DECISÕES e a existência de valores ausentes (conflito 11).
- **Exemplo:** Um mês sem repasse conhecido é "ausente" e não passa como valor nulo desconhecido.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 3); DECISÕES §Arquitetura e padrões de dados (Validação antes de publicar).
- **Relacionadas:** RN-MOD-06, RN-VPU-02

### RN-MOD-12: Preservar o motivo da não divulgação
- **Status:** PROPOSTA
- **Regra:** Quando a fonte explicar por que não divulga um valor, o motivo, a etapa, a rede e a edição devem ser preservados com a observação.
- **Motivo:** O motivo muda a leitura: insuficiência de participação é diferente de dado inexistente.
- **Exemplo:** IDEB 2023 de um município sem nota municipal por participação insuficiente.
- **Fonte:** CONSUMO §Sociedade (IDEB). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-MOD-09

### RN-MOD-13: Não misturar Censo e estimativa
- **Status:** DECIDIDA
- **Regra:** Valores do Censo e estimativas anuais de população não devem ser combinados numa mesma série sem identificar a origem de cada ponto e a quebra metodológica.
- **Motivo:** Os dois têm métodos diferentes e a mistura cria saltos que parecem fenômeno.
- **Exemplo:** A estimativa de 2025 do agregado 6579 (variável 9324) não se mistura com o Censo 2022.
- **Fonte:** VAL-15/10 §Matriz operacional (População estimada 2025); LAB-19/10 §4 (IBGE SIDRA); CONSUMO §Dinâmica populacional.
- **Relacionadas:** RN-MOD-14, RN-TER-10

### RN-MOD-14: Não misturar projeção
- **Status:** PROPOSTA
- **Regra:** Projeções de população não devem ser combinadas com Censo ou estimativa sem identificar a série e a quebra metodológica.
- **Motivo:** É a mesma razão da regra anterior, estendida às projeções.
- **Exemplo:** Uma projeção municipal não deve completar a série 1980–2022 sem marcação.
- **Fonte:** CONSUMO §Dinâmica populacional. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-MOD-13

### RN-MOD-15: Não interpolar anos sem dado
- **Status:** PROPOSTA
- **Regra:** Anos sem observação não devem ser preenchidos por interpolação nem apresentados como se fossem observados.
- **Motivo:** O valor interpolado parece dado oficial e não é.
- **Exemplo:** Rendimento domiciliar per capita só tem pontos nos anos censitários.
- **Fonte:** MAPA-TEMAS §Economia e mercado de trabalho; CONSUMO §Economia e mercado de trabalho.
- **Relacionadas:** RN-MOD-08, RN-MOD-13

### RN-MOD-16: Fluxo e estoque não se somam
- **Status:** PROPOSTA
- **Regra:** Medidas de fluxo (admissões e desligamentos do CAGED) e de estoque (vínculos da RAIS) não devem ser somadas nem tratadas como a mesma medida.
- **Motivo:** O fluxo mede movimento num período e o estoque mede o total num ponto no tempo.
- **Exemplo:** O saldo do CAGED (ADMISNC − DESLIGNC) não substitui os vínculos da RAIS.
- **Fonte:** CONSUMO §Economia e mercado de trabalho; VAL-15/10 §Matriz operacional (RAIS, CAGED, emprego: "validar fluxo versus estoque").
- **Relacionadas:** RN-IND-07

### RN-MOD-17: Razões registram numerador, denominador e ano
- **Status:** PROPOSTA
- **Regra:** Todo indicador derivado como razão deve registrar o numerador, o denominador e o ano de cada um, e não deve usar denominadores de anos diferentes ao comparar territórios.
- **Motivo:** Razões com denominadores de anos distintos não são comparáveis e não são reproduzíveis.
- **Exemplo:** PIB per capita da RI e de Canaã deve usar a população do mesmo ano para os dois.
- **Fonte:** CONSUMO §Economia e mercado de trabalho, §Finanças públicas e índices. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-MOD-18, RN-IND-09, RN-IND-10

### RN-MOD-18: Razão regional como soma sobre soma
- **Status:** PROPOSTA
- **Regra:** A razão da RI deve ser calculada somando os numeradores e somando os denominadores dos 12 municípios do mesmo ano, e não pela média das razões municipais.
- **Motivo:** A média das razões dá o mesmo peso a municípios de tamanhos muito diferentes.
- **Exemplo:** Despesa per capita da RI = soma da despesa dos 12 municípios ÷ soma das populações dos 12.
- **Fonte:** Dedução, por coerência com DECISÕES §Municípios da RI Carajás e RN-MOD-17. Nenhuma fonte fixa essa fórmula.
- **Relacionadas:** RN-TER-02, RN-MOD-17

### RN-MOD-19: Preço internacional não é atribuído a município
- **Status:** DECIDIDA
- **Regra:** Preços de commodities são séries globais e não devem ser atribuídos a um município nem apresentados como preço realizado numa empresa ou no Pará.
- **Motivo:** São preços de referência internacionais; atribuí-los a um município seria afirmar o que a fonte não diz.
- **Exemplo:** O preço do minério de ferro é uma série global e não aparece no recorte de Canaã dos Carajás.
- **Fonte:** BLOCOS §Bloco 2 ("séries globais (sem recorte municipal)"); VAL-15/10 §Matriz operacional (World Bank Pink Sheet); LAB-19/10 §4 (FRED e World Bank Pink Sheet); CONSUMO §Economia.
- **Relacionadas:** RN-FNT-05

### RN-MOD-20: Ano de referência sempre exibido
- **Status:** DECIDIDA
- **Regra:** Todo número exibido deve vir acompanhado do seu ano (ou período) de referência.
- **Motivo:** Evita anunciar dado mais novo do que o existente e torna a defasagem visível.
- **Exemplo:** Um gráfico de PIB municipal mostra 2023 como último ano, mesmo que a fonte publique outro ano mais tarde.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3); PLANO §Riscos e cuidados.
- **Relacionadas:** RN-TMP-01, RN-VPU-09

### RN-MOD-21: Proveniência acompanha o dado
- **Status:** DECIDIDA
- **Regra:** Todo dado tratado deve carregar quando foi gerado, de qual fonte e de qual ano-base, e a edição e a data de coleta da fonte.
- **Motivo:** Permite exibir "atualizado em" e torna evidente quando uma fonte parou.
- **Exemplo:** O manifesto de qualidade da distribuição da CFEM de 2025 registra o hash da origem, 11/12 municípios presentes e a ausência de julho em todo o arquivo (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026 com arquivos da ANM (o hash é o do arquivo de 24/10/2026).
- **Fonte:** DECISÕES §Arquitetura e padrões de dados ("Proveniência embutida"); VAL-15/10 §Marco 1, §Marco 2.
- **Relacionadas:** RN-FON-13, RN-ENT-04

### RN-MOD-22: Período do fenômeno separado da data de coleta
- **Status:** DECIDIDA
- **Regra:** O período a que o dado se refere não deve ser confundido com a data em que ele foi coletado ou atualizado.
- **Motivo:** Um dado coletado numa data pode se referir a um ano anterior.
- **Exemplo:** A população de 2025 coletada em out/2026 tem período 2025 e data de coleta out/2026.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (`ano` e `atualizado_em`); VAL-15/10 §Marco 1.
- **Relacionadas:** RN-MOD-21

### RN-MOD-23: Eleitorado guarda total e gênero
- **Status:** DECIDIDA
- **Regra:** O número de eleitores deve ser guardado como total e por gênero, e a escolha do que exibir deve ser feita na apresentação.
- **Motivo:** Segue o princípio de guardar no detalhe e decidir na saída.
- **Exemplo:** Eleitorado por município e zona, agregado por município.
- **Fonte:** DECISÕES §Número de eleitores; BLOCOS §Bloco 1.
- **Relacionadas:** RN-MOD-05, RN-TER-08

### RN-MOD-24: Valor real e índice de correção
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir como o valor real será publicado: o índice de correção, o ano-base e se entra como indicador derivado, com o índice explícito.
- **Motivo:** O valor real é um pedido do projeto, mas nenhuma fonte de decisão define o índice nem o ano-base. Até lá, os valores monetários são publicados em valor nominal (RN-MOD-26).
- **Exemplo:** Despesa per capita por função, 2013–2025, em valor nominal.
- **Fonte:** CONSUMO §Finanças públicas e índices (despesa per capita); DECISÃO-MANTENEDOR de 26/10/2026 (o valor real fica para uma etapa futura).
- **Relacionadas:** RN-MOD-17, RN-MOD-26

### RN-MOD-25: Manifesto único de indicadores
- **Status:** DECIDIDA
- **Regra:** Deve existir um manifesto único que descreva cada indicador (identificação, nome, bloco, fonte, método, frequência e estratégia, congelado ou recalculado) e a lista de municípios de comparação.
- **Motivo:** É a fonte da verdade: documentação, agenda e configuração no mesmo lugar.
- **Exemplo:** O Barômetro da Sustentabilidade consta como "congelado, não promovível".
- **Exceções:** Nome, formato e local do arquivo ficam fora desta documentação.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados ("Manifesto"), §Indicadores compostos; LAB-19/10 §7 (Próximos passos, item 5).
- **Relacionadas:** RN-IND-01, RN-TER-09, RN-TMP-02

### RN-MOD-26: Valores monetários em valor nominal por enquanto
- **Status:** DECIDIDA
- **Regra:** Os valores monetários devem ser publicados em valor nominal, como a fonte os informou, sem correção por índice de preços, até a decisão sobre o valor real (RN-MOD-24).
- **Motivo:** Nenhum indicador atual exige valor real, e escolher índice e ano-base agora ampliaria o escopo sem definição.
- **Exemplo:** Despesa per capita por função, 2013–2025, em valor nominal.
- **Exceções:** O valor real é um pedido do projeto e será acrescentado depois, com índice e ano-base explícitos; por isso RN-MOD-24 continua EM ABERTO.
- **Fonte:** DECISÃO-MANTENEDOR de 26/10/2026; CONSUMO §Finanças públicas e índices (despesa per capita).
- **Relacionadas:** RN-MOD-24, RN-MOD-17
