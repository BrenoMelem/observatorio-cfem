# Entrega dos dados

Regras sobre o que o consumidor dos dados (front-end, exportações CSV e assistente de IA) pode receber e como. Legenda de status e siglas das fontes: [README](README.md).

As fontes divergiam sobre a forma da entrega: DECISÕES e PLANO descrevem uma camada de arquivos JSON e CSV versionados; VAL-15/10 e CONSUMO preveem uma API própria. O mantenedor decidiu pela API própria em 30/10/2026 (RN-ENT-02, conflito 2). As regras abaixo foram escritas para valer nos dois casos; onde aparece "camada publicada", leia "API própria".

### RN-ENT-01: Camada tratada entre as fontes e o consumo
- **Status:** DECIDIDA
- **Regra:** O front-end, as exportações e o assistente de IA devem consumir apenas a camada publicada de dados tratados e nunca devem chamar a fonte externa diretamente.
- **Motivo:** Uma fonte fora do ar não quebra o consumidor, trocar a origem de um indicador não afeta o gráfico, e cache, credenciais, versionamento e falhas ficam centralizados.
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
- **Exceções:** Nenhuma restrição de licença: as fontes são dados abertos (decisão do mantenedor de 07/11/2026; RN-PRI-05, RN-PRI-06 e RN-ENT-10 ficaram obsoletas).
- **Fonte:** DECISÕES §Publicação e extras; VAL-15/10 §Marco 4.
- **Relacionadas:** RN-ENT-05

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
- **Motivo:** Os arquivos têm centenas de MB e registros por linha, e a ausência de municípios ou de meses ficaria escondida.
- **Exemplo:** O arquivo de distribuição tem 2.238.877 linhas, das quais 11.847 são dos 12 municípios (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3), §Rodada adicional; CONSUMO §CFEM e receitas minerais, §Bypass seguro quando não houver API; MAPA-TEMAS §Tema central do Observatório: CFEM.
- **Relacionadas:** RN-ENT-01, RN-VPU-10

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
- **Exceções:** As metas numéricas de cada critério estão **EM ABERTO**; não há evidência de que a avaliação tenha sido executada. Em 11/11/2026 o mantenedor definiu a prioridade: o assistente é etapa posterior ao tratamento dos dados, e os critérios e as metas só serão fixados quando essa etapa começar (a regra segue PROPOSTA; não é esquecimento, é ordem de trabalho).
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 2). O próprio VAL-15/10 chama os critérios de "propostos".
- **Relacionadas:** RN-ENT-07

### RN-ENT-09: Primeiros gráficos
- **Status:** PROPOSTA
- **Regra:** Os primeiros gráficos devem usar dados homologados de população municipal e de CFEM arrecadada e recebida, em painéis separados.
- **Motivo:** Começa pelo que já tem rota validada e respeita que arrecadação e distribuição são medidas distintas.
- **Exemplo:** Painel de população de Canaã e Parauapebas; painéis separados de CFEM arrecadada e CFEM recebida.
- **Exceções:** Em 13/11/2026 o mantenedor decidiu que a dimensão econômica é a primeira (RN-ENT-12). A CFEM arrecadada e a recebida fazem parte dela, e nisso as duas regras coincidem. A população é da dimensão social; está **EM ABERTO** se o painel de população continua entre os primeiros gráficos ou se a população entra na primeira etapa só como denominador dos indicadores per capita (RN-IND-09, RN-IND-12). Ver [pendencias.md](pendencias.md), seção 2.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3), que é uma recomendação do relatório e não uma decisão de DECISÕES ou de BLOCOS; BLOCOS §Bloco 1 (população como primeiro pipeline).
- **Relacionadas:** RN-CFE-02, RN-VPU-10, RN-ENT-12

### RN-ENT-10: Licença de reuso das exportações
- **Status:** OBSOLETA
- **Obsoleta desde 07/11/2026:** decisão do mantenedor. As fontes do projeto são dados abertos, então o tema privacidade e licença não é necessário nesta documentação. O texto original fica abaixo, sem alteração, para o histórico.
- **Regra:** O CSV aberto inclui apenas as fontes cuja licença de redistribuição esteja confirmada. As demais ficam fora das exportações até o mantenedor verificar a licença; a licença de cada fonte continua pendente em RN-PRI-06.
- **Motivo:** Nenhuma licença de redistribuição foi confirmada nas fontes de decisão; publicar sem ela contraria RN-ENT-03.
- **Exemplo:** Enquanto a licença de FAPESPA e IDSC não for verificada, seus indicadores não entram no CSV aberto.
- **Fonte:** DECISÃO-MANTENEDOR de 28/10/2026; LAB-19/10 §4 (Portais de apoio); CONSUMO §Contrato de dados para o front-end; PESQUISA §Conclusões principais (item 4).
- **Relacionadas:** RN-ENT-03, RN-PRI-05, RN-PRI-06

### RN-ENT-11: Dado fictício aparece só rotulado
- **Status:** DECIDIDA
- **Regra:** Gráfico com dado fictício de demonstração deve trazer, em si mesmo, o rótulo visível "dados fictícios (protótipo)", e o rótulo só sai quando o dado for substituído por dado real.
- **Motivo:** O mantenedor mandou manter o que o `obcefem` faz: nas páginas de dimensão, cada gráfico traz o selo "dados reais" ou "dados fictícios (protótipo)".
- **Exemplo:** As quatro páginas de dimensão do `obcefem` misturam os dois selos (conferido no código das páginas em 08/11/2026).
- **Exceções:** Não flexibiliza RN-VPU-10: dado fictício não é dado homologado e não entra na camada publicada.
- **Fonte:** DECISÃO-MANTENEDOR de 08/11/2026; `obcefem`, páginas `dimensao-*.html`.
- **Relacionadas:** RN-VPU-10, RN-ENT-04

### RN-ENT-12: A dimensão econômica é a primeira
- **Status:** DECIDIDA
- **Regra:** A dimensão econômica deve ser a primeira a ser feita, tanto na carga dos dados quanto nos painéis; as dimensões social, ambiental e institucional vêm depois. A dimensão econômica reúne: a CFEM (arrecadação, distribuição e autuações), o PIB municipal e seus derivados, os preços do minério de ferro e do cobre, as finanças municipais e a despesa por função.
- **Motivo:** O projeto trata principalmente da CFEM e da economia e é um projeto da Vale; por ser um dos pontos principais, esse conteúdo deve ficar pronto antes dos demais.
- **Exemplo:** A página da dimensão econômica do `obcefem` tem quatro seções: dinâmica econômica (PIB), preços do minério e do cobre, finanças municipais, e investimento público e despesa por função; a página inicial lista "Distribuição da CFEM" nessa dimensão. A `obcefem_api` inteira (arrecadação, autuações e distribuição estimada) é CFEM e, portanto, pertence a ela (conferido no código dos dois repositórios em 13/11/2026).
- **Exceções:** (1) Emprego e renda ficam na dimensão social, como no `obcefem`, por decisão do mantenedor de 13/11/2026; isso contraria BLOCOS §Bloco 2, que junta economia e mercado de trabalho (04/10/2026, última edição 20/10/2026). BLOCOS não foi alterado. (2) A ordem não flexibiliza RN-VPU-10: só dado homologado alimenta os gráficos, e RN-ENT-11 continua valendo para dado fictício. (3) Estão **EM ABERTO**: a ordem das outras três dimensões; a composição de cada uma delas; e a fonte e o método da composição da receita corrente, do investimento público e do ICMS repassado, que aparecem na página do `obcefem` e não têm regra. Ver [pendencias.md](pendencias.md), seções 2 e 4.
- **Fonte:** DECISÃO-MANTENEDOR de 13/11/2026; `obcefem`, páginas `index.html` e `dimensao-economica.html`; `obcefem_api`. A composição corresponde a BLOCOS §Bloco 3 (Mineração e CFEM), §Bloco 6 (Finanças Públicas) e à parte de PIB e preços do §Bloco 2.
- **Relacionadas:** RN-ENT-09, RN-ENT-11, RN-VPU-10, RN-CFE-02, RN-CFE-25, RN-CFE-26, RN-FNT-02, RN-FNT-04, RN-FNT-05, RN-IND-09, RN-IND-10
