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
| Preço do minério de ferro | 1985–2025 | 1992–2025 | Pink Sheet mensal, exibição desde 1985 (RN-TMP-13); até 2005 o ferro repete o valor anual em cada mês e só é mensal desde 2006 |
| Preço do cobre | 2000–2026 | 2000–2026 | 2000–2026 |
| PIB municipal | 2010–2023 | 2010–2023 | 2010–2023 |
| Série populacional | 1980–2022 | 1980–2022 | 1980–2022 |
| IDEB | 2023 | sem ano | Todas as edições disponíveis, a mais recente descoberta na execução (RN-TMP-17) |

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
- **Exceções:** Vale na rota por Earth Engine, que é a rota decidida (RN-FNT-13).
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
- **Status:** DECIDIDA
- **Regra:** Nas séries que não são da CFEM, um ano só deve ser considerado fechado quando tiver todos os períodos esperados; os períodos já disponíveis podem ser publicados com o estado de validação "provisório", e qualquer valor anual (média ou soma) deve ficar bloqueado até o ano fechar.
- **Motivo:** Mantém uma regra única para o projeto, a mesma da CFEM (RN-CFE-06): mostra o que a fonte já tem sem apresentar como completo um ano que não é.
- **Exemplo:** O cobre e o ferro mensais do FRED tinham valores até set/2026 (reproduzido em 25/10/2026); em 10/11/2026 o Pink Sheet já trazia out/2026; os nove meses de 2026 podem ser exibidos como provisórios, e uma média anual de 2026 fica bloqueada até dez/2026.
- **Exceções:** O que conta como "período esperado" depende da frequência da série (mensal, anual) e deve constar no manifesto de cada indicador (RN-MOD-25).
- **Fonte:** DECISÃO-MANTENEDOR de 26/10/2026; VAL-15/10 §Matriz operacional (Commodities); RN-CFE-06 (regra equivalente da CFEM).
- **Relacionadas:** RN-CFE-06, RN-MOD-07, RN-TMP-13

### RN-TMP-13: Commodities pelo Pink Sheet do World Bank
- **Status:** DECIDIDA
- **Regra:** Os preços de minério de ferro e de cobre devem vir do Pink Sheet do World Bank (planilha mensal de preços nominais), em toda a série. O ferro é exibido desde 1985 e o cobre mantém o período vigente de 2000 a 2026. O FRED fica só como reserva (RN-FNT-05), para o caso de o Pink Sheet não estar disponível. Nos anos em que o Pink Sheet repete o valor anual em cada mês (ferro, de 1985 a 2005), a exibição deve avisar que o trecho é anual.
- **Motivo:** A comparação de 10/11/2026 mostrou que o ferro do FRED só é comparável ao Pink Sheet a partir de dez/2008: de 1992 a 2005 o Pink Sheet vale 2,31 vezes o FRED, sem variação; de 2006 a nov/2008 a razão oscila entre 1,95 e 5,33. O Pink Sheet cobre toda a série em uma fonte, sem emenda, e o cobre coincide com o FRED.
- **Exemplo:** Ferro (`Iron ore, cfr spot`), Pink Sheet: 1985 = 26,6; 1991 = 34,8; 1992 = 33,1; dez/2008 = 70,0, igual ao FRED (reproduzido em 10/11/2026: planilha mensal do World Bank e gráfico público do FRED). Cobre (`Copper`), mês de junho: 1995 = 2.995 (FRED 2.987,7); 2000 = 1.753 (1.752,1); 2010 = 6.499 (6.501,5); 2024 = 9.648 (9.648,2) (reproduzido em 10/11/2026). O Pink Sheet de 10/11/2026 vai até out/2026, um mês além do FRED. A execução do script de laboratório em 10/11/2026 achou 45 anos com valor anual repetido no ferro (de 1960 a 2005, com poucas exceções), o que coincide com a razão constante de 2,31 até 2005 e com a divergência a partir de 2006.
- **Exceções:** Contraria a decisão de 24/10/2026 (FRED como rota; Pink Sheet só antes de 1980). Como o ferro do FRED não é comparável ao Pink Sheet antes de dez/2008, a reserva do ferro só serve a partir desse mês e DECISÕES e BLOCOS (FRED com ferro desde 1992). A causa da diferença do ferro do FRED até 2008 não foi documentada (a página do FRED não abriu na consulta). O Pink Sheet rotula o ferro como `$/dmtu`; ver RN-TMP-14.
- **Fonte:** DECISÃO-MANTENEDOR de 10/11/2026 (conflitos 8 e 17); DECISÕES §Rotas de coleta por fonte (Commodities); BLOCOS §Bloco 2; LAB-19/10 §4 (FRED e World Bank Pink Sheet), superado nesse ponto; PLANO e MAPA-TEMAS (Pink Sheet).
- **Relacionadas:** RN-TMP-16, RN-FNT-05, RN-FNT-06, RN-FON-10

### RN-TMP-14: Unidade do minério de ferro
- **Status:** DECIDIDA
- **Regra:** O preço do minério de ferro deve ser exibido em dólares americanos por tonelada métrica (`$/dmt`), e não em `$/dmtu`.
- **Motivo:** A planilha anual do Pink Sheet rotula o ferro como `$/dmtu` e o PDF de outubro de 2026 como `$/dmt`, embora os números coincidam. O FRED, rota de coleta decidida, informa "U.S. Dollars per Metric Ton" nos metadados de `PIORECRUSDM`.
- **Exemplo:** Ferro: 120,6 (2023), 109,4 (2024) e 100,2 (2025) (transcrito do relatório VAL-15/10, não conferido no JSON). Em 25/10/2026, os metadados do FRED para `PIORECRUSDM` diziam "U.S. Dollars per Metric Ton" (reproduzido em 25/10/2026).
- **Exceções:** Desde 10/11/2026 o Pink Sheet é a fonte do ferro (RN-TMP-13); as planilhas mensal e anual rotulam o ferro como `$/dmtu` (reproduzido em 10/11/2026), e o rótulo não deve ser copiado: a unidade exibida continua sendo `$/dmt`. Como o FRED passou a ser só reserva, a confirmação pelos metadados do FRED não vale mais para a série usada e a escolha de `$/dmt` fica apoiada na dedução abaixo; a confirmação com o World Bank é desejável. Que o rótulo `$/dmtu` seja um erro da planilha é dedução (valores perto de 100 não combinam com preço por 1% de ferro contido); o World Bank não confirmou.
- **Fonte:** DECISÃO-MANTENEDOR de 26/10/2026; VAL-15/10 §Matriz operacional (Commodities), §Rodada adicional (probe do World Bank); consulta à API do FRED em 25/10/2026.
- **Relacionadas:** RN-TMP-13, RN-FNT-05, RN-FNT-06

### RN-TMP-15: Finanças a partir de 2013 pelo SICONFI
- **Status:** DECIDIDA
- **Regra:** Para 2013 em diante, as finanças municipais devem vir do SICONFI. Se algum dia houver série financeira anterior a 2013, ela deve vir de outra fonte, ser publicada como série separada, com o nome da fonte e da classificação de função, e com um corte visível em 2013; ela nunca é emendada com a série do SICONFI.
- **Motivo:** O SICONFI é a fonte primária por API para o período, e as funções das duas fontes podem não corresponder (as séries municipais do IPEADATA usam nomes como "educação e cultura" e "saúde e saneamento"; a equivalência não foi verificada). Juntá-las mostraria um salto que não existiu.
- **Exemplo:** Despesa por função de 2013 a 2025 vem do SICONFI. Nenhum indicador previsto precisa de dado anterior a 2013.
- **Exceções:** Os códigos `FINBRA_DESP` e `FINBRA_REC`, citados em BLOCOS e DECISÕES, não existem no IPEADATA em 10/11/2026 (ver Notas de evidência); a fonte da série pré-2013, se for pedida, deve ser escolhida então.
- **Fonte:** DECISÃO-MANTENEDOR de 10/11/2026 (série pré-2013 separada, sem emenda); BLOCOS §Bloco 6 (Finanças históricas); DECISÕES §Rotas de coleta por fonte.
- **Relacionadas:** RN-FNT-04

### RN-TMP-16: BLOCOS prevalece sobre PLANO nos períodos
- **Status:** DECIDIDA
- **Regra:** Onde PLANO e BLOCOS divergem sobre o período de um indicador, vale o período de BLOCOS, exceto a série do ferro (RN-TMP-13), cujo recorte de exibição é desde 1985, tudo pelo Pink Sheet.
- **Motivo:** PLANO é anterior e foi atualizado pelas Decisões.
- **Exemplo:** Uso do solo: PLANO diz 1983–2024 e BLOCOS diz 1985–2025; vale 1985–2025.
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (conflito 15); BLOCOS §Bloco 2, §Bloco 5, §Bloco 6; PLANO §Bloco 2, §Bloco 5, §Bloco 6.
- **Relacionadas:** RN-TMP-07, RN-TMP-13, RN-TMP-17

### RN-TMP-17: Edições do IDEB
- **Status:** DECIDIDA
- **Regra:** O observatório deve publicar todas as edições do IDEB que a fonte tiver, e o pipeline deve descobrir a mais recente em cada execução, sem fixar o ano; cada valor deve mostrar o ano da edição.
- **Motivo:** O IDEB sai de dois em dois anos, e fixar 2023 (PLANO) ficaria desatualizado e contradiria o 2025 que DECISÕES cita como o mais recente na Base dos Dados. A descoberta em tempo de execução é a regra geral do projeto (RN-TMP-01).
- **Exemplo:** O INEP não divulga a nota municipal de 2023 em certos casos de participação insuficiente; nesse caso o valor fica como não divulgado, nunca como zero (RN-MOD-12).
- **Fonte:** DECISÃO-MANTENEDOR de 27/10/2026; PLANO §Bloco 4; BLOCOS §Bloco 4; DECISÕES §Tabelas da Base dos Dados confirmadas.
- **Relacionadas:** RN-MOD-09, RN-MOD-12, RN-TMP-01, RN-TMP-16

## Notas de evidência

Evidência datada que sustenta ou qualifica as regras acima. Nenhuma nota muda o status da regra. Ordem: a das regras.

#### RN-TMP-15: Finanças a partir de 2013 pelo SICONFI

- **Evidência de 10/11/2026 (catálogo de metadados do IPEADATA, 4.135 séries, consulta direta à API pública):** nenhuma série tem `FINBRA` no código ou no nome; os códigos `FINBRA_DESP` e `FINBRA_REC` citados em BLOCOS §Bloco 6 e em DECISÕES não existem. Há séries municipais anuais da Secretaria do Tesouro Nacional com outros códigos, por exemplo `DESPORM` (despesa total empenhada), `DFEDUCM` (despesa por função, educação e cultura) e `DFSAUSM` (saúde e saneamento), com atualização de 07/07/2026. Os nomes das funções seguem uma classificação diferente da do SICONFI (inferência pelos nomes; as duas estruturas não foram comparadas). A cobertura por município não foi conferida. Não se sabe se essas séries são a mesma base que BLOCOS chamava de FINBRA.
