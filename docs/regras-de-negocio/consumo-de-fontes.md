# Consumo de fontes

Regras gerais sobre como o observatório obtém dados de fontes externas: nível de acesso, procedência, o que é permitido e como tratar credenciais. Regras de uma fonte específica estão em [regras-por-fonte.md](regras-por-fonte.md). Legenda de status e siglas das fontes: [README](README.md).

## Níveis de acesso A, B, C e D

O nível mede a forma de acesso, não a qualidade do dado. Uma fonte B pode ser mais confiável que uma API A.

| Nível | Significado | Forma de consumo adequada |
| --- | --- | --- |
| A | API documentada | Consultas programadas, com paginação, limites e resposta bruta preservada |
| B | Arquivo ou tabela estruturada oficial, sem API documentada | Captura por edição, registrando URL, data e checksum, e validando o esquema antes de atualizar |
| C | Exportação assistida (painel público ou PDF) | Usar o recurso oficial, passar por área de revisão e reconciliar antes de publicar |
| D | Acesso condicionado ou lacuna | Solicitar acesso ou dado agregado, nunca raspar nem contornar; manter o indicador pendente se preciso |

### RN-FON-01: Níveis de acesso medem a forma, não a qualidade
- **Status:** PROPOSTA
- **Regra:** Cada indicador deve ser classificado em um dos níveis A, B, C ou D conforme a forma de acesso à fonte, e o nível não deve ser usado como juízo de qualidade do dado.
- **Motivo:** A forma de acesso define o cuidado de consumo; a qualidade é outra questão.
- **Exemplo:** A CFEM da ANM é nível B (CSV oficial sem API); o SICONFI é nível A.
- **Fonte:** CONSUMO §Classificação de consumo; MAPA-TEMAS (critério da coluna "Tem API?"). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-FON-05, RN-FON-06

### RN-FON-02: Fonte primária onde há API boa
- **Status:** DECIDIDA
- **Regra:** Quando a fonte primária tiver API adequada, o observatório deve consumi-la diretamente.
- **Motivo:** Reduz intermediários e dá procedência mais clara.
- **Exemplo:** O IBGE SIDRA e o SICONFI têm API própria e são consumidos direto.
- **Exceções:** Onde a Base dos Dados é a via prática (RAIS, IDEB, eleitorado e Censo Escolar) ela é usada, sempre com citação da origem. A escolha da via em alguns indicadores está em conflito (RN-FON-20).
- **Fonte:** DECISÕES §Estratégia de fontes e acesso.
- **Relacionadas:** RN-FON-03, RN-FON-20

### RN-FON-03: A Base dos Dados nunca é fonte primária
- **Status:** DECIDIDA
- **Regra:** Dados obtidos pela Base dos Dados devem ser citados com a origem, no formato "<fonte> via Base dos Dados", e nunca apenas como "Base dos Dados".
- **Motivo:** A Base dos Dados espelha dados públicos; MTE, DATASUS, INEP e TSE não publicam no BigQuery. A procedência precisa apontar para o órgão produtor.
- **Exemplo:** "RAIS via Base dos Dados". O prefixo `br_` nos nomes de tabela indica que a consulta é à Base dos Dados, não ao órgão.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso; BLOCOS §Bloco 4, §Glossário.
- **Relacionadas:** RN-FON-02, RN-TMP-03

### RN-FON-04: Portal acessível não é dado consumível
- **Status:** DECIDIDA
- **Regra:** A abertura de uma página, a leitura de um cabeçalho, a importação de uma biblioteca ou um metadado não devem ser tratados como prova de que o indicador municipal existe, e uma prova aprovada não equivale a uma série coletada, validada e pronta.
- **Motivo:** Uma prova confirma só o que ela testou; concluir mais leva a prometer um indicador que não pode ser consumido.
- **Exemplo:** No laboratório de 17/10/2026, 16 provas ficaram OK, mas sete eram apenas páginas de portal acessíveis e três eram cabeçalhos de CSV da CFEM (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** LAB-19/10 §1, §2, §3, §4 (Portais de apoio); VAL-15/10 §Como repetir os testes (item 6).
- **Relacionadas:** RN-FON-18, RN-VPU-09

### RN-FON-05: Não contornar login nem usar endpoints internos de painéis
- **Status:** PROPOSTA
- **Regra:** O observatório não deve contornar login ou controle de acesso, não deve automatizar autenticação para dados identificados e não deve depender de endpoints internos de painéis nem imitar chamadas privadas.
- **Motivo:** O contorno é frágil, pode violar termos de uso e expõe o projeto a risco jurídico.
- **Exemplo:** No CECAD usam-se as consultas agregadas públicas e não o módulo restrito; em fonte que exige senha individual, solicita-se acesso ou dado agregado.
- **Fonte:** CONSUMO §Conclusão executiva, §Bypass seguro quando não houver API; MAPA-TEMAS §Resumo para apresentação.
- **Relacionadas:** RN-FON-06, RN-PRI-08

### RN-FON-06: PDF só entra por área de revisão
- **Status:** PROPOSTA
- **Regra:** Dado extraído de PDF deve ter o original guardado, a tabela e a página registradas e deve passar por área de revisão e conferência de amostras e totais antes de ir à produção.
- **Motivo:** A extração de PDF é frágil e a transcrição pode errar.
- **Exemplo:** O Barômetro da Sustentabilidade da FAPESPA é congelado por transcrição auditada.
- **Fonte:** CONSUMO §Bypass seguro quando não houver API (item 3). Dedução complementar: DECISÕES §Estratégia ("documentar como manual onde só há PDF") trata do mesmo risco, sem prever a revisão.
- **Relacionadas:** RN-FON-16, RN-IND-04

### RN-FON-07: Nunca desligar a verificação TLS
- **Status:** DECIDIDA
- **Regra:** A coleta não deve desligar a verificação de certificado TLS, e falha de certificado deve ser registrada como falha do ambiente, e não convertida em sucesso.
- **Motivo:** Desligar a verificação enfraquece a prova de conexão segura e esconde o problema real.
- **Exemplo:** Em 15/10/2026 duas chamadas ao IBGE falharam por certificado; o erro do DETRAN-PA foi atribuído a uma cadeia de certificados incompleta no servidor. Um teste diagnóstico com verificação desligada deu HTTP 200, mas essa prática "não deve virar método de coleta" (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** LAB-19/10 §5.4; VAL-15/10 §O que o notebook do Daniel efetivamente provou (parágrafo sobre TLS).
- **Relacionadas:** RN-FON-08

### RN-FON-08: Credenciais são segredo
- **Status:** DECIDIDA
- **Regra:** Credenciais, chaves de acesso e tokens devem ser guardados como segredo e não devem aparecer no código, no Git, em notebooks nem em saídas impressas.
- **Motivo:** Um segredo vazado dá acesso indevido a contas e a serviços pagos.
- **Exemplo:** A chave do FRED é guardada como segredo e nunca escrita no código nem compartilhada.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Credencial única do Google Cloud); LAB-19/10 §4 (FRED e World Bank Pink Sheet), §5.3; VAL-15/10 §Como repetir os testes (item 7).
- **Relacionadas:** RN-FON-09, RN-FON-10

### RN-FON-09: Credencial do Google Cloud
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir como o pipeline se autentica no Google Cloud, entre as duas versões abaixo.
- **Motivo:** DECISÕES, LAB-19/10 e VAL-15/10 divergem, e o mantenedor ainda não domina a plataforma.
- **Exemplo:** Uma execução do laboratório com `GCP_PROJECT` vazio e sem autenticação terminou em estado PENDENTE, sem consulta faturada (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Exceções:** Nenhuma regra sobre o tipo de credencial vale até a decisão. As regras RN-FON-08 (segredo) e RN-FON-11 (ensaio de custo) valem em qualquer versão.
- **Fonte:** Versão A: DECISÕES §Estratégia de fontes e acesso, §Pré-requisitos e pendências (service account com chave em arquivo guardada como segredo, 04/10/2026, última edição 20/10/2026); BLOCOS §Bloco 5 ("mesma credencial do BigQuery"). Versão B: LAB-19/10 §5.3 e VAL-15/10 §Como repetir os testes (item 7) (não usar chave de conta de serviço e autenticar com a conta de quem executa, 15 e 19/10/2026). VAL-15/10 §Pendências externas registra ainda que o consentimento OAuth pedia acesso amplo a Drive e Google Cloud. O mantenedor registra que LAB-19/10 é mais recente nesse ponto (DECISÃO-MANTENEDOR de 24/10/2026), mas não decidiu.
- **Relacionadas:** RN-FON-08, RN-FON-11, RN-PRI-10

### RN-FON-10: Chave do FRED própria de quem executa
- **Status:** DECIDIDA
- **Regra:** Cada aplicação e cada usuário que roda a coleta deve usar a própria chave do FRED, obtida gratuitamente no site do serviço.
- **Motivo:** Os termos de uso do FRED exigem uma chave por aplicação e uma por usuário.
- **Exemplo:** A chave não estava configurada em 17/10/2026 e a prova ficou PENDENTE; configurada em 19/10/2026, a prova passou (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** LAB-19/10 §4 (FRED e World Bank Pink Sheet), §5.2.
- **Relacionadas:** RN-FON-08, RN-FNT-05

### RN-FON-11: Ensaio de custo antes de consultar a Base dos Dados
- **Status:** DECIDIDA
- **Regra:** Nenhuma consulta ao BigQuery deve ser executada sem um ensaio de custo (estimativa de processamento sem executar) revisado antes.
- **Motivo:** Consultas podem gerar custo e o volume da RAIS e do CAGED é grande.
- **Exemplo:** O notebook preserva a consulta desligada até a revisão do custo e usa uma estimativa de bytes antes de executar.
- **Fonte:** LAB-19/10 §5.3, §6; VAL-15/10 §Como repetir os testes (item 7).
- **Relacionadas:** RN-FON-12, RN-FON-19

### RN-FON-12: Teto de bytes por consulta
- **Status:** PROPOSTA
- **Regra:** Cada consulta ao BigQuery deve ter um teto de bytes processados, e a consulta cuja estimativa passar do teto não deve ser executada.
- **Motivo:** Impede custo inesperado.
- **Exemplo:** O laboratório usou 100 MiB por consulta.
- **Fonte:** NOTEBOOK (células 16 e 18); VAL-15/10 §Como repetir os testes (item 7: "O código impõe 100 MiB por consulta"). O valor é do laboratório, não uma decisão para produção.
- **Relacionadas:** RN-FON-11

### RN-FON-13: Proveniência de cada captura
- **Status:** DECIDIDA
- **Regra:** Toda captura de dado externo deve registrar a URL da fonte, a edição, o checksum do arquivo, a data de coleta e a versão do tratamento aplicado.
- **Motivo:** Permite refazer a busca e provar de onde veio cada número.
- **Exemplo:** Os registros de evidência dos CSVs da ANM preservam URL, data, tamanho e SHA-256 (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** VAL-15/10 §Marco 1, §Marco 2, §Rodada adicional; DECISÕES §Arquitetura e padrões de dados (Proveniência embutida); CONSUMO §Classificação de consumo (nível B).
- **Relacionadas:** RN-MOD-21, RN-FON-14

### RN-FON-14: Filtros usados ficam registrados
- **Status:** PROPOSTA
- **Regra:** Os filtros aplicados na obtenção de um dado (ano, mês, modalidade, município, consulta) devem ser registrados junto da captura.
- **Motivo:** O mesmo arquivo filtrado de formas diferentes dá totais diferentes.
- **Exemplo:** A reconciliação de maio de 2025 registrou ano 2025, mês 5 e distribuição do tipo `Produtor`.
- **Fonte:** CONSUMO §Bypass seguro quando não houver API (item 2); SCRIPTS (`reconcile_anm_distribution`).
- **Relacionadas:** RN-FON-13

### RN-FON-15: Dado bruto fora do Git quando grande ou identificável
- **Status:** DECIDIDA
- **Regra:** O dado bruto baixado não deve ser versionado quando for grande ou conter campos identificadores, e só os agregados e os metadados devem ser versionados.
- **Motivo:** Evita repositório inchado e lento e evita expor CPF/CNPJ.
- **Exemplo:** Os CSVs completos da ANM ficam fora do Git por terem centenas de MB e campos identificadores.
- **Exceções:** BLOCOS diz que a planilha do SEEG é "guardada no repositório" e não define o que conta como "grande". Isso está **EM ABERTO** (conflito 16 em [pendencias.md](pendencias.md)), junto da licença de redistribuição do SEEG.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (Separar raw de processed); VAL-15/10 §Rodada adicional; BLOCOS §Bloco 5 (CO₂).
- **Relacionadas:** RN-PRI-01, RN-PRI-06

### RN-FON-16: Automatizar onde há API, aceitar arquivo estável, documentar o que é manual
- **Status:** DECIDIDA
- **Regra:** Deve-se automatizar onde há API, aceitar download onde a fonte publica arquivo estável e documentar como manual onde só há PDF.
- **Motivo:** Um extrator de PDF frágil dá mais trabalho do que baixar o arquivo uma vez por ano.
- **Exemplo:** SIDRA e SICONFI por API; SEEG por download; o Barômetro da FAPESPA por transcrição manual congelada.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso (Regra geral de método); PLANO §Resumo por método de acesso.
- **Relacionadas:** RN-FON-06, RN-FON-17

### RN-FON-17: Fontes manuais entram na mesma camada
- **Status:** PROPOSTA
- **Regra:** Dados de fontes manuais devem entrar na mesma camada de dados tratados, depositados à mão e documentados.
- **Motivo:** Quem consome os dados não deve distinguir a origem automática da manual.
- **Exemplo:** O ranking de competitividade da CLP congelado com citação.
- **Fonte:** PLANO §Arquitetura e fluxo geral. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-FON-16, RN-IND-01

### RN-FON-18: Validar a leitura antes de concluir sobre cobertura
- **Status:** DECIDIDA
- **Regra:** Uma conclusão sobre cobertura territorial de um arquivo só deve ser tirada depois de confirmar que o arquivo foi lido corretamente, incluindo o separador de colunas, que deve ser detectado no cabeçalho e não presumido.
- **Motivo:** Um erro de leitura pode parecer ausência de dado.
- **Exemplo:** O CSV do AMB foi lido com ";" e pareceu ter uma única coluna; com a vírgula detectada, viu-se que há UF, mas não município (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** LAB-19/10 §5.1; DECISÕES §Bloco 3 (VPM: "o metadado da ANM diz ponto e vírgula, mas o arquivo real usa vírgula").
- **Relacionadas:** RN-FON-04, RN-CFE-19

### RN-FON-19: RAIS e CAGED por consulta filtrada
- **Status:** DECIDIDA
- **Regra:** As tabelas de RAIS e CAGED na Base dos Dados devem ser consultadas por SQL filtrado pelos municípios de interesse e nunca baixadas inteiras.
- **Motivo:** São grandes demais para baixar pela interface.
- **Exemplo:** A tabela `microdados_movimentacoes` do Novo CAGED cobre o período pós-2020; a `microdados_antigos` vai só até cerca de 2019.
- **Fonte:** DECISÕES §Tabelas da Base dos Dados confirmadas; PLANO §Bloco 2.
- **Relacionadas:** RN-FON-11, RN-FNT-11

### RN-FON-20: Escolha da via de acesso nos indicadores em conflito
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir a fonte e a via de acesso de cada indicador cujas fontes de decisão divergem; até lá, nenhuma versão vale como regra.
- **Motivo:** DECISÕES, BLOCOS, PLANO, MAPA-TEMAS, CONSUMO e relatórios divergem em emprego, homicídios, frota, uso do solo e na via Base dos Dados versus arquivo oficial.
- **Exemplo:** Emprego: IPEADATA (DECISÕES, BLOCOS) versus microdados do MTE (MAPA-TEMAS, CONSUMO); em 15/10/2026 o filtro do IPEADATA não limitou a resposta, que anunciou 63.685.034 bytes (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** Conflitos 3, 4, 5, 6 e 9 em [pendencias.md](pendencias.md); DECISÕES; BLOCOS; CONSUMO; MAPA-TEMAS; VAL-15/10; LAB-19/10.
- **Relacionadas:** RN-FON-02, RN-FNT-08, RN-FNT-12, RN-FNT-13, RN-FNT-20, RN-FNT-21
