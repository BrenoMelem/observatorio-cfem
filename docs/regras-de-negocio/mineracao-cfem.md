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
- **Exceções:** O ano só fecha com os 12 meses (RN-CFE-06). O mês faz parte do esquema comum (RN-MOD-04).
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
- **Status:** DECIDIDA
- **Regra:** Quando um município não tiver linha num mês em que o arquivo nacional tem linhas, o valor deve ficar como "ausente", nunca zero, com a causa marcada como "não confirmada"; a causa só deve passar a "lacuna da fonte" ou "não recebeu" quando uma publicação independente, como o PDF mensal da ANM, a confirmar.
- **Motivo:** O arquivo não diz por que falta a linha, e presumir uma das causas poderia esconder uma lacuna da extração como se fosse um fato. O relatório de qualidade de cada lote lista os casos (RN-VPU-06).
- **Exemplo:** A falta de julho de 2025 é da fonte (há repasse publicado pela ANM) e vale RN-CFE-06. A falta de São Domingos do Araguaia em todo o arquivo segue com causa não confirmada (RN-CFE-09).
- **Exceções:** Quando o mês inteiro está ausente do arquivo nacional, vale RN-CFE-06, e não esta regra.
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026; VAL-15/10 §Marco 2 (cada lote registra qual das duas situações ocorreu).
- **Relacionadas:** RN-CFE-06, RN-CFE-09, RN-MOD-10, RN-VPU-06

### RN-CFE-08: Recuperar julho de 2025
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve obter julho de 2025 numa publicação oficial da ANM, entender por que o mês falta no CSV e só então liberar o total anual de 2025.
- **Motivo:** Enquanto o mês faltar, o total anual de distribuição de 2025 fica bloqueado.
- **Exemplo:** A rota histórica de tabela municipal da ANM falhou com erro de banco de dados do próprio servidor; o PDF mensal da remessa 696 serviu de controle de maio de 2025 (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Evidência de 31/10/2026 (arquivo de distribuição da ANM baixado em 31/10/2026; só agregados):** julho de 2025 continua ausente: não há linha com `Ano=2025` e `Mês=7`, e o arquivo não foi corrigido desde 24 e 27/10/2026. Os meses de 2025 presentes são 1 a 6 e 8 a 12. O campo `Mês` do CSV é o mês de emissão do repasse: os totais nacionais dos meses 5, 6, 8 e 10 batem com os relatórios de distribuição em PDF da ANM de maio, junho, agosto e outubro de 2025 (por exemplo, junho: R$ 354.438.110,65 no CSV contra R$ 354.438.102,78 no PDF; Canaã dos Carajás e Parauapebas batem ao centavo em junho e agosto). O PDF de julho de 2025 não foi encontrado: dez nomes de arquivo tentados deram 404. A MSC orçamentária do SICONFI registra receita de CFEM (natureza 17125101, fonte 1708) em julho de 2025: Canaã dos Carajás R$ 63,2 milhões, Parauapebas R$ 46,0 milhões e Marabá R$ 17,6 milhões (consulta de 31/10/2026, sem conciliação com a ANM). Hipótese, não verificada: o repasse de julho foi omitido da extração do CSV, possivelmente por troca do processo de geração dos relatórios (a numeração das remessas e o nome dos arquivos mudam entre junho e agosto de 2025). Não se deve afirmar que a ANM não distribuiu em julho. O arquivo tem outras lacunas de mês, nacionalmente: 2013 (mês 6), 2018 (meses 3 e 5), 2019 (mês 9), 2022 (meses 2 a 12) e 2023 (meses 1 a 4 e 6).
- **Fonte:** VAL-15/10 §Marco 2, §Issues sugeridas (item 1).
- **Relacionadas:** RN-CFE-05, RN-VPU-07

### RN-CFE-09: São Domingos do Araguaia sem linhas
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve investigar por que São Domingos do Araguaia (1507151) não tem linha nos arquivos de arrecadação e de distribuição, e até lá o município deve constar como ausente, nunca como zero.
- **Motivo:** A causa não foi confirmada: pode ser lacuna da extração, ausência de repasse ou ausência de atividade.
- **Exemplo:** 11 dos 12 municípios têm linhas em arrecadação (2022–2026) e em distribuição (2007–2026); nas autuações, 9 dos 12 (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM). Em 27/10/2026, o arquivo completo de arrecadação (2002–2026, 2.433.916 linhas) não tinha nenhuma linha de São Domingos do Araguaia, nem pelo código 1507151 nem pelo nome; só aparece São Domingos do Capim (PA, 1507201), outro município, com 1 linha. Isso afasta uma troca de código ou de nome como causa nesse arquivo, mas não confirma a causa real (reproduzido em 27/10/2026: arquivo da ANM).
- **Evidência de 31/10/2026 (arquivos da ANM e API do SICONFI; só agregados):** não há nenhuma linha de São Domingos do Araguaia (1507151) nos arquivos de arrecadação (2.434.016 linhas), distribuição (2.238.876) e autuação (21.029), nem por código nem por nome, com ou sem acento, em nenhum ano; Curionópolis, usada como controle, aparece nos três. O município está cadastrado no SICONFI (população 21.555 em 2026). A MSC orçamentária registra receita de CFEM (natureza 17125101, fonte 1708) desde 2024, em valor pequeno: R$ 31.703,11 em 2024 (meses 2 e 5), R$ 58.851,88 em 2025 (meses 11 e 12) e R$ 22.570,78 em 2026 (janeiro a agosto), e nada em 2022 e 2023; a título de comparação, a MSC de Curionópolis soma R$ 47,8 milhões em 2025. Isso afasta "sem repasse nenhum" desde 2024 e afasta troca de código ou de nome, mas não prova falha do arquivo: a situação é indeterminada, com indício de divergência entre o Tesouro e a ANM. Hipóteses, não verificadas: o valor vem de uma modalidade ou beneficiário que a ANM não publica por município, ou de outra via de repasse, ou de lacuna da extração. Só a ANM pode confirmar a causa.
- **Fonte:** VAL-15/10 §Matriz operacional, §Rodada adicional, §Issues sugeridas (item 2).
- **Relacionadas:** RN-MOD-10, RN-CFE-07

### RN-CFE-10: Modalidades de distribuição que compõem a CFEM recebida
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir quais modalidades de distribuição (coluna do tipo de distribuição) compõem a "CFEM recebida", e até lá a modalidade deve ser guardada e exibida separadamente.
- **Motivo:** A reconciliação cobriu só o tipo `Produtor`; as demais modalidades não foram conferidas.
- **Exemplo:** A reconciliação de maio de 2025 foi feita com `Ano=2025`, `Mês=5` e tipo `Produtor` (transcrito do relatório VAL-15/10; reproduzido em 25/10/2026: arquivos da ANM). Em 27/10/2026, o arquivo de distribuição tinha três modalidades: `Produtor` (2007–2026, só municípios), `Afetado` (2019–2022, só municípios, com subtipos como estrutura de mineração, ferrovias e perda) e `-` (2019–2022, só estados). De 2023 a 2026 existe só `Produtor`, que somou R$ 1.556.820.292,67 nos 12 municípios em 2025; a soma é bruta e provisória (reproduzido em 27/10/2026: arquivo da ANM).
- **Evidência de 31/10/2026 (distribuição da ANM contra a MSC orçamentária, receita realizada da fonte 1708; só agregados):** o tipo `Produtor` reproduz a receita registrada em Canaã dos Carajás (diferença de 0,03% a 0,04% por ano, 2024 a 2026) e em Parauapebas (0,14% a 0,38%), mas não em Marabá, onde a receita registrada é maior que o `Produtor` em 7% a 26% (2024 a 2026); Marabá usa a natureza 17225101, enquanto os outros dois usam a 17125101. A modalidade `-` só existe para entes estaduais (2019 a 2022) e não tem linha em nenhum dos três municípios. `Afetado` só existe no arquivo até 2022 e só pôde ser testado nesse ano, de forma anual e inconclusiva (em Marabá, `Produtor` mais `Afetado` aproxima a MSC; em Canaã e Parauapebas não muda o resultado). O arquivo da ANM tem defeitos de calendário que impedem a comparação mensal em 2022 (todo o `Produtor` está no mês 1) e em 2023 (faltam os meses 1 a 4 e 6), e julho de 2025 é ausente (RN-CFE-08). A natureza 17125101 da fonte 1708 não é só CFEM: a fonte tem valores pequenos de outras naturezas. Causas da diferença em Marabá e da pequena diferença em Parauapebas não foram verificadas. A comparação de 2019 a 2021 não foi feita porque a MSC usa outra estrutura de fonte e natureza nesses anos.
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
- **Status:** DECIDIDA
- **Regra:** As autuações sem ano de publicação aparecem numa faixa "sem ano", separada e visível, ao lado da série anual. A série anual contém só as autuações com ano, e o total de autuações inclui as duas partes. Nenhum ano é inferido por outro campo.
- **Motivo:** Decisão do mantenedor. As sem ano pesam muito: em 31/10/2026 são 87 de 171 linhas do recorte dos 12 municípios (51%) e 87,3% do valor (R$ 13,26 bi de R$ 15,20 bi); tirá-las da série subestimaria o total sem aviso, e o ano do número do processo é o ano de abertura, não o da publicação (contrária a RN-CFE-14).
- **Exemplo:** Em Canaã dos Carajás e Curionópolis, mais de 99% do valor das autuações do recorte está sem ano. 81 das 87 linhas sem ano têm número de processo de 2006 a 2011 e seis têm número de 2026 (R$ 11,7 bi, 88% do valor sem ano) (calculado em 31/10/2026 sobre o arquivo da ANM; só agregados; a interpretação do número do processo é hipótese não confirmada pela ANM).
- **Exceções:** RN-CFE-02 e RN-CFE-17 continuam valendo: autuação nunca se soma à arrecadada nem à recebida, e não é valor devido nem arrecadado. A contagem do recorte mudou de 176 (88 sem ano), em 25 e 27/10/2026, para 171 (87 sem ano), em 31/10/2026; a causa não foi investigada (hipótese: o arquivo da ANM foi atualizado). Só 7 dos 12 municípios têm autuação; o arquivo não traz código IBGE, só o nome do município.
- **Fonte:** DECISÃO-MANTENEDOR de 31/10/2026; VAL-15/10 §Matriz operacional, §Rodada adicional; DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 6: deixar em aberto, agora superada).
- **Relacionadas:** RN-CFE-13, RN-CFE-14, RN-CFE-17, RN-MOD-10

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

### RN-CFE-22: Arquivo e cobertura histórica da arrecadação
- **Status:** DECIDIDA
- **Regra:** A arrecadação da CFEM deve ser coletada do arquivo completo de arrecadação da ANM (`CFEM_Arrecadacao.csv`), com a série começando em 2003.
- **Motivo:** O arquivo completo é o citado em DECISÕES e já cobre todos os anos; o de 2022–2026, usado pelo validador, descartaria 20 anos de série. O ano 2002 tem só 10 linhas no país, o que sugere cobertura incompleta (dedução: a ANM não diz isso).
- **Exemplo:** Em 27/10/2026, o arquivo completo tinha 2.433.916 linhas, de 2002 a 2026; 2003 tem 30.559 linhas. A ANM publica também arquivos por faixa de anos (2002–2006, 2007–2011, 2012–2016, 2017–2021, 2022–2026), e as contagens por ano de 2022 a 2026 são iguais no arquivo completo e no de 2022–2026 (reproduzido em 27/10/2026: arquivos da ANM).
- **Exceções:** O validador atual usa o arquivo de 2022–2026 e precisa passar a usar o completo. A cobertura municipal dos anos anteriores a 2022 não foi verificada.
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026; DECISÕES §Rotas de coleta por fonte; SCRIPTS (`validate_anm_cfem`); VAL-15/10 §Rodada adicional; consulta ao servidor da ANM em 27/10/2026.
- **Relacionadas:** RN-CFE-01, RN-FNT-18

### RN-CFE-23: Cobertura parcial de Bom Jesus do Tocantins na arrecadação de 2025
- **Status:** PROPOSTA
- **Regra:** Os meses sem linha de Bom Jesus do Tocantins (1501576) na arrecadação de 2025 devem ser registrados como `ausente`, nunca como zero; a causa e a completude municipal do ano dependem de publicação independente da ANM.
- **Motivo:** Ausência de linha não comprova arrecadação zero nem erro da fonte.
- **Exemplo:** O briefing de 30/10/2026 relata ausência em 2025; a leitura do CSV completo da ANM em 30/10/2026 encontrou janeiro, mas não fevereiro a dezembro. A causa da divergência ainda não foi confirmada.
- **Fonte:** Briefing operacional de 30/10/2026, §9; leitura local do `CFEM_Arrecadacao.csv` em 30/10/2026, relatório `output/observatorio/tratado/cfem/relatorio.json`.
- **Relacionadas:** RN-CFE-07, RN-CFE-22, RN-VPU-06

### RN-CFE-24: Despesa municipal financiada por CFEM exige identificação da fonte de recursos
- **Status:** PROPOSTA
- **Regra:** Um indicador de despesa financiada por CFEM só deve ser criado após confirmar o código de fonte de recursos na despesa executada, a cobertura dos períodos e a extração reproduzível; dados agregados de CFEM recebida e de despesa por função não devem ser usados para afirmar financiamento direto.
- **Motivo:** ANM registra a receita e SICONFI registra despesa agregada do orçamento, sem vincular cada despesa à receita CFEM.
- **Exemplo:** `17080000` aparece em previsão orçamentária de Canaã dos Carajás em 2023/2024, enquanto `1708000` também foi encontrado; nenhum foi confirmado como filtro da despesa executada.
- **Fonte:** Briefing operacional de 30/10/2026, §9; verificação independente nos portais municipais ainda pendente.
- **Nota de evidência de 31/10/2026 (sem mudar o status):** a MSC orçamentária do SICONFI (classe 6, 2022–2026, 12 municípios) traz o código de fonte de recursos com 4 dígitos em todas as linhas (nenhum com 7 ou 8 dígitos), e a fonte `1708` aparece nas despesas de 10 dos 12 municípios (detalhes em RN-FNT-04). A observação de que a `1708` identifica a CFEM recebida e bate com a distribuição da ANM (Canaã dos Carajás, 2026, abril e junho idênticos ao centavo) foi relatada na sessão de 31/10/2026 e não foi reproduzida nesta consulta. A cobertura de meses é incompleta em alguns meses truncados e em 2026, o mapeamento de estágios não foi feito e a conciliação com a DCA não foi feita; a regra continua `PROPOSTA`.
- **Relacionadas:** RN-FNT-04, RN-FON-05, RN-FON-06

### RN-CFE-25: Percentuais legais da repartição da CFEM
- **Status:** DECIDIDA
- **Regra:** A repartição legal da CFEM arrecadada deve seguir os percentuais abaixo, aplicados conforme o ano de referência da arrecadação.
  - Até 2017 (Lei 8.001/1990, art. 2º, § 2º, redação da Lei 9.993/2000): 65% para os municípios, 23% para os Estados e o Distrito Federal, 2% para o FNDCT e 10% para o Ministério de Minas e Energia, repassados ao DNPM, que destinava 2% dessa cota ao Ibama. Em pontos percentuais do total: DNPM 9,8, FNDCT 2 e Ibama 0,2, ou seja, 12% para a União. Não havia cota para municípios afetados.
  - Desde 2018 (Lei 13.540/2017, que deu nova redação ao mesmo parágrafo): 60% para o município onde ocorre a produção, 15% para o Estado e o Distrito Federal onde ocorre a produção, 15% para os municípios afetados e 10% para a União (ANM 7%, FNDCT 1%, Cetem 1,8% e Ibama 0,2%).
- **Motivo:** O mantenedor mandou seguir os percentuais usados na `obcefem_api`, e o texto das duas leis confere com eles.
- **Exemplo:** Para R$ 100,00 arrecadados em 2019, o município produtor corresponde a R$ 60,00 e a União a R$ 10,00 (conta ilustrativa, não é dado da ANM).
- **Exceções:** (1) A Lei 13.540/2017, art. 4º, III, diz que os demais dispositivos entram em vigor em 01/08/2017; a `obcefem_api` troca de regra em 2018. O tratamento dos meses de agosto a dezembro de 2017 está em aberto (ver `pendencias.md`, seção 2). (2) Pelo § 3º do art. 2º, quando não houver município afetado nas hipóteses do inciso VII, ou enquanto o decreto não for editado, a cota dos afetados vai ao Estado; a redação do § 3º foi alterada pela Lei 14.514/2022. A `obcefem_api` atribui os 15% a "afetados" em todos os anos desde 2018, e a observação dela diz que os repasses só começaram depois do Decreto 9.407/2018. O tratamento de 2018 em diante está em aberto. (3) O art. 2º, § 6º, prevê que, preferencialmente, ao menos 20% das cotas de Estados e municípios produtores sejam usados em diversificação econômica, desenvolvimento mineral sustentável e ciência e tecnologia; não é percentual de repartição.
- **Fonte:** DECISÃO-MANTENEDOR de 08/11/2026 (seguir a `obcefem_api`); Lei 8.001/1990, art. 2º, § 2º, com as redações das Leis 9.993/2000 e 13.540/2017 (texto lido em 08/11/2026 nos arquivos `L8001.html` e `L13540.html` do Planalto, fornecidos pelo mantenedor).
- **Relacionadas:** RN-CFE-02, RN-CFE-03, RN-CFE-26

### RN-CFE-26: Estimativa pela lei é análise derivada, separada da CFEM recebida
- **Status:** DECIDIDA
- **Regra:** O valor calculado pela repartição legal (arrecadação × percentual de RN-CFE-25) pode ser exibido como "estimativa" e deve ser tratado como análise derivada; não substitui a CFEM recebida do arquivo de distribuição da ANM, que continua sendo a medida de RN-CFE-03, e as duas não devem aparecer no mesmo eixo sem aviso.
- **Motivo:** A estimativa responde "quanto caberia pela lei" e a distribuição responde "quanto o ente recebeu"; a `obcefem_api` já prevê mostrar o repasse efetivo ao lado da estimativa quando a ANM normalizar o arquivo.
- **Exemplo:** A `obcefem_api` afirma que o arquivo de distribuição de 01/11/2026 tinha a cota municipal de 2023 a 2025 em cerca de 15% do arrecadado (não reproduzido aqui). A nota de 31/10/2026 em RN-CFE-10 mostra o tipo `Produtor` batendo com a MSC em Canaã dos Carajás e Parauapebas; as duas leituras precisam ser conciliadas antes de usar a estimativa como substituta da recebida.
- **Fonte:** DECISÃO-MANTENEDOR de 08/11/2026; `obcefem_api`, README §Distribuição; RN-IND-05.
- **Relacionadas:** RN-CFE-02, RN-CFE-03, RN-CFE-10, RN-CFE-25, RN-IND-05
