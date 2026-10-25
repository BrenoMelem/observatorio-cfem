# Território

Regras sobre quais municípios o observatório cobre, como são identificados e como entram nas agregações regionais. Legenda de status e siglas das fontes: [README](README.md).

## Os 12 municípios da RI Carajás

A Região de Integração Carajás é um recorte do governo do Pará, não do IBGE. Esta é a lista que vale em toda agregação regional (fonte: FAPESPA, conferida contra a API de localidades do IBGE em out/2026).

| Município | Código IBGE |
| --- | --- |
| Bom Jesus do Tocantins | 1501576 |
| Brejo Grande do Araguaia | 1501758 |
| Canaã dos Carajás | 1502152 |
| Curionópolis | 1502772 |
| Eldorado do Carajás | 1502954 |
| Marabá | 1504208 |
| Palestina do Pará | 1505494 |
| Parauapebas | 1505536 |
| Piçarra | 1505635 |
| São Domingos do Araguaia | 1507151 |
| São Geraldo do Araguaia | 1507458 |
| São João do Araguaia | 1507508 |

Canaã dos Carajás e Parauapebas são os municípios de foco do observatório.

### RN-TER-01: Lista fixa dos 12 municípios da RI Carajás
- **Status:** DECIDIDA
- **Regra:** Toda agregação regional deve usar exatamente os 12 municípios da lista acima, mantida em configuração com a citação da FAPESPA, e não deve incluir nem excluir municípios por outro critério.
- **Motivo:** Sem uma lista oficial fechada, nenhum número regional é reproduzível e dois indicadores regionais podem somar territórios diferentes.
- **Exemplo:** A população da RI Carajás é a soma dos 12 códigos acima, incluindo Eldorado do Carajás (1502954).
- **Fonte:** DECISÕES §Municípios da RI Carajás; PLANO §Visão geral.
- **Relacionadas:** RN-TER-02, RN-TER-05, RN-TER-11

### RN-TER-02: Indicador regional é sempre agregado dos municípios
- **Status:** DECIDIDA
- **Regra:** Todo indicador da RI Carajás deve ser calculado a partir dos valores dos municípios da lista e não deve ser substituído por um valor regional pronto de outra fonte.
- **Motivo:** A RI não é um recorte do IBGE; só a agregação pela lista oficial garante que o número regional é reproduzível.
- **Exemplo:** A comparação "Canaã e Parauapebas versus RI Carajás" da dinâmica populacional usa a soma dos 12 municípios.
- **Exceções:** Indicadores compostos congelados citam o valor publicado pela entidade (ver RN-IND-01).
- **Fonte:** DECISÕES §Municípios da RI Carajás ("fixa quais municípios entram em toda agregação regional"); BLOCOS §Bloco 1; PLANO §Visão geral.
- **Relacionadas:** RN-TER-01, RN-MOD-18, RN-IND-01

### RN-TER-03: Código IBGE de 7 dígitos identifica o município
- **Status:** DECIDIDA
- **Regra:** O município deve ser identificado pelo código IBGE de 7 dígitos, e fontes que usam outro código ou apenas o nome devem ser convertidas por uma tabela de equivalência.
- **Motivo:** O código é o único identificador estável entre as fontes; nomes variam e códigos de outros órgãos não coincidem.
- **Exemplo:** Canaã dos Carajás é 1502152 e Parauapebas é 1505536.
- **Fonte:** DECISÕES §Municípios da RI Carajás, §Rotas de coleta por fonte (SICONFI `id_ente` com o código IBGE de 7 dígitos).
- **Relacionadas:** RN-TER-04, RN-TER-06, RN-TER-08

### RN-TER-04: Código tratado como texto
- **Status:** PROPOSTA
- **Regra:** O código IBGE deve ser tratado como texto, e não como número.
- **Motivo:** Evita perda de dígitos à esquerda em códigos de outros estados e evita conversões silenciosas.
- **Exemplo:** O laboratório de fontes e os scripts guardam os 12 códigos como texto.
- **Fonte:** NOTEBOOK (célula 1); SCRIPTS (`build_cfem_distribution_municipal`, `validate_anm_cfem`).
- **Relacionadas:** RN-TER-03

### RN-TER-05: Checagem dos nomes na largada
- **Status:** DECIDIDA
- **Regra:** Toda execução deve conferir os 12 códigos e nomes contra a API de localidades do IBGE e deve avisar se algum nome deixar de corresponder.
- **Motivo:** Detecta mudança de nome ou de código antes que ela contamine uma agregação.
- **Exemplo:** O nome oficial é "Eldorado do Carajás", não "Eldorado dos Carajás". O laboratório de 17/10/2026 registrou 12/12 códigos conferidos (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** DECISÕES §Municípios da RI Carajás; LAB-19/10 §4 (IBGE Localidades).
- **Relacionadas:** RN-TER-01, RN-TER-03

### RN-TER-06: Fonte que traz município só por nome exige tabela de equivalência
- **Status:** DECIDIDA
- **Regra:** Quando a fonte identificar o município apenas pelo nome, o registro deve ser ligado ao código IBGE por uma tabela de equivalência, e o registro que não puder ser ligado não deve entrar em nenhuma agregação municipal.
- **Motivo:** Nome sem código permite homônimos e grafias diferentes; sem a equivalência, o valor pode ser atribuído ao município errado.
- **Exemplo:** O arquivo de autuações da ANM traz a coluna `Município` por nome. Nos arquivos completos, 9 dos 12 municípios tiveram linhas de autuação; Canaã teve 11 linhas e Parauapebas 35 (transcrito do relatório VAL-15/10, não conferido no JSON).
- **Fonte:** BLOCOS §Bloco 3 (Autuações); DECISÕES §Autuações da CFEM; VAL-15/10 §Rodada adicional.
- **Relacionadas:** RN-TER-07, RN-CFE-13

### RN-TER-07: Comparação de nomes sem acento e sem diferença de caixa, apenas para o Pará
- **Status:** PROPOSTA
- **Regra:** A equivalência por nome deve ignorar acentos e diferença entre maiúsculas e minúsculas e deve considerar apenas registros da UF PA.
- **Motivo:** Há municípios homônimos em outros estados e a fonte pode variar a grafia.
- **Exemplo:** O validador dos arquivos da ANM compara "Canaã dos Carajás" e "CANAA DOS CARAJAS" como o mesmo município quando a UF é PA.
- **Fonte:** SCRIPTS (`validate_anm_cfem`, rotina de normalização e filtro de UF). Deduzida do código.
- **Relacionadas:** RN-TER-06

### RN-TER-08: Código do TSE exige tabela de equivalência
- **Status:** DECIDIDA
- **Regra:** Dados do TSE obtidos com o código do tribunal devem ser convertidos ao código IBGE antes de qualquer uso.
- **Motivo:** O TSE usa código próprio, diferente do IBGE.
- **Exemplo:** O eleitorado baixado do portal de dados abertos do TSE vem com código TSE, e o eleitorado obtido pela Base dos Dados já traz o código IBGE.
- **Fonte:** DECISÕES §Número de eleitores; BLOCOS §Bloco 1.
- **Relacionadas:** RN-TER-03

### RN-TER-09: Municípios de comparação são configuráveis
- **Status:** DECIDIDA
- **Regra:** A lista de municípios mineradores usada na comparação deve ser configurável e, por padrão, deve ser formada pelos N municípios com maior CFEM recebida segundo o arquivo de distribuição.
- **Motivo:** O arquivo da ANM é nacional, então a comparação com outros municípios mineradores não exige fonte nova, e a lista precisa mudar sem mudar regras.
- **Exemplo:** O ranking considera o valor recebido por ente no arquivo de distribuição, que traz o código IBGE do ente (`CodigoEnte`).
- **Exceções:** O valor de N, o período do ranking e a modalidade de distribuição usada no ranking estão **EM ABERTO**.
- **Fonte:** DECISÕES §Bloco 3; BLOCOS §Bloco 3. Pendência registrada em [pendencias.md](pendencias.md).
- **Relacionadas:** RN-CFE-10, RN-IND-10

### RN-TER-10: Nota sobre a criação de Canaã dos Carajás em 1994
- **Status:** DECIDIDA
- **Regra:** A série populacional "desde 1980" deve trazer nota informando que Canaã dos Carajás foi criada em 1994 e que antes disso o território pertencia a Parauapebas e Marabá.
- **Motivo:** Sem a nota, a ausência ou o salto de valores antes de 1994 parece erro de dado.
- **Exemplo:** Série populacional 1980–2022 de Canaã dos Carajás (1502152).
- **Fonte:** BLOCOS §Bloco 1 ("Série longa precisa de nota de rodapé"); PLANO §Bloco 1.
- **Relacionadas:** RN-MOD-13, RN-MOD-15

### RN-TER-11: Guardar a composição territorial usada
- **Status:** PROPOSTA
- **Regra:** Cada publicação deve registrar a composição da RI usada na agregação.
- **Motivo:** Permite reproduzir um número regional antigo se a lista oficial mudar.
- **Exemplo:** Um total regional de 2025 registra os 12 códigos vigentes em out/2026.
- **Fonte:** CONSUMO §Contrato de dados para o front-end (campos `geo_id`, `geo_level`).
- **Relacionadas:** RN-TER-01, RN-MOD-02

### RN-TER-12: Declarar se o indicador usa residência ou ocorrência
- **Status:** PROPOSTA
- **Regra:** Indicadores de saúde e de violência devem declarar se o município é o de residência ou o de ocorrência, e não devem misturar os dois conceitos numa mesma série.
- **Motivo:** O mesmo óbito pode cair em municípios diferentes conforme o critério.
- **Exemplo:** Para uma amostra do SIM, o filtro municipal deve seguir a definição escolhida do indicador.
- **Fonte:** VAL-15/10 §Como repetir os testes (item sobre PySUS); CONSUMO §Sociedade (localidade de referência). Dedução: nenhuma das duas fontes fixa a regra.
- **Relacionadas:** RN-FNT-15
