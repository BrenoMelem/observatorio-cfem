# Entrega dos dados

Regras sobre o que o consumidor dos dados (front-end, exportações CSV e assistente de IA) pode receber e como. Legenda de status e siglas das fontes: [README](README.md).

As fontes divergiam sobre a forma da entrega: DECISÕES e PLANO descrevem uma camada de arquivos JSON e CSV versionados; VAL-15/10 e CONSUMO preveem uma API própria. O mantenedor decidiu pela API própria em 30/10/2026 (RN-ENT-02, conflito 2). As regras abaixo foram escritas para valer nos dois casos; onde aparece "camada publicada", leia "API própria".

### RN-ENT-01: Camada tratada entre as fontes e o consumo
- **Status:** DECIDIDA
- **Regra:** O front-end, as exportações e o assistente de IA devem consumir apenas a camada publicada de dados tratados e nunca devem chamar a fonte externa diretamente.
- **Motivo:** Uma fonte fora do ar não quebra o consumidor, trocar a origem de um indicador não afeta o gráfico, e cache, licenças, credenciais, versionamento e falhas ficam centralizados.
- **Exemplo:** O gráfico de população lê a camada publicada e não a API do IBGE; o gráfico de CFEM não lê os CSVs nacionais da ANM.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados; VAL-15/10 §Resposta ao orientador (item 3); PLANO §Arquitetura e fluxo geral; CONSUMO §Contrato de dados para o front-end.
- **Relacionadas:** RN-ENT-02, RN-ENT-06, RN-VPU-03, RN-VPU-10

### RN-ENT-02: Forma de entrega da camada publicada
- **Status:** DECIDIDA
- **Regra:** A camada publicada é entregue por uma API própria, mantida pelo projeto, com endpoint de leitura e metadados. A obrigação de oferecer o CSV aberto (RN-ENT-03) continua valendo e deve ser atendida por essa mesma camada.
- **Motivo:** Decisão do mantenedor, entre as duas versões das fontes. A API permite consultas sob demanda; em contrapartida, exige um serviço em funcionamento.
- **Exemplo:** VAL-15/10 §Marco 1 prevê "endpoint de leitura" com metadados; o painel consulta a API e não lê arquivos publicados.
- **Exceções:** Esta decisão contraria DECISÕES e PLANO, que descrevem arquivos JSON e CSV versionados. Essas fontes devem ser atualizadas pelo mantenedor.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; Versão A (não adotada): DECISÕES §Arquitetura e padrões de dados (04/10/2026, última edição 20/10/2026); PLANO §Arquitetura e fluxo geral (30/09/2026). Versão B (adotada): VAL-15/10 §Marco 1, §Marco 4 (15/10/2026); CONSUMO §Contrato de dados para o front-end (02/10/2026).
- **Relacionadas:** RN-MOD-03, RN-ENT-01

### RN-ENT-03: CSV aberto
- **Status:** DECIDIDA
- **Regra:** Os dados tratados devem poder ser baixados por qualquer pessoa em CSV aberto.
- **Motivo:** O custo é quase zero, pois o dado já existe nesse formato na camada tratada, e aumenta a credibilidade do observatório como fonte reutilizável e citável.
- **Exemplo:** A série populacional dos 12 municípios disponível em CSV.
- **Exceções:** Não devem ser publicados dados cuja licença de redistribuição não esteja confirmada (RN-PRI-05, RN-PRI-06 e RN-ENT-10).
- **Fonte:** DECISÕES §Publicação e extras; VAL-15/10 §Marco 4.
- **Relacionadas:** RN-ENT-05, RN-ENT-10, RN-PRI-05

### RN-ENT-04: Painel de status por indicador
- **Status:** DECIDIDA
- **Regra:** Deve existir um painel de status que mostre, para cada indicador, quando foi atualizado pela última vez e qual o ano de referência.
- **Motivo:** Serve de alarme de "fonte em silêncio": o visitante e a equipe percebem quando algo parou de atualizar.
- **Exemplo:** A população estimada de 2025 aparece com a data da última atualização e o ano de referência 2025.
- **Fonte:** DECISÕES §Publicação e extras; VAL-15/10 §Marco 4.
- **Relacionadas:** RN-MOD-21, RN-MOD-22, RN-TMP-02

### RN-ENT-05: Exportações levam os metadados junto dos valores
- **Status:** PROPOSTA
- **Regra:** As exportações em CSV ou JSON devem incluir os metadados (fonte, edição, método, limitações) junto dos valores.
- **Motivo:** Um valor exportado sem contexto perde a rastreabilidade.
- **Exemplo:** O CSV da CFEM recebida traz fonte ANM e a limitação de que distribuição não equivale a arrecadação.
- **Fonte:** CONSUMO §Contrato de dados para o front-end. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-ENT-03, RN-MOD-02

### RN-ENT-06: Arquivos integrais da ANM não vão ao consumidor
- **Status:** DECIDIDA
- **Regra:** Os CSVs nacionais da ANM não devem ser entregues integralmente ao navegador nem consumidos diretamente pelos gráficos.
- **Motivo:** Os arquivos têm centenas de MB e campos identificadores (CPF/CNPJ), e a ausência de municípios ou de meses ficaria escondida.
- **Exemplo:** O arquivo de distribuição tem 2.238.877 linhas, das quais 11.847 são dos 12 municípios (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3), §Rodada adicional; CONSUMO §CFEM e receitas minerais, §Bypass seguro quando não houver API; MAPA-TEMAS §Tema central do Observatório: CFEM.
- **Relacionadas:** RN-ENT-01, RN-PRI-01, RN-VPU-10

### RN-ENT-07: O assistente responde só com a camada publicada
- **Status:** PROPOSTA
- **Regra:** O assistente de IA deve responder apenas com dados da camada publicada, sempre com fonte, período e limitações, e quando não houver observação validada compatível deve dizer que não há dado validado e explicar a lacuna.
- **Motivo:** Evita resposta inventada e mantém a mesma garantia de procedência do restante do observatório.
- **Exemplo:** Perguntado sobre o total anual de distribuição da CFEM de 2025, o assistente deve informar que o total está bloqueado por falta de julho de 2025, e não somar os meses disponíveis.
- **Fonte:** CONSUMO §Contrato de dados para o front-end. VAL-15/10 §Resposta ao orientador (item 2) lista como critério de avaliação a "recusa de inventar número ausente", sem fixar a regra.
- **Relacionadas:** RN-ENT-01, RN-ENT-08, RN-CFE-05, RN-MOD-08

### RN-ENT-08: Critérios de avaliação do assistente
- **Status:** PROPOSTA
- **Regra:** O assistente deve ser avaliado por: taxa de respostas corretas com citação, recusa de inventar número ausente, latência (p50 e p95), disponibilidade, custo por consulta e cobertura de perguntas dos 12 municípios, com um conjunto de perguntas de respostas verificadas pela equipe.
- **Motivo:** Dá critério objetivo para aceitar o assistente.
- **Exemplo:** Conjunto de perguntas sobre população e CFEM de Canaã dos Carajás e Parauapebas com respostas verificadas.
- **Exceções:** As metas numéricas de cada critério estão **EM ABERTO**; não há evidência de que a avaliação tenha sido executada.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 2). O próprio VAL-15/10 chama os critérios de "propostos".
- **Relacionadas:** RN-ENT-07

### RN-ENT-09: Primeiros gráficos
- **Status:** PROPOSTA
- **Regra:** Os primeiros gráficos devem usar dados homologados de população municipal e de CFEM arrecadada e recebida, em painéis separados.
- **Motivo:** Começa pelo que já tem rota validada e respeita que arrecadação e distribuição são medidas distintas.
- **Exemplo:** Painel de população de Canaã e Parauapebas; painéis separados de CFEM arrecadada e CFEM recebida.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3), que é uma recomendação do relatório e não uma decisão de DECISÕES ou de BLOCOS; BLOCOS §Bloco 1 (população como primeiro pipeline).
- **Relacionadas:** RN-CFE-02, RN-VPU-10

### RN-ENT-10: Licença de reuso das exportações
- **Status:** DECIDIDA
- **Regra:** O CSV aberto inclui apenas as fontes cuja licença de redistribuição esteja confirmada. As demais ficam fora das exportações até o mantenedor verificar a licença; a licença de cada fonte continua pendente em RN-PRI-06.
- **Motivo:** Nenhuma licença de redistribuição foi confirmada nas fontes de decisão; publicar sem ela contraria RN-ENT-03.
- **Exemplo:** Enquanto a licença de FAPESPA e IDSC não for verificada, seus indicadores não entram no CSV aberto.
- **Fonte:** DECISÃO-MANTENEDOR de 28/10/2026; LAB-19/10 §4 (Portais de apoio); CONSUMO §Contrato de dados para o front-end; PESQUISA §Conclusões principais (item 4).
- **Relacionadas:** RN-ENT-03, RN-PRI-05, RN-PRI-06
