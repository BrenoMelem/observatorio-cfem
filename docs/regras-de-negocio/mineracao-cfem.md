# Mineração e CFEM

Regras do Bloco 3 do observatório: CFEM arrecadada, CFEM recebida (distribuição), autuações e valor da produção mineral (VPM). Legenda de status e siglas das fontes: [README](README.md).

## As três medidas da CFEM

As três medidas vêm da ANM em CSVs nacionais, filtrados pelos municípios de interesse. São medidas distintas e nunca se somam.

| Medida | Arquivo da ANM | Chave municipal | O que representa |
| --- | --- | --- | --- |
| Arrecadação | `CFEM_Arrecadacao.csv` | `CodigoMunicipio` | Royalty gerado pela extração no município de origem |
| Distribuição (CFEM recebida) | `CFEM_Distribuicao.csv` | `CodigoEnte` | Repasse que cada município recebe |
| Autuação | `CFEM_Autuacao.csv` (separador `;`) | `Município`, por nome | Cobrança lançada pela fiscalização; acusação com valor, não dinheiro em caixa |

Fonte: DECISÕES §Rotas de coleta por fonte, §Glossário; BLOCOS §Bloco 3; LAB-19/10 §4 (ANM CFEM).

### RN-CFE-01: Fonte única, a ANM
- **Status:** DECIDIDA
- **Regra:** A CFEM arrecadada, a CFEM recebida e as autuações devem vir exclusivamente da ANM, dos arquivos nacionais de dados abertos, filtrados pelos municípios de interesse.
- **Motivo:** Uma só fonte evita divergência entre as três medidas e permite comparar com outros municípios mineradores sem fonte nova.
- **Exemplo:** Para Canaã dos Carajás (1502152), o arquivo de arrecadação 2022–2026 tem 251 linhas, o de distribuição 739 e o de autuação 11 (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3; VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-CFE-02, RN-TER-09

### RN-CFE-02: Arrecadada, recebida e autuação nunca se somam
- **Status:** DECIDIDA
- **Regra:** A CFEM arrecadada, a CFEM recebida e as autuações não devem ser somadas entre si nem exibidas no mesmo eixo sem aviso, e a arrecadada e a recebida devem aparecer como indicadores distintos.
- **Motivo:** São medidas de natureza diferente: o que a extração gerou, o repasse efetivo e uma cobrança ainda sujeita a recurso.
- **Exemplo:** Em maio de 2025, o repasse do tipo `Produtor` a Canaã foi R$ 60.776.801,44, e isso não é o que as empresas recolheram em Canaã naquele mês (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3; LAB-19/10 §4 (ANM CFEM); CONSUMO §CFEM e receitas minerais.
- **Relacionadas:** RN-CFE-03, RN-CFE-17, RN-ENT-09

### RN-CFE-03: Arrecadação é do município de origem; distribuição é do ente que recebe
- **Status:** DECIDIDA
- **Regra:** A arrecadação deve ser atribuída ao município onde ocorreu a extração, e a distribuição deve ser atribuída ao ente que recebe o repasse; uma não deve ser usada no lugar da outra.
- **Motivo:** O município que arrecada pode não ser o que recebe o valor, e dizer o contrário distorce a leitura da dependência fiscal.
- **Exemplo:** A arrecadação filtra por `CodigoMunicipio`; a distribuição, por `CodigoEnte`.
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3; CONSUMO §CFEM e receitas minerais.
- **Relacionadas:** RN-CFE-02

### RN-CFE-04: Guardar por mês, exibir por ano
- **Status:** DECIDIDA
- **Regra:** A CFEM deve ser guardada no detalhe mensal, e o gráfico deve agregá-la para o ano.
- **Motivo:** O arquivo vem por mês, e o detalhe mensal permite reconciliar e detectar mês ausente.
- **Exemplo:** A distribuição de 2025 é guardada por município, mês e modalidade e somada por ano só na exibição (quando o ano fecha).
- **Exceções:** O ano só fecha com os 12 meses (RN-CFE-06). O campo de mês no esquema comum está em aberto (RN-MOD-04).
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3.
- **Relacionadas:** RN-MOD-04, RN-MOD-05, RN-CFE-06

### RN-CFE-05: Não somar total anual com mês ausente
- **Status:** DECIDIDA
- **Regra:** O total anual da CFEM não deve ser calculado nem publicado quando algum mês do ano estiver ausente na fonte.
- **Motivo:** Somar com um mês faltando produz um total que parece completo e não é.
- **Exemplo:** O CSV de distribuição não tem nenhuma linha de julho de 2025, mas a ANM publicou que repassou R$ 478.839.591,45 em julho de 2025 aos estados e municípios produtores; por isso o total anual de distribuição de 2025 está bloqueado (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivo da ANM e notícia da ANM).
- **Fonte:** VAL-15/10 §Resposta ao orientador (item 1), §Marco 2, §Rodada adicional; CONSUMO §Validação complementar de 15/10/2026.
- **Relacionadas:** RN-CFE-06, RN-CFE-08, RN-VPU-05, RN-MOD-08

### RN-CFE-06: O ano só fecha com os 12 meses; meses disponíveis saem como provisórios
- **Status:** DECIDIDA
- **Regra:** O ano de CFEM só deve ser considerado fechado quando o arquivo nacional tiver os 12 meses, e os meses já presentes podem ser publicados individualmente com o estado de validação "provisório".
- **Motivo:** Equilibra a regra de não somar com mês ausente com a utilidade de mostrar o que já existe.
- **Exemplo:** Em 2025, janeiro a junho e agosto a dezembro podem ser exibidos como provisórios, mas o total anual fica bloqueado até julho ser incorporado e reconciliado.
- **Exceções:** O critério vale para "mês sem nenhuma linha no arquivo nacional". Ausência de um município específico num mês que existe no arquivo é tratada em RN-CFE-07.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 5); VAL-15/10 §Marco 2 (que prevê bloquear a publicação do lote com mês ausente; esta decisão restringe o bloqueio ao total anual).
- **Relacionadas:** RN-CFE-05, RN-MOD-07, RN-TMP-12, RN-VPU-05

### RN-CFE-07: Ausência de um município num mês existente no arquivo
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir como classificar a falta de linha de um município num mês em que o arquivo nacional tem linhas: lacuna da fonte ou município que não recebeu.
- **Motivo:** VAL-15/10 pede que cada lote registre qual das duas situações ocorreu, mas nenhuma fonte define o critério operacional.
- **Exemplo:** A falta de julho de 2025 é da fonte (há repasse publicado pela ANM). A falta de São Domingos do Araguaia em todo o arquivo não tem causa confirmada (RN-CFE-09).
- **Fonte:** VAL-15/10 §Marco 2.
- **Relacionadas:** RN-CFE-06, RN-CFE-09, RN-MOD-10

### RN-CFE-08: Recuperar julho de 2025
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve obter julho de 2025 numa publicação oficial da ANM, entender por que o mês falta no CSV e só então liberar o total anual de 2025.
- **Motivo:** Enquanto o mês faltar, o total anual de distribuição de 2025 fica bloqueado.
- **Exemplo:** A rota histórica de tabela municipal da ANM falhou com erro de banco de dados do próprio servidor; o PDF mensal da remessa 696 serviu de controle de maio de 2025 (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** VAL-15/10 §Marco 2, §Issues sugeridas (item 1).
- **Relacionadas:** RN-CFE-05, RN-VPU-07

### RN-CFE-09: São Domingos do Araguaia sem linhas
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve investigar por que São Domingos do Araguaia (1507151) não tem linha nos arquivos de arrecadação e de distribuição, e até lá o município deve constar como ausente, nunca como zero.
- **Motivo:** A causa não foi confirmada: pode ser lacuna da extração, ausência de repasse ou ausência de atividade.
- **Exemplo:** 11 dos 12 municípios têm linhas em arrecadação (2022–2026) e em distribuição (2007–2026); nas autuações, 9 dos 12 (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Matriz operacional, §Rodada adicional, §Issues sugeridas (item 2).
- **Relacionadas:** RN-MOD-10, RN-CFE-07

### RN-CFE-10: Modalidades de distribuição que compõem a CFEM recebida
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir quais modalidades de distribuição (coluna do tipo de distribuição) compõem a "CFEM recebida", e até lá a modalidade deve ser guardada e exibida separadamente.
- **Motivo:** A reconciliação cobriu só o tipo `Produtor`; as demais modalidades não foram conferidas.
- **Exemplo:** A reconciliação de maio de 2025 foi feita com `Ano=2025`, `Mês=5` e tipo `Produtor` (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Rodada adicional (escopo da reconciliação).
- **Relacionadas:** RN-VPU-07, RN-TER-09, RN-CFE-11

### RN-CFE-11: Agregação por município, ano, mês e modalidade
- **Status:** PROPOSTA
- **Regra:** Os valores devem ser somados em precisão decimal por código IBGE, ano, mês e modalidade de distribuição, e só depois arredondados ao centavo, para cima a partir da metade.
- **Motivo:** Evita erro de arredondamento acumulado e preserva a modalidade.
- **Exemplo:** O primeiro importador gerou 75 linhas municipais agregadas de 2025, com código IBGE, município, ano, mês, modalidade, valor e contagem de linhas (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** SCRIPTS (`build_cfem_distribution_municipal`). Deduzida do código.
- **Relacionadas:** RN-CFE-04, RN-CFE-10

### RN-CFE-12: Controle de escala com o total nacional
- **Status:** PROPOSTA
- **Regra:** O total nacional de uma medida deve ser comparado com o total publicado pela ANM como controle de escala, sem substituir a conferência municipal.
- **Motivo:** Detecta erro grosseiro de leitura do arquivo.
- **Exemplo:** A soma nacional da arrecadação de 2025 foi R$ 7.910.581.327,56, que arredonda para os R$ 7,91 bilhões do Relatório de Gestão 2025 da ANM (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Rodada adicional (apresentado como controle, não como regra).
- **Relacionadas:** RN-VPU-08

### RN-CFE-13: Autuação guardada como evento
- **Status:** DECIDIDA
- **Regra:** Cada autuação deve ser guardada como um evento (data de publicação, valor, processo, município e titular), e a série do gráfico deve ser derivada dos eventos.
- **Motivo:** O evento preserva o detalhe; a série é só uma visão.
- **Exemplo:** O arquivo completo tem 21.029 linhas; 176 estão no recorte dos 12 municípios (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3 (Autuações).
- **Relacionadas:** RN-CFE-14, RN-CFE-16, RN-TER-06

### RN-CFE-14: A série de autuações usa a data de lavratura
- **Status:** DECIDIDA
- **Regra:** A série de autuações deve usar a data de lavratura, que é a data de publicação trazida pelo arquivo, e não o fato gerador.
- **Motivo:** O arquivo não traz o fato gerador, e a data de lavratura é também a mais honesta para o observatório.
- **Exemplo:** O ano de lavratura é o ano em que a ANM emitiu a autuação; o fato gerador é o ano em que o débito se originou.
- **Fonte:** DECISÕES §Bloco 3 (Data da autuação), §Glossário (lavratura, fato gerador); BLOCOS §Bloco 3.
- **Relacionadas:** RN-CFE-13, RN-CFE-16

### RN-CFE-15: Autuações podem diminuir na série
- **Status:** DECIDIDA
- **Regra:** A validação "a série não encolheu" não deve ser aplicada às autuações.
- **Motivo:** As autuações diminuem legitimamente em recurso; é uma nota técnica, não uma decisão de negócio.
- **Exemplo:** Uma autuação cancelada em recurso reduz o total da série sem ser erro.
- **Fonte:** DECISÕES §Arquitetura e padrões de dados, §Bloco 3; BLOCOS §Bloco 3.
- **Relacionadas:** RN-VPU-02

### RN-CFE-16: Autuação sem ano de publicação
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir o tratamento das autuações sem ano de publicação antes de formar a série temporal.
- **Motivo:** VAL-15/10 aponta que não se deve formar série sem regra para esses registros.
- **Exemplo:** 88 das 176 linhas do recorte dos 12 municípios não têm ano de publicação (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM).
- **Fonte:** VAL-15/10 §Matriz operacional, §Rodada adicional; DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 6: deixar em aberto).
- **Relacionadas:** RN-CFE-13, RN-CFE-14, RN-MOD-10

### RN-CFE-17: Autuação é cobrança, não receita
- **Status:** DECIDIDA
- **Regra:** A autuação não deve ser tratada como dinheiro em caixa, e como o arquivo não traz a situação do processo (pago, em recurso, cancelado), nenhum valor de autuação deve ser apresentado como valor devido ou arrecadado.
- **Motivo:** É uma acusação com valor, sujeita a recurso.
- **Exemplo:** O arquivo de autuação não tem coluna de situação do processo.
- **Fonte:** DECISÕES §Bloco 3, §Glossário (autuação); BLOCOS §Bloco 3.
- **Relacionadas:** RN-CFE-02, RN-CFE-18

### RN-CFE-18: Nome da empresa autuada: guardar agora, exibir depois
- **Status:** DECIDIDA
- **Regra:** O nome da empresa autuada (campo `NomeTitular`) deve ser guardado na tabela de eventos, e a decisão de exibi-lo no site deve ficar adiada até a publicação se aproximar, com revisão jurídica antes.
- **Motivo:** Expor uma acusação ainda não julgada tem risco jurídico, e o projeto ainda não está no ar.
- **Exemplo:** Cada evento de autuação guarda processo, titular, município, substância e valor.
- **Exceções:** A decisão final de exibir ou não o nome continua **EM ABERTO** até a revisão jurídica. CPF e CNPJ nunca são guardados na camada tratada (RN-PRI-01).
- **Fonte:** DECISÕES §Bloco 3, §Publicação e extras; BLOCOS §Bloco 3.
- **Relacionadas:** RN-CFE-13, RN-PRI-01

### RN-CFE-19: O VPM só existe por UF
- **Status:** DECIDIDA
- **Regra:** O valor da produção mineral (VPM) não deve ser publicado como indicador de município nem prometido como municipal, e pode ser exibido apenas como contexto do estado do Pará.
- **Motivo:** Os arquivos do AMB (`Producao_Bruta.csv` e `Producao_Beneficiada.csv`) não têm coluna de município.
- **Exemplo:** O cabeçalho real tem ano base, UF, classe de substância, quantidades e valores, e nenhuma coluna municipal.
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3; LAB-19/10 §4 (ANM AMB e VPM).
- **Relacionadas:** RN-CFE-20, RN-FON-18

### RN-CFE-20: A CFEM como proxy da produção municipal
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve decidir se a CFEM pode ser apresentada como proxy da produção municipal, ou se deve ser exibida apenas como CFEM, sem rótulo de VPM.
- **Motivo:** As fontes divergem.
- **Exemplo:** A CFEM é base de cálculo derivada do VPM, mas é um repasse financeiro, não uma medida de produção.
- **Fonte:** Versão A: DECISÕES §Bloco 3 e BLOCOS §Bloco 3 (a CFEM "serve de proxy da produção municipal"; 04/10/2026, última edição 20/10/2026). Versão B: LAB-19/10 §4 (a CFEM municipal "pode ser analisada separadamente, sem renomeá-la como VPM"; 19/10/2026); VAL-15/10 §Matriz operacional (pesquisar fonte oficial alternativa antes de prometer VPM municipal; 15/10/2026).
- **Relacionadas:** RN-CFE-19, RN-CFE-21

### RN-CFE-21: A CFEM vem pronta e não é recalculada
- **Status:** DECIDIDA
- **Regra:** O valor da CFEM arrecadada deve ser o do arquivo da ANM e não deve ser recalculado pela fórmula base de cálculo × alíquota.
- **Motivo:** A fórmula explica o indicador, mas o arquivo já traz o valor pronto.
- **Exemplo:** CFEM = base de cálculo (faturamento da venda menos tributos sobre a comercialização) × alíquota por substância, conforme a Lei 13.540/2017; para o minério de ferro a faixa é de cerca de 3,5%, a conferir na lei.
- **Fonte:** DECISÕES §Bloco 3 (Como a CFEM é calculada); BLOCOS §Bloco 3 (Cálculo).
- **Relacionadas:** RN-CFE-19

### RN-CFE-22: Cobertura histórica da arrecadação
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve confirmar qual arquivo e qual cobertura de anos da arrecadação a ANM publica antes de prometer série longa.
- **Motivo:** DECISÕES cita `CFEM_Arrecadacao.csv`, mas o validador usou `CFEM_Arrecadacao_2022_2026.csv`, que cobre apenas 2022–2026.
- **Exemplo:** O arquivo 2022–2026 tinha 744.244 linhas em 15/10/2026 (transcrito do relatório VAL-15/10) e 744.279 em 25/10/2026, depois da atualização da ANM de 24/10/2026; as 2.534 linhas dos 12 municípios não mudaram (reproduzido em 25/10/2026).
- **Fonte:** DECISÕES §Rotas de coleta por fonte; SCRIPTS (`validate_anm_cfem`); VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-CFE-01, RN-FNT-18
