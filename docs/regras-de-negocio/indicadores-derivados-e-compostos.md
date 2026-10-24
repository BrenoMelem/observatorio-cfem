# Indicadores derivados e compostos

Regras sobre indicadores calculados pelo observatório a partir de outros (derivados) e sobre os índices publicados por terceiros que entram congelados (compostos). Legenda de status e siglas das fontes: [README](README.md).

## Indicadores compostos

| Indicador | Fonte | Estratégia | Promovível a recalculado? |
| --- | --- | --- | --- |
| Relação receita per capita × IDSC (grupos AA, AB, BA, BB) | IPEA, TD 3146 (2025) | Congelado | Sim, é candidato real |
| Barômetro da Sustentabilidade | FAPESPA | Congelado | Não |
| Ranking de competitividade | CLP | Congelado | Não |

Fonte: REG §Indicadores compostos; BT §Bloco 6.

### RN-IND-01: Compostos entram congelados, com citação e marca de promovível
- **Status:** DECIDIDA
- **Regra:** Os três indicadores compostos devem entrar congelados, com citação da fonte e do ano, e cada um deve ter no manifesto a marca de estratégia "congelado" e a marca "promovível" (sim ou não).
- **Motivo:** Congelar não é deixar de fora: o número aparece com fonte e ano; a diferença é se é uma foto, atualizada à mão a cada edição, ou um cálculo vivo. A marca impede que a ressalva se perca.
- **Exemplo:** O Barômetro da Sustentabilidade 2024 (FAPESPA) consta como congelado e não promovível.
- **Fonte:** REG §Indicadores compostos; BT §Bloco 6.
- **Relacionadas:** RN-MOD-25, RN-IND-02, RN-IND-04

### RN-IND-02: A relação do IPEA é a única candidata a recálculo
- **Status:** DECIDIDA
- **Regra:** A relação receita per capita × IDSC (IPEA, TD 3146) deve ser tratada como candidata a recalculado e só deve ser promovida depois que o SICONFI estiver rodando.
- **Motivo:** É uma classificação 2×2 simples que usa dados que o projeto já terá: receita per capita (SICONFI ÷ população) e nota do IDSC.
- **Exemplo:** Quatro quadrantes (AA, AB, BA, BB) conforme receita per capita e IDSC altos ou baixos.
- **Fonte:** REG §Indicadores compostos; BT §Bloco 6.
- **Relacionadas:** RN-IND-03, RN-FNT-04

### RN-IND-03: Corte do TD 3146
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve confirmar no TD 3146 o corte usado para "alto" e "baixo" em cada eixo (mediana, média ou valor fixo) antes de promover a relação a recalculada.
- **Motivo:** Sem o corte exato, o número recalculado não bate com o do IPEA.
- **Exemplo:** A faixa AB corresponde a receita per capita alta e IDSC baixo.
- **Fonte:** REG §Indicadores compostos, §Pré-requisitos e pendências.
- **Relacionadas:** RN-IND-02

### RN-IND-04: Barômetro e CLP ficam congelados sem previsão
- **Status:** DECIDIDA
- **Regra:** O Barômetro da Sustentabilidade e o ranking de competitividade da CLP devem ser tratados como dado que a entidade publica, e não como dado que o observatório calcula.
- **Motivo:** O Barômetro (metodologia Prescott-Allen) é pesado demais para um item anual; o ranking da CLP usa pesos proprietários, e reproduzi-lo sem a documentação completa é inviável.
- **Exemplo:** O ranking de competitividade de Canaã dos Carajás é reproduzido com citação, sem recálculo.
- **Fonte:** REG §Indicadores compostos; BT §Bloco 6.
- **Relacionadas:** RN-IND-01, RN-IND-08

### RN-IND-05: Derivado ou composto é marcado como análise derivada
- **Status:** PROPOSTA
- **Regra:** Todo indicador composto ou derivado deve ser marcado como análise derivada e não como indicador oficial contínuo, guardando o ano de referência, os cortes, o deflator e a regra de classificação.
- **Motivo:** Evita que uma conclusão de estudo seja lida como série oficial.
- **Exemplo:** A relação do TD 3146 guarda o ano de referência, os cortes de receita e de IDSC e a regra de classificação.
- **Fonte:** ANA §Finanças públicas e índices (receita per capita e IDSC). Não consta em REG, BT, L19 ou R15.
- **Relacionadas:** RN-IND-01, RN-MOD-17

### RN-IND-06: Mineração × cobertura florestal é derivado próprio
- **Status:** DECIDIDA
- **Regra:** A área de mineração versus cobertura florestal deve ser calculada pelo observatório, por município e ano, a partir das classes de mineração e de floresta do MapBiomas, sem fonte nova.
- **Motivo:** Mostra o avanço da mineração sobre a floresta, pertinente para Canaã dos Carajás e Parauapebas, com dados que o bloco ambiental já tem.
- **Exemplo:** Mineração e floresta de Canaã dos Carajás (1502152), por ano, de 1985 a 2025.
- **Exceções:** As classes que formam "floresta", "mineração" e "área urbana" estão em aberto (RN-IND-11).
- **Fonte:** REG §Área de mineração × cobertura florestal; BT §Bloco 5.
- **Relacionadas:** RN-IND-11, RN-TMP-07

### RN-IND-07: Denominador do emprego formal como proporção da população
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir qual população é o denominador do indicador "emprego formal como % da população" (total, em idade ativa ou força de trabalho) e manter a mesma regra entre territórios.
- **Motivo:** O PLN e o BT dizem "RAIS ÷ população" sem especificar qual; a ANA exige aprovar o denominador.
- **Exemplo:** A RAIS mede vínculos formais (estoque), e a população total inclui pessoas fora da idade ativa.
- **Fonte:** BT §Bloco 4 (04/10/2026, última edição 20/10/2026); PLN §Bloco 2 (30/09/2026); ANA §Economia e mercado de trabalho (02/10/2026).
- **Relacionadas:** RN-MOD-16, RN-MOD-17

### RN-IND-08: Não recalcular o Barômetro sem reproduzir o método
- **Status:** PROPOSTA
- **Regra:** O Barômetro da Sustentabilidade não deve ser recalculado nem atualizado sem reproduzir o método, com fórmula, edição, componentes e valores ausentes.
- **Motivo:** Um recálculo parcial gera um número que a FAPESPA não publicou.
- **Exemplo:** O Barômetro 2024 entra como publicado pela FAPESPA.
- **Fonte:** ANA §Finanças públicas e índices (Barômetro da Sustentabilidade 2024). Não consta em REG, BT, L19 ou R15.
- **Relacionadas:** RN-IND-04

### RN-IND-09: Definição de "% PIB RI-Carajás per capita"
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir o que o indicador "% PIB RI-Carajás per capita" mede: a participação da RI no PIB ou o PIB per capita.
- **Motivo:** O nome mistura porcentagem e per capita; o BT o descreve como "Calculado: PIB ÷ população".
- **Exemplo:** A ANA lista "PIB per capita e participação da RI Carajás" como dois itens.
- **Fonte:** BT §Bloco 2; PLN §Bloco 2; ANA §Economia e mercado de trabalho; DM de 24/10/2026 (item IND-09 deixado em aberto).
- **Relacionadas:** RN-MOD-17, RN-IND-10

### RN-IND-10: CFEM per capita e comparação com mineradores são derivados
- **Status:** DECIDIDA
- **Regra:** A CFEM per capita (CFEM ÷ população) e a comparação com outros municípios mineradores devem ser derivadas das fontes já existentes e não devem ter fonte própria.
- **Motivo:** Evita fonte nova para algo que se calcula do arquivo nacional da ANM e da população.
- **Exemplo:** A comparação usa o mesmo arquivo nacional de distribuição, com os N maiores recebedores como padrão.
- **Exceções:** Qual CFEM e qual população entram na razão está em aberto (RN-IND-12).
- **Fonte:** BT §Bloco 3 (tabela: CFEM per capita e comparação).
- **Relacionadas:** RN-TER-09, RN-MOD-17, RN-IND-12

### RN-IND-11: Definição das classes de uso do solo
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir quais classes do MapBiomas formam "floresta", "mineração" e "área urbana", o denominador das porcentagens e a edição do limite municipal.
- **Motivo:** Sem essa definição, os indicadores de uso do solo não são reproduzíveis.
- **Exemplo:** A Coleção 11 do MapBiomas classifica o uso do solo em classes numeradas por ano, de 1985 a 2025.
- **Fonte:** ANA §Meio ambiente e saneamento; BT §Bloco 5.
- **Relacionadas:** RN-IND-06

### RN-IND-12: Qual CFEM e qual população no per capita
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir se a CFEM per capita usa a CFEM arrecadada ou a recebida, e qual série de população (estimativa anual ou Censo) entra no denominador.
- **Motivo:** O BT diz apenas "CFEM ÷ população", mas CFEM arrecadada e recebida são medidas distintas e população estimada e Censo não se misturam.
- **Exemplo:** A população estimada de 2025 de Parauapebas foi 305.771 pessoas (agregado 6579, variável 9324) (transcrito do relatório R15, não conferido no JSON).
- **Fonte:** BT §Bloco 3; RN-CFE-02 e RN-MOD-13 (restrições aplicáveis).
- **Relacionadas:** RN-IND-10, RN-CFE-02, RN-MOD-13
