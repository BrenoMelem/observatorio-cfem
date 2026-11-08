# Revisão das duplicatas na CFEM arrecadada

Leitura do arquivo completo da ANM em 30/10/2026. Este relatório **não contém CPF/CNPJ nem linhas brutas**. O lote segue bloqueado por RN-VPU-11 e nenhum valor da CFEM foi publicado pela API.

## Arquivo e critério

- Fonte: `https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv`
- Tamanho: 325.147.685 bytes; SHA-256: `01259502DF0A0182125EE4AF03B8794CDA4CADD25E1781C8EE5CEFF31647C6C3`
- Linhas lidas: 2.433.952; linhas distintas no recorte dos 12 municípios: 10.698.
- Duplicata significa que **todos os 14 campos** da linha são iguais aos de uma linha anterior do mesmo arquivo. Foram encontradas **129 repetições**, distribuídas em 31 combinações de município, ano e mês. A contagem considera as repetições além da primeira ocorrência.

## Distribuição

| Ano | Município | Repetições | Meses (mês: repetição) |
| --- | --- | ---: | --- |
| 2005 | Marabá | 6 | 2:1, 4:1, 5:1, 6:1, 7:1, 8:1 |
| 2011 | Eldorado do Carajás | 3 | 4:3 |
| 2011 | Marabá | 2 | 3:2 |
| 2012 | Marabá | 3 | 7:3 |
| 2014 | Marabá | 3 | 6:3 |
| 2019 | Marabá | 1 | 7:1 |
| 2019 | Parauapebas | 1 | 7:1 |
| 2020 | Marabá | 1 | 2:1 |
| 2020 | Parauapebas | 2 | 7:1, 8:1 |
| 2021 | Marabá | 1 | 10:1 |
| 2021 | Parauapebas | 2 | 1:1, 9:1 |
| 2022 | Eldorado do Carajás | 1 | 3:1 |
| 2022 | Marabá | 9 | 11:9 |
| 2023 | Marabá | 5 | 1:3, 8:1, 9:1 |
| 2024 | Canaã dos Carajás | 3 | 2:3 |
| 2024 | Curionópolis | 2 | 2:2 |
| 2024 | Marabá | 1 | 2:1 |
| 2024 | Parauapebas | 2 | 2:2 |
| 2025 | Parauapebas | 1 | 9:1 |
| 2026 | Marabá | 80 | 1:24, 2:24, 3:32 |

## Outras lacunas observadas

O arquivo nacional tem todos os 12 meses de 2025 e janeiro a outubro de 2026. Bom Jesus do Tocantins tem linha em janeiro de 2025 e nenhuma de fevereiro a dezembro; não tem linha nos dez meses nacionais de 2026. Brejo Grande do Araguaia também não tem linha nesses dez meses de 2026. São Domingos do Araguaia não aparece no recorte. A ausência não foi convertida em zero, e nenhuma causa foi presumida.

## Decisão pendente

Confirmar se as repetições refletem duplicação de publicação pela ANM ou registros legítimos indistinguíveis no CSV. A regra vigente bloqueia o lote até revisão e proíbe remover linhas automaticamente. Os detalhes completos, sem campos pessoais, estão no relatório local `output/observatorio/tratado/cfem/relatorio.json`.
