# Indicadores derivados e compostos

Regras sobre indicadores calculados pelo observatório a partir de outros (derivados) e sobre os índices publicados por terceiros que entram congelados (compostos). Legenda de status e siglas das fontes: [README](README.md).

## Indicadores compostos

| Indicador | Fonte | Estratégia | Promovível a recalculado? |
| --- | --- | --- | --- |
| Relação receita per capita × IDSC (grupos AA, AB, BA, BB) | IPEA, TD 3146 (2025) | Congelado | Sim, é candidato real |
| Barômetro da Sustentabilidade | FAPESPA | Congelado | Não |
| Ranking de competitividade | CLP | Congelado | Não |

Fonte: DECISÕES §Indicadores compostos; BLOCOS §Bloco 6.

### RN-IND-01: Compostos entram congelados, com citação e marca de promovível
- **Status:** DECIDIDA
- **Regra:** Os três indicadores compostos devem entrar congelados, com citação da fonte e do ano, e cada um deve ter no manifesto a marca de estratégia "congelado" e a marca "promovível" (sim ou não).
- **Motivo:** Congelar não é deixar de fora: o número aparece com fonte e ano; a diferença é se é uma foto, atualizada à mão a cada edição, ou um cálculo vivo. A marca impede que a ressalva se perca.
- **Exemplo:** O Barômetro da Sustentabilidade 2024 (FAPESPA) consta como congelado e não promovível.
- **Fonte:** DECISÕES §Indicadores compostos; BLOCOS §Bloco 6.
- **Relacionadas:** RN-MOD-25, RN-IND-02, RN-IND-04

### RN-IND-02: A relação do IPEA é a única candidata a recálculo
- **Status:** DECIDIDA
- **Regra:** A relação receita per capita × IDSC (IPEA, TD 3146) deve ser tratada como candidata a recalculado e só deve ser promovida depois que o SICONFI estiver rodando.
- **Motivo:** É uma classificação 2×2 simples que usa dados que o projeto já terá: receita per capita (SICONFI ÷ população) e nota do IDSC.
- **Exemplo:** Quatro quadrantes (AA, AB, BA, BB) conforme receita per capita e IDSC altos ou baixos.
- **Fonte:** DECISÕES §Indicadores compostos; BLOCOS §Bloco 6.
- **Relacionadas:** RN-IND-03, RN-FNT-04

### RN-IND-03: Corte do TD 3146
- **Status:** DECIDIDA
- **Regra:** A classificação receita per capita × IDSC segue o método do TD 3146: o corte de "alto" e "baixo" em cada eixo é a média nacional simples de 2022, isto é, R$ 6.880,37 de receita per capita e 46,925 de IDSC. Esses cortes ficam congelados em 2022: o IPEA não os atualiza, e a classificação só é comparável ao estudo para 2022. Qualquer outro ano é cálculo do projeto, deve ser identificado como tal e não é comparável ao IPEA.
- **Motivo:** Decisão do mantenedor, para que o resultado recalculado bata com o do IPEA. O corte vem da leitura do TD 3146 (média nacional simples de 2022).
- **Exemplo:** A faixa AB corresponde a receita per capita acima de R$ 6.880,37 e IDSC abaixo de 46,925.
- **Evidência datada:** no fim deste arquivo, em [Notas de evidência](#notas-de-evidência), sob RN-IND-03.
- **Exceções:** Não foi verificado se a "receita bruta" do Finbra, usada pelo IPEA, coincide com a que o SICONFI (DCA) fornece ao projeto; o número recalculado pode divergir um pouco do do IPEA. A relação só pode ser publicada depois que o SICONFI estiver coletado. Se o projeto adotar um corte recalculado por ano, isso exige nova decisão.
- **Fonte:** DECISÃO-MANTENEDOR de 02/11/2026; IPEA, Texto para Discussão 3146 (29/07/2025); DECISÕES §Indicadores compostos, §Pré-requisitos e pendências.
- **Relacionadas:** RN-IND-02

### RN-IND-04: Barômetro e CLP ficam congelados sem previsão
- **Status:** DECIDIDA
- **Regra:** O Barômetro da Sustentabilidade e o ranking de competitividade da CLP devem ser tratados como dado que a entidade publica, e não como dado que o observatório calcula.
- **Motivo:** O Barômetro (metodologia Prescott-Allen) é pesado demais para um item anual; o ranking da CLP usa pesos proprietários, e reproduzi-lo sem a documentação completa é inviável.
- **Exemplo:** O ranking de competitividade de Canaã dos Carajás é reproduzido com citação, sem recálculo.
- **Fonte:** DECISÕES §Indicadores compostos; BLOCOS §Bloco 6.
- **Relacionadas:** RN-IND-01, RN-IND-08

### RN-IND-05: Derivado ou composto é marcado como análise derivada
- **Status:** PROPOSTA
- **Regra:** Todo indicador composto ou derivado deve ser marcado como análise derivada e não como indicador oficial contínuo, guardando o ano de referência, os cortes, o deflator e a regra de classificação.
- **Motivo:** Evita que uma conclusão de estudo seja lida como série oficial.
- **Exemplo:** A relação do TD 3146 guarda o ano de referência, os cortes de receita e de IDSC e a regra de classificação.
- **Fonte:** CONSUMO §Finanças públicas e índices (receita per capita e IDSC). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-IND-01, RN-MOD-17

### RN-IND-06: Mineração × cobertura florestal é derivado próprio
- **Status:** DECIDIDA
- **Regra:** A área de mineração versus cobertura florestal deve ser calculada pelo observatório, por município e ano, a partir das classes de mineração e de floresta do MapBiomas, sem fonte nova.
- **Motivo:** Mostra o avanço da mineração sobre a floresta, pertinente para Canaã dos Carajás e Parauapebas, com dados que o bloco ambiental já tem.
- **Exemplo:** Mineração e floresta de Canaã dos Carajás (1502152), por ano, de 1985 a 2025.
- **Exceções:** As classes que formam "floresta", "mineração" e "área urbana" estão decididas em RN-IND-11; o denominador e o limite municipal estão em RN-IND-13.
- **Fonte:** DECISÕES §Área de mineração × cobertura florestal; BLOCOS §Bloco 5.
- **Relacionadas:** RN-IND-11, RN-TMP-07

### RN-IND-07: Denominador do emprego formal como proporção da população
- **Status:** DECIDIDA
- **Regra:** O emprego formal é publicado como dois indicadores separados, sem misturar os denominadores: (1) emprego formal ÷ população total, com a estimativa anual de população do IBGE, em toda a série; e (2) emprego formal ÷ população em idade ativa, de 15 a 64 anos, pelo Censo 2022, só para 2022. A mesma regra vale para todos os territórios. A idade ativa de outros anos fica fora até haver uma fonte decidida.
- **Motivo:** O mantenedor orientou, em 27/10/2026, incluir a população em idade ativa. A estimativa anual do IBGE traz só o total por município, e o Censo 2022 traz a população por idade. Dois indicadores atendem à orientação sem deixar a série anual vazia, no mesmo padrão de RN-IND-09 e RN-IND-12.
- **Exemplo:** A RAIS mede vínculos formais (estoque). Pelo Censo 2022, Canaã dos Carajás tem 77.079 habitantes, dos quais 53.714 (69,7%) têm de 15 a 64 anos (consulta ao SIDRA, tabela 9514, em 02/11/2026). Na RI Carajás são 526.378 de 763.106 (69,0%).
- **Exceções:** O Censo e a estimativa anual não se misturam numa mesma série sem identificar a origem (RN-MOD-13); a população total de 2022 do Censo difere da estimativa anual, e o indicador (2) usa a do Censo. O indicador (2) não existe para os demais anos. Estimativas por idade do Ministério da Saúde (DATASUS) não foram adotadas: não foram verificadas e, segundo a documentação do pacote brpop e a nota técnica do PROADESS, a divisão por idade de 2016 a 2020 extrapola a distribuição de 2015. Não foi verificado se o Censo 2010 serve de segundo ponto. Não foi decidido o nome final de cada indicador no manifesto.
- **Fonte:** DECISÃO-MANTENEDOR de 02/11/2026 (faixa de 15 a 64 anos e dois indicadores); DECISÃO-MANTENEDOR de 27/10/2026 (orientação de usar a população em idade ativa); BLOCOS §Bloco 4 (04/10/2026, última edição 20/10/2026); PLANO §Bloco 2 (30/09/2026); CONSUMO §Economia e mercado de trabalho (02/10/2026); consulta ao SIDRA em 02/11/2026.
- **Relacionadas:** RN-MOD-13, RN-MOD-16, RN-MOD-17, RN-IND-12

### RN-IND-08: Não recalcular o Barômetro sem reproduzir o método
- **Status:** PROPOSTA
- **Regra:** O Barômetro da Sustentabilidade não deve ser recalculado nem atualizado sem reproduzir o método, com fórmula, edição, componentes e valores ausentes.
- **Motivo:** Um recálculo parcial gera um número que a FAPESPA não publicou.
- **Exemplo:** O Barômetro 2024 entra como publicado pela FAPESPA.
- **Fonte:** CONSUMO §Finanças públicas e índices (Barômetro da Sustentabilidade 2024). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-IND-04

### RN-IND-09: PIB per capita e participação da RI no PIB são dois indicadores
- **Status:** DECIDIDA
- **Regra:** O indicador "% PIB RI-Carajás per capita" do Bloco 2 deve ser separado em indicadores derivados: o PIB per capita (`pib_per_capita`, "PIB per capita", PIB municipal ÷ população do mesmo ano) e a participação da RI Carajás no PIB, calculada nas duas bases, como dois indicadores no manifesto: `participacao_pib_para` ("Participação da RI Carajás no PIB do Pará") e `participacao_pib_brasil` ("Participação da RI Carajás no PIB do Brasil"). A participação é a soma do PIB dos 12 municípios dividida pelo PIB da base (RN-MOD-18), com todos os valores do mesmo ano; o PIB do Pará e o do Brasil saem do mesmo agregado do SIDRA, nos níveis UF e Brasil.
- **Motivo:** O nome original mistura porcentagem e per capita; a fórmula de BLOCOS ("PIB ÷ população") corresponde ao PIB per capita, e CONSUMO lista os dois itens separados.
- **Exemplo:** CONSUMO lista "PIB per capita e participação da RI Carajás" como dois itens.
- **Exceções:** O PIB municipal e a população devem ser do mesmo ano; a população do per capita do PIB não foi fixada nesta regra (a da CFEM per capita está em RN-IND-12, e a coerência entre as duas é desejável). BLOCOS ainda traz um só indicador no Bloco 2 e precisa ser atualizado.
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026 (dois indicadores) e de 11/11/2026 (bases Pará e Brasil; nomes no manifesto); BLOCOS §Bloco 2; PLANO §Bloco 2; CONSUMO §Economia e mercado de trabalho.
- **Relacionadas:** RN-MOD-17, RN-IND-10, RN-IND-12

### RN-IND-10: CFEM per capita e comparação com mineradores são derivados
- **Status:** DECIDIDA
- **Regra:** A CFEM per capita (CFEM ÷ população) e a comparação com outros municípios mineradores devem ser derivadas das fontes já existentes e não devem ter fonte própria.
- **Motivo:** Evita fonte nova para algo que se calcula do arquivo nacional da ANM e da população.
- **Exemplo:** A comparação usa o mesmo arquivo nacional de distribuição, com os N maiores recebedores como padrão.
- **Exceções:** Qual CFEM e qual população entram na razão está decidido em RN-IND-12.
- **Fonte:** BLOCOS §Bloco 3 (tabela: CFEM per capita e comparação).
- **Relacionadas:** RN-TER-09, RN-MOD-17, RN-IND-12

### RN-IND-11: Definição das classes de uso do solo
- **Status:** DECIDIDA
- **Regra:** Na Coleção 11 do MapBiomas, "floresta" é o grupo 1 inteiro (classes 3, 4, 5, 6, 7 e 49), "mineração" é a classe 30 e "área urbana" é a classe 24. A classe 7 (savana alagada) é beta e deve ser registrada como tal. O denominador e o limite municipal estão em RN-IND-13.
- **Motivo:** Segue a hierarquia oficial da legenda. A silvicultura (classe 9) fica fora de "floresta", pois pertence ao grupo Agropecuária.
- **Exemplo:** A Coleção 11 do MapBiomas classifica o uso do solo em classes numeradas por ano, de 1985 a 2025; a legenda de 13/08/2026 lista 1 Floresta, com 3 Formação Florestal, 4 Formação Savânica, 5 Mangue, 6 Floresta Alagável, 7 Savana Alagada (beta) e 49 Restinga Arbórea; 24 Área Urbanizada; 30 Mineração. Reproduzido em 30/10/2026: PDF de códigos da legenda da Coleção 11, publicado pelo MapBiomas.
- **Exceções:** Os códigos valem para a Coleção 11; uma coleção nova pode mudar a legenda e deve ser conferida (RN-TMP-06).
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; MapBiomas, "Códigos das classes da legenda da Coleção 11" (13/08/2026); CONSUMO §Meio ambiente e saneamento; BLOCOS §Bloco 5.
- **Relacionadas:** RN-IND-06, RN-IND-13, RN-TMP-06

### RN-IND-12: Qual CFEM e qual população no per capita
- **Status:** DECIDIDA
- **Regra:** A CFEM per capita é publicada como dois indicadores separados: um com a CFEM arrecadada e outro com a CFEM recebida, sem somar nem misturar (RN-CFE-02). O denominador de ambos é a estimativa anual de população do IBGE.
- **Motivo:** CFEM arrecadada e recebida são medidas distintas e respondem a perguntas diferentes: o que a extração gerou por morador e o que a prefeitura recebeu por morador. A estimativa existe para todo ano e combina com a CFEM anual; o Censo não se mistura com a estimativa (RN-MOD-13).
- **Exemplo:** A população estimada de 2025 de Parauapebas foi 305.771 pessoas (agregado 6579, variável 9324) (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Exceções:** Nos anos de Censo a série segue identificada como estimativa, sem trocar de fonte no meio (RN-MOD-13). O nome final de cada indicador no manifesto não foi definido.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; BLOCOS §Bloco 3; RN-CFE-02 e RN-MOD-13 (restrições aplicáveis).
- **Relacionadas:** RN-IND-09, RN-IND-10, RN-CFE-02, RN-MOD-13

### RN-IND-13: Denominador e limite municipal do uso do solo
- **Status:** DECIDIDA
- **Regra:** As porcentagens de uso do solo têm como denominador a área total do município, isto é, a soma de todas as classes mapeadas dentro do limite municipal. O limite municipal é a malha que o MapBiomas usa na Coleção 11, e a edição exata deve ser registrada na proveniência (RN-MOD-02).
- **Motivo:** Decisão do mantenedor: o total mapeado é simples e comparável entre municípios e anos, e a malha do MapBiomas mantém os números compatíveis com as estatísticas publicadas.
- **Exemplo:** A porcentagem de área urbana de Canaã dos Carajás em um ano é a área da classe de área urbana dividida pela soma de todas as classes do município nesse ano.
- **Exceções:** Essa área pode diferir levemente da área territorial oficial do IBGE. As classes que formam "floresta", "mineração" e "área urbana" estão em RN-IND-11. A edição da malha ainda não foi conferida.
- **Fonte:** DECISÃO-MANTENEDOR de 30/10/2026; CONSUMO §Meio ambiente e saneamento; BLOCOS §Bloco 5.
- **Relacionadas:** RN-IND-11, RN-FNT-13, RN-TMP-07

## Notas de evidência

Evidência datada que sustenta ou qualifica as regras acima. Cada nota é o texto original, movido sem alteração das regras; nenhuma delas muda o status da regra. Ordem: a das regras.

#### RN-IND-03: Corte do TD 3146

- **Evidência de 02/11/2026 (leitura do TD 3146, baixado do repositório do IPEA):** o Texto para Discussão 3146, "Capacidade fiscal e desenvolvimento no território: bases para a articulação federativa" (Mendes, Vasconcellos, Colombo, Araujo e Arantes; IPEA; 29/07/2025; DOI 10.38116/td3146-port), classifica os municípios comparando a receita bruta per capita (Finbra/STN) e o IDSC-BR, ambos de 2022, com as **médias nacionais**: receita per capita de R$ 6.880,37 e IDSC de 46,925. Acima da média é "alto" e abaixo é "baixo"; os grupos são AA, BB, AB e BA. Na tabela 7 a média é identificada como média simples entre os municípios (os grupos AA e BB têm receita média de R$ 10.772,76 e R$ 4.869,36). O estudo observa que a média brasileira do IDSC (46,9) é "baixa" na escala original do índice (40 a 49,99). Não encontrei no texto menção a atualização do estudo nem a repetir a classificação em outros anos; qualquer outro ano seria cálculo do projeto. Ficam por decidir: se os cortes de 2022 são congelados ou se a média nacional é recalculada a cada ano, e se a "receita bruta" do Finbra coincide com o que o SICONFI (DCA) fornece para o projeto (não verificado). O método de Jenks citado no estudo serve a outra parte do estudo e não foi usado como corte dos quatro grupos, segundo o que li (não conferi todas as ocorrências).
