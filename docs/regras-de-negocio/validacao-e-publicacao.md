# Validação e publicação

Regras sobre o que um lote precisa cumprir para ser publicado e sobre o que fazer quando não cumpre. Legenda de status e siglas das fontes: [README](README.md). As regras de entrega ao consumidor estão em [entrega-dos-dados.md](entrega-dos-dados.md).

### RN-VPU-01: Publicar só lotes validados
- **Status:** DECIDIDA
- **Regra:** Somente lotes que passaram por todas as validações devem ser publicados, e uma execução cujo lote falhar não deve publicar nenhum dado novo desse indicador.
- **Motivo:** Publicar dado não validado transmite como certo um número que pode estar errado.
- **Exemplo:** O arquivo agregado da distribuição da CFEM de 2025 registra "pronto para publicar: não" e serve só a testes mensais, não a um total anual (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (Validação antes de publicar); VAL-15/10 §Marco 4, §Rodada adicional.
- **Relacionadas:** RN-VPU-03, RN-VPU-08, RN-VPU-10

### RN-VPU-02: Checagens mínimas antes de publicar
- **Status:** DECIDIDA
- **Regra:** Todo lote deve ser checado quanto a: o município existe na lista oficial, o valor informado não é nulo, a série não encolheu em relação à versão anterior e o número está numa faixa plausível.
- **Motivo:** São as verificações simples que pegam a maior parte dos erros de fonte e de tratamento.
- **Exemplo:** Um valor de CFEM para um código que não está entre os 12 municípios não passa na checagem de existência.
- **Exceções:** (1) A checagem "série não encolheu" fica desligada para as autuações da CFEM (RN-CFE-15). (2) "Valor não nulo" vale para observações informadas; a ausência e a não divulgação são registradas pela natureza do valor (RN-MOD-11).
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (Validação antes de publicar); DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 3).
- **Relacionadas:** RN-MOD-11, RN-CFE-15, RN-TER-01

### RN-VPU-03: Se a validação falha, manter o último dado bom
- **Status:** DECIDIDA
- **Regra:** Quando a validação falhar, o pipeline deve manter o último dado bom publicado e abrir uma issue (registro de pendência), e não deve publicar o lote com falha.
- **Motivo:** Uma fonte fora do ar ou um lote ruim não quebra o que o consumidor já vê, e a falha fica registrada.
- **Exemplo:** Se o arquivo da ANM mudar de colunas, o último lote validado continua publicado e a pendência é aberta.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados; PLANO §Arquitetura e fluxo geral.
- **Relacionadas:** RN-VPU-01, RN-VPU-04, RN-ENT-01

### RN-VPU-04: Mudança de colunas da fonte falha o lote
- **Status:** DECIDIDA
- **Regra:** A mudança de colunas ou de formato de um arquivo de fonte deve ser detectada e deve fazer o lote falhar de forma explícita, e nunca deve resultar em publicação silenciosa.
- **Motivo:** Uma mudança de layout pode quebrar o tratamento sem aviso e produzir números errados.
- **Exemplo:** O metadado da ANM para o AMB diz separador ponto e vírgula, mas o arquivo real usa vírgula (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** VAL-15/10 §Marco 2 ("testes de contrato para mudanças de coluna"); PLANO §Riscos e cuidados (Fonte muda o layout do arquivo); DECISÕES §Bloco 3 (VPM).
- **Relacionadas:** RN-VPU-03, RN-FON-18

### RN-VPU-05: Lote bloqueia quando falta mês esperado
- **Status:** DECIDIDA
- **Regra:** Quando um mês esperado estiver ausente, o lote não deve fechar o total do período e deve registrar se a falta é da fonte ou se o município realmente não recebeu.
- **Motivo:** Fechar um total com mês faltante produz um número que parece completo e não é.
- **Exemplo:** O arquivo de distribuição da CFEM tem linhas nacionais de janeiro a junho e de agosto a dezembro de 2025, e nenhuma em julho (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Exceções:** Os meses já presentes podem ser publicados como "provisório" (RN-CFE-06); o que fica bloqueado é o total anual.
- **Fonte:** VAL-15/10 §Marco 2; DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 5).
- **Relacionadas:** RN-CFE-05, RN-CFE-06, RN-CFE-07

### RN-VPU-06: Relatório de qualidade por execução
- **Status:** DECIDIDA
- **Regra:** Cada execução de coleta deve produzir um relatório de qualidade com linhas lidas, municípios presentes, anos, nulos, duplicatas, faixas de valores e divergência com a fonte primária.
- **Motivo:** Permite ver, sem abrir o dado, se o lote cobre o que deveria.
- **Exemplo:** O manifesto da distribuição de 2025 registra o hash da origem, 11 dos 12 municípios presentes e os meses ausentes (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Marco 3; LAB-19/10 §7 (Próximos passos, item 5).
- **Relacionadas:** RN-MOD-21, RN-VPU-11

### RN-VPU-07: Reconciliação independente antes de homologar
- **Status:** DECIDIDA
- **Regra:** Um indicador só deve ser homologado depois de uma reconciliação com publicação independente da fonte oficial; a reconciliação de um mês e de uma modalidade não homologa o ano nem as demais modalidades.
- **Motivo:** O arquivo oficial pode ter lacunas que só aparecem na comparação com outra publicação.
- **Exemplo:** A distribuição de maio de 2025, do tipo `Produtor`, bateu com o PDF da remessa 696 da ANM (emitida em 07/05/2025): Canaã R$ 60.776.801,44, Parauapebas R$ 42.951.670,43 e Marabá R$ 17.289.067,88 (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Exceções:** A tolerância da diferença aceita é zero centavos (RN-VPU-12).
- **Fonte:** VAL-15/10 §Marco 2, §Rodada adicional; CONSUMO §Ordem recomendada para prova de consumo.
- **Relacionadas:** RN-VPU-08, RN-VPU-12, RN-CFE-10

### RN-VPU-08: Somas brutas são provisórias
- **Status:** DECIDIDA
- **Regra:** Somas calculadas sobre o arquivo bruto devem ser tratadas como provisórias e não homologadas até a reconciliação com a fonte oficial.
- **Motivo:** O total do arquivo pode divergir do total oficial publicado.
- **Exemplo:** A soma nacional da arrecadação de 2025 foi R$ 7.910.581.327,56, que arredonda para os R$ 7,91 bilhões do Relatório de Gestão 2025 da ANM; é um controle de escala nacional e arredondado, não uma conferência municipal (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-VPU-07, RN-CFE-12

### RN-VPU-09: Cada ponto exibido leva seus metadados
- **Status:** DECIDIDA
- **Regra:** Cada ponto exibido ao público deve mostrar fonte, unidade, ano de referência, data de atualização e estado de validação, e a ausência não deve aparecer como zero.
- **Motivo:** O leitor precisa julgar o número sem abrir a fonte.
- **Exemplo:** População municipal e CFEM, em painéis separados, mostram os cinco metadados.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3).
- **Relacionadas:** RN-MOD-07, RN-MOD-08, RN-MOD-20

### RN-VPU-10: Só dados homologados alimentam os gráficos
- **Status:** DECIDIDA
- **Regra:** Os gráficos devem consumir apenas dados homologados da camada publicada, e não devem consumir os arquivos nacionais da ANM diretamente.
- **Motivo:** O arquivo bruto pode ter lacunas e campos identificadores.
- **Exemplo:** O CSV de distribuição de 2025 sem julho não pode alimentar um gráfico anual.
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 3).
- **Relacionadas:** RN-ENT-06, RN-VPU-01

### RN-VPU-11: Tratamento de duplicidades
- **Status:** DECIDIDA
- **Regra:** Uma linha duplicada é a que repete todos os campos de outra linha da fonte; quando houver, o lote deve registrar a contagem de repetições no relatório de qualidade e ficar bloqueado até revisão, sem apagar linhas automaticamente.
- **Motivo:** Descartar sozinho pode eliminar um registro real que por acaso repita valor e data, e publicar sem aviso pode inflar o total. Bloquear não custa nada hoje, porque não há linhas idênticas no arquivo de autuações.
- **Exemplo:** Em 27/10/2026, o arquivo de autuações tinha 21.029 linhas, nenhuma idêntica a outra, e a combinação número do auto + processo de cobrança era única em todas. O mesmo vale para as 176 linhas do recorte dos 12 municípios (reproduzido em 27/10/2026: arquivo da ANM).
- **Exceções:** A verificação só foi feita nas autuações; os arquivos de arrecadação e de distribuição não foram testados. Repetir apenas parte dos campos (por exemplo, o mesmo processo de cobrança em duas linhas) não é duplicata e não bloqueia o lote.
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026; VAL-15/10 §Matriz operacional (CFEM autuações).
- **Relacionadas:** RN-VPU-06, RN-CFE-13

### RN-VPU-12: Tolerância da reconciliação
- **Status:** DECIDIDA
- **Regra:** A diferença aceita entre o total do arquivo da fonte, arredondado ao centavo, e a publicação independente deve ser zero; qualquer diferença deve bloquear a homologação daquele recorte.
- **Motivo:** Nos casos conferidos os totais coincidiram ao centavo, e uma tolerância percentual esconderia erros reais em valores altos.
- **Exemplo:** Em maio de 2025, os três totais coincidiram ao centavo (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM). Uma diferença de R$ 0,01 seria tratada como erro e investigada.
- **Exceções:** Se um caso real mostrar diferença só de arredondamento do PDF, a regra pode ser revista pelo mantenedor.
- **Fonte:** DECISÃO-MANTENEDOR de 26/10/2026; VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-VPU-07
