# Temporalidade e atualização

Regras sobre o ano de referência, a agenda de atualização por fonte, os recortes de período dos indicadores e as mudanças de método que afetam a comparação no tempo. Legenda de status e siglas das fontes: [README](README.md).

## Agenda de atualização por fonte

Cada fonte tem a própria agenda, e uma fonte não segue a agenda de outra (RN-TMP-02).

| Frequência | Fontes |
| --- | --- |
| Mensal | CAGED, veículos, commodities, CFEM |
| Anual | Censo, PIB, SICONFI, INEP, MapBiomas, SEEG |
| Sob demanda | FAPESPA, CadÚnico |
| A cada eleição (bianual) | Eleitorado do TSE |

Fonte: DECISÕES §Arquitetura e padrões de dados (Uma agenda por fonte).

## Recortes de período dos indicadores

Quando PLANO (30/09/2026) e BLOCOS (04/10/2026, última edição 20/10/2026) divergem, BLOCOS prevalece (RN-TMP-16). A tabela mostra o período vigente.

| Indicador | PLANO | BLOCOS | Período vigente |
| --- | --- | --- | --- |
| Uso do solo, área urbana | 1983–2024 | 1985–2025 | 1985–2025 |
| Despesa per capita por função | 2013–2024 | 2013–2025 | 2013–2025 |
| Preço do minério de ferro | 1985–2025 | 1992–2025 | Início em jan/1980, pelo FRED (RN-TMP-13); recorte de exibição **EM ABERTO** |
| Preço do cobre | 2000–2026 | 2000–2026 | 2000–2026 |
| PIB municipal | 2010–2023 | 2010–2023 | 2010–2023 |
| Série populacional | 1980–2022 | 1980–2022 | 1980–2022 |
| IDEB | 2023 | sem ano | **EM ABERTO** (RN-TMP-17) |

### RN-TMP-01: Nunca fixar o ano no código
- **Status:** DECIDIDA
- **Regra:** O ano mais recente de cada fonte deve ser descoberto em tempo de execução e não deve ser fixado no código nem em configuração.
- **Motivo:** Um observatório que mostra 2023 quando já existe 2024 perde credibilidade mais rápido do que um que mostra menos indicadores.
- **Exemplo:** O pipeline descobre o ano máximo de uma tabela da Base dos Dados na execução. Para o SICONFI, o laboratório procura um exercício que tenha linhas, em vez de supor que o ano corrente já foi publicado (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** DECISÕES §Tabelas da Base dos Dados confirmadas; PLANO §Riscos e cuidados; LAB-19/10 §5.5.
- **Relacionadas:** RN-MOD-20, RN-TMP-03

### RN-TMP-02: Uma agenda por fonte
- **Status:** DECIDIDA
- **Regra:** Cada fonte deve ter agenda própria de atualização, na frequência indicada na tabela acima.
- **Motivo:** As fontes publicam em ritmos diferentes, e uma agenda única atualizaria dados que não mudaram ou deixaria passar os que mudaram.
- **Exemplo:** A CFEM é mensal; o eleitorado do TSE é bianual.
- **Exceções:** A frota de veículos aparece como mensal em DECISÕES, mas sua fonte está em conflito (RN-FNT-12).
- **Fonte:** DECISÕES §Arquitetura e padrões de dados (Uma agenda por fonte).
- **Relacionadas:** RN-MOD-25, RN-FNT-12

### RN-TMP-03: A Base dos Dados pode parar de atualizar sem aviso
- **Status:** DECIDIDA
- **Regra:** Para indicadores obtidos pela Base dos Dados, o ano mais recente deve ser descoberto a cada execução, porque a reingestão da Base é irregular e pode ter parado sem aviso.
- **Motivo:** O ponto fraco da Base dos Dados é a atualização, não a confiabilidade.
- **Exemplo:** O Censo 2022 ainda não está na Base dos Dados no nível de detalhe necessário, e o SIM começa só em 1996.
- **Fonte:** DECISÕES §Estratégia de fontes e acesso.
- **Relacionadas:** RN-FON-03, RN-TMP-01

### RN-TMP-04: Retificações do SICONFI
- **Status:** PROPOSTA
- **Regra:** Declarações retificadas do SICONFI não devem ser somadas como registros distintos da versão original.
- **Motivo:** Somar original e retificação conta o mesmo valor duas vezes.
- **Exemplo:** A despesa por função de um exercício deve usar a declaração retificada vigente.
- **Fonte:** CONSUMO §Finanças públicas e índices (despesa per capita). VAL-15/10 §Matriz operacional cita "reconciliar totais retificados" como pendência, sem fixar a regra.
- **Relacionadas:** RN-FNT-04

### RN-TMP-05: Nome do asset do MapBiomas não é fixado
- **Status:** DECIDIDA
- **Regra:** Quando o MapBiomas for obtido pelo Google Earth Engine, o nome do asset de cobertura não deve ser fixado: a pasta deve ser listada em tempo de execução.
- **Motivo:** O sufixo muda em correções sem aviso.
- **Exemplo:** O arquivo de cobertura atual deveria terminar em `_coverage_v3`, mas esse sufixo pode mudar.
- **Exceções:** Vale só se a rota por Earth Engine for a escolhida (conflito 6, **EM ABERTO**).
- **Fonte:** DECISÕES §Rotas de coleta por fonte (MapBiomas: caminho do asset ainda não testado); BLOCOS §Bloco 5.
- **Relacionadas:** RN-TMP-06, RN-FNT-13

### RN-TMP-06: Congelar a versão a cada coleção do MapBiomas
- **Status:** PROPOSTA
- **Regra:** A cada nova coleção do MapBiomas, a versão usada deve ser congelada e identificada, porque revisões podem alterar a série retroativamente.
- **Motivo:** Sem a versão identificada, um número do passado muda sem explicação.
- **Exemplo:** A Coleção 11 cobre 1985–2025.
- **Fonte:** CONSUMO §Meio ambiente e saneamento. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-TMP-05, RN-TMP-07

### RN-TMP-07: Uso do solo vai de 1985 a 2025
- **Status:** DECIDIDA
- **Regra:** A série de uso do solo do observatório deve cobrir 1985–2025, e o ponto de 1983 não faz parte dela.
- **Motivo:** A Coleção 11 do MapBiomas começa em 1985, então 1983 não é atendido por essa fonte; BLOCOS prevalece sobre PLANO nos períodos.
- **Exemplo:** A área urbana de Canaã dos Carajás é publicada de 1985 a 2025.
- **Fonte:** BLOCOS §Bloco 5; DECISÃO-MANTENEDOR de 24/10/2026 (conflito 15); CONSUMO §Meio ambiente e saneamento; VAL-15/10 §Matriz operacional (Uso do solo/floresta).
- **Relacionadas:** RN-TMP-16

### RN-TMP-08: Mudança de nomenclatura entre censos
- **Status:** PROPOSTA
- **Regra:** Categorias cuja nomenclatura mudou entre censos não devem ser comparadas automaticamente.
- **Motivo:** A mudança de nome pode refletir mudança de conceito.
- **Exemplo:** "Favelas e Comunidades Urbanas" (Censo 2022) não se compara automaticamente com "aglomerados subnormais" (edições antigas).
- **Fonte:** CONSUMO §Sociedade, serviços e segurança; MAPA-TEMAS §Sociedade.
- **Relacionadas:** RN-MOD-13

### RN-TMP-09: Registros policiais podem ser retificados
- **Status:** PROPOSTA
- **Regra:** Dados de segurança pública baseados em registros policiais não devem ser tratados como definitivos na primeira publicação.
- **Motivo:** Os registros podem ser retificados depois.
- **Exemplo:** Consultas do CODEC/SEGUP são feitas por intervalos de até um ano e os registros podem ser revistos.
- **Fonte:** CONSUMO §Sociedade, serviços e segurança.
- **Relacionadas:** RN-MOD-07, RN-FNT-08

### RN-TMP-10: Transição CID-9 e CID-10 no SIM
- **Status:** PROPOSTA
- **Regra:** Séries de óbitos do SIM devem documentar a transição entre CID-9 e CID-10 e a regra de classificação adotada.
- **Motivo:** A mudança de classificação pode criar quebra na série.
- **Exemplo:** O SIM na Base dos Dados começa em 1996.
- **Fonte:** CONSUMO §Sociedade, serviços e segurança.
- **Relacionadas:** RN-FNT-15

### RN-TMP-11: Estimativa por proxy não é medição direta
- **Status:** PROPOSTA
- **Regra:** Valores do SEEG alocados por proxy devem ser identificados como estimativa, com gás, setor e edição, e não devem ser chamados de medição direta local.
- **Motivo:** O SEEG não tem desagregação municipal direta para todos os setores.
- **Exemplo:** A série municipal do SEEG começa em 2000.
- **Fonte:** CONSUMO §Meio ambiente e saneamento. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-FNT-14

### RN-TMP-12: Regra para anos parciais
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir como tratar anos ainda incompletos (por exemplo, o ano corrente) em séries que não são da CFEM.
- **Motivo:** VAL-15/10 aponta a necessidade de definir a regra, e ela não foi decidida. Para a CFEM vale RN-CFE-06.
- **Exemplo:** O cobre vai até 2026 em BLOCOS, e 2026 é um ano parcial.
- **Fonte:** VAL-15/10 §Matriz operacional (Commodities).
- **Relacionadas:** RN-CFE-06, RN-TMP-13

### RN-TMP-13: Commodities pelo FRED, com Pink Sheet só antes de 1980
- **Status:** DECIDIDA
- **Regra:** A série de preços de ferro e cobre deve vir do FRED, o início da série do ferro é janeiro de 1980, e o Pink Sheet do World Bank só deve ser usado, congelado uma vez com citação, para anos anteriores a 1980.
- **Motivo:** O laboratório de 19/10/2026 encontrou o ferro no FRED desde jan/1980, mais recente que DECISÕES e BLOCOS, que diziam 1992.
- **Exemplo:** FRED, ferro (`PIORECRUSDM`) e cobre (`PCOPPUSDM`), mensais, de jan/1980 a jul/2026 (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Exceções:** O recorte de exibição da série do ferro (desde 1980 ou desde 1985, como pediu a oficina) está **EM ABERTO**.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (conflito 8); LAB-19/10 §4 (FRED e World Bank Pink Sheet); DECISÕES §Rotas de coleta por fonte (Commodities); BLOCOS §Bloco 2.
- **Relacionadas:** RN-TMP-16, RN-FNT-05, RN-FNT-06

### RN-TMP-14: Unidade do minério de ferro
- **Status:** EM ABERTO
- **Regra:** A unidade exibida para o minério de ferro deve seguir a definição confirmada pela fonte, e o rótulo só deve ser publicado depois dessa confirmação.
- **Motivo:** A planilha anual do Pink Sheet rotula o ferro como `$/dmtu` e o PDF de outubro de 2026 como `$/dmt`, embora os números coincidam.
- **Exemplo:** Ferro: 120,6 (2023), 109,4 (2024) e 100,2 (2025) (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** VAL-15/10 §Matriz operacional (Commodities), §Rodada adicional (probe do World Bank).
- **Relacionadas:** RN-TMP-13, RN-FNT-05, RN-FNT-06

### RN-TMP-15: Finanças a partir de 2013 pelo SICONFI
- **Status:** DECIDIDA
- **Regra:** Para 2013 em diante, as finanças municipais devem vir do SICONFI, e o FINBRA no IPEADATA só serve à série pré-2013, se ela for necessária.
- **Motivo:** O SICONFI é a fonte primária por API para o período.
- **Exemplo:** Despesa por função de 2013 a 2025 vem do SICONFI.
- **Exceções:** A emenda entre as duas fontes numa mesma série não foi definida (**EM ABERTO**).
- **Fonte:** BLOCOS §Bloco 6 (Finanças históricas); DECISÕES §Rotas de coleta por fonte.
- **Relacionadas:** RN-FNT-04

### RN-TMP-16: BLOCOS prevalece sobre PLANO nos períodos
- **Status:** DECIDIDA
- **Regra:** Onde PLANO e BLOCOS divergem sobre o período de um indicador, vale o período de BLOCOS, exceto o início da série do ferro (RN-TMP-13).
- **Motivo:** PLANO é anterior e foi atualizado pelas Decisões.
- **Exemplo:** Uso do solo: PLANO diz 1983–2024 e BLOCOS diz 1985–2025; vale 1985–2025.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (conflito 15); BLOCOS §Bloco 2, §Bloco 5, §Bloco 6; PLANO §Bloco 2, §Bloco 5, §Bloco 6.
- **Relacionadas:** RN-TMP-07, RN-TMP-13, RN-TMP-17

### RN-TMP-17: Ano do IDEB
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve definir qual edição ou período do IDEB o observatório publica.
- **Motivo:** PLANO diz 2023, BLOCOS não diz o ano e DECISÕES indica o ano mais recente da Base dos Dados como 2025.
- **Exemplo:** O INEP não divulga a nota municipal de 2023 em certos casos de participação insuficiente.
- **Fonte:** PLANO §Bloco 4; BLOCOS §Bloco 4; DECISÕES §Tabelas da Base dos Dados confirmadas; DECISÃO-MANTENEDOR de 24/10/2026 (conflito 15).
- **Relacionadas:** RN-MOD-09, RN-TMP-16
