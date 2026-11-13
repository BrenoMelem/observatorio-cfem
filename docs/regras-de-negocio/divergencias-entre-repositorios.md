# Divergências entre este repositório e `obcefem_api` e `obcefem`

Registro da comparação de 08/11/2026 e do que o mantenedor decidiu. A decisão de cada item está nas regras citadas; este arquivo só aponta para elas. A comparação detalhada (as recomendações iniciais, com o raciocínio de cada item) está no histórico do Git, no commit `5e4bd0c`. Legenda de status e siglas: [README](README.md).

## Os três repositórios

| Repositório | O que é |
| --- | --- |
| `observatorio-cfem` (este) | Regras de negócio, pesquisa e scripts de laboratório. Não é o produto |
| `obcefem_api` | Protótipo funcional: API em FastAPI e painel web de arrecadação e distribuição da CFEM, com atualização diária. Publicado na Vercel |
| `obcefem` | Site institucional estático, com uma página por dimensão. Os gráficos das dimensões trazem o selo "dados reais" ou "dados fictícios (protótipo)" e os links "Disponível" apontam para o painel da `obcefem_api` |

O código da `obcefem_api` não define regra por si. O mantenedor decidiu em 08/11/2026 seguir o que ela faz nos pontos abaixo; onde isso contraria uma regra já decidida, a regra continua no texto e ganhou uma exceção.

## O que já concordava

Os 12 municípios (RN-TER-01), a ANM como fonte única (RN-CFE-01), o valor pronto da ANM sem recalcular (RN-CFE-21), valores nominais (RN-MOD-26), autuação como cobrança e não dinheiro em caixa (RN-CFE-17), ausência sem virar zero (RN-CFE-07, RN-CFE-09), a trava que mantém o último dado bom (RN-VPU-03) e o titular visível (RN-CFE-18).

## Decisões

| # | Tema | Diferença | Decisão (08/11/2026) | Registro |
| --- | --- | --- | --- | --- |
| D1 | Distribuição | A API calcula a repartição pela lei (arrecadado × percentual); aqui a recebida vem do arquivo da ANM | Seguir a API. Percentuais conferidos nas Leis 8.001/1990 e 13.540/2017. A estimativa é análise derivada; a recebida continua do arquivo. Em 12/11/2026: 60/15/15/10 a partir de 2018 (2017 inteiro em 65/23/12) e 15% rotulados "afetados" desde 2018, com ressalva, como a API | [RN-CFE-25](mineracao-cfem.md), [RN-CFE-26](mineracao-cfem.md) |
| D2 | Duplicatas | A API soma as 129 linhas repetidas; aqui o lote ficaria bloqueado | Manter o que a API faz | Exceção em [RN-VPU-11](validacao-e-publicacao.md) |
| D3 | Ano parcial | A API rotula o ano em curso "(parcial)" e usa o volume de registros (50% da mediana) | Manter o que a API faz | Exceção em [RN-CFE-05](mineracao-cfem.md) e [RN-CFE-06](mineracao-cfem.md) |
| D4 | Ano da autuação | A API usa o ano do processo de cobrança e descarta as sem ano; aqui vale a data de publicação e a faixa "sem ano" | Manter o que a API faz | Exceção em [RN-CFE-14](mineracao-cfem.md) e [RN-CFE-16](mineracao-cfem.md) |
| D5 | Chave do município | A API usa o nome normalizado; aqui vale o código IBGE | Manter o que a API faz | Exceção em [RN-TER-03](territorio.md) |
| D6 | Média do Pará e do Brasil | A API compara com a média por município; aqui só havia a comparação com municípios mineradores | Manter o que a API faz | [RN-CFE-27](mineracao-cfem.md) |
| D7 | Esquema de resposta | A API tem formato próprio | Formato híbrido: envelope da API mais observações no esquema comum. A API ainda não faz isso | Exceção em [RN-MOD-03](modelo-de-dados.md) |
| D8 | Dado fictício | O site mistura dados reais e fictícios, rotulados | Manter, com o rótulo obrigatório | [RN-ENT-11](entrega-dos-dados.md) |
| D9 | Substâncias | A API soma "MINÉRIO DE FERRO" com "FERRO" | Manter o que a API faz | [RN-CFE-28](mineracao-cfem.md) |
| D10 | Foco | A API gira em torno de Parauapebas e Canaã dos Carajás | Manter o que a API faz | [RN-TER-13](territorio.md) |
| D11 | Arrecadação: arquivos e início da série | A API usa arquivos por faixa de ano e começa em 2002; aqui vale o arquivo completo desde 2003 | Manter o que a API faz | Exceção em [RN-CFE-22](mineracao-cfem.md) |

## Em aberto

- **Homologação:** RN-VPU-10 (só dado homologado alimenta os gráficos) continua valendo e a API ainda não a cumpre; não há exceção decidida.
- **Efeito das 129 duplicatas** em reais nos totais: não foi medido (D2).
- **O "15%" da cota municipal** que a API cita no arquivo de distribuição de 2023 a 2025 não foi reproduzido aqui. Ver RN-CFE-26.

## O que a comparação não verificou

- Os totais publicados pelo painel não foram conferidos contra o arquivo da ANM, e os testes da `obcefem_api` não foram executados.
- A rotina de atualização do GitHub Actions da API e a correspondência com RN-TMP-02 (agenda por fonte) ficaram a conferir.
- O texto das quatro páginas do `obcefem` não foi confrontado com o glossário.
