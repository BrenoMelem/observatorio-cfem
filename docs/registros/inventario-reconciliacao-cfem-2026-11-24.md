# Inventário da reconciliação da arrecadação CFEM — 24/11/2026

Este registro inventaria a evidência local usada no PR #47 antes da investigação
das divergências. Os valores e as referências não foram alterados nesta etapa.
A diferença da tabela abaixo é **soma do CSV menos tabela municipal da ANM**.
Nenhuma causa foi confirmada para as 15 diferenças.

## Artefatos e proveniência

| Artefato | Local | Situação em 24/11/2026 |
| --- | --- | --- |
| CSV integral da arrecadação | `tmp/CFEM_Arrecadacao.csv` | Fora do Git; 325.147.685 bytes; SHA-256 `01259502df0a0182125ee4af03b8794cda4cadd25e1781c8ee5ceff31647c6c3`; a cópia está em `output/pipeline-cfem/bruto/`. Origem registrada no lote: `https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv`. |
| Lote transformado | `output/pipeline-cfem/lote.json` | Fora do Git; SHA-256 `7d59e916c3e8d61bcb028d17e1b0f3a5fa1a47f96f080b70854a69a4ad731473`. |
| Capturas das tabelas municipais por ano e estado | `tmp/pipeline-referencias/anm-pa-<ano>.md` | 18 arquivos Markdown, de 2008 a 2025, fora do Git. São extrações da página oficial, não o corpo HTTP original. A referência informa consulta em 23/11/2026; os arquivos locais têm modificação em 24/11/2026 UTC. Não há registro do cabeçalho HTTP nem da edição da página. |
| Gerador das referências e comparações | `tmp/preparar-referencias-pipeline.py` | Fora do Git; SHA-256 `73c3378f3e3f3928195b3617bd8ea0a0ff4225b865aee30e06929fb76b280a95`. Lê as capturas e o lote, escreve as referências selecionadas e o relatório completo. |
| Relatório completo | `output/pipeline-cfem/conferencia-oficial.json` | Fora do Git; 1.232 comparações, das quais 15 divergentes; SHA-256 `677b34aa3c5344038c9d6f61546655aa90cddbc27bbb7e6f542bcbd0f267628a`. Contém apenas identificação, período e diferença, sem os dois valores comparados. |
| Referências selecionadas | `data/referencia-cfem-mensal-anm.json` | Versionadas no PR #47; 669 células de dez anos. Cada linha contém documento, URL, data de consulta e SHA-256 da captura Markdown correspondente. O validador ainda não confere os bytes dessa captura. |

A URL das tabelas municipais segue
`https://sistemas.anm.gov.br/arrecadacao/extra/relatorios/arrecadacao_cfem_muni.aspx?ano=<ano>&uf=PA`.
Em 24/11/2026, nova consulta à [tabela oficial de 2024](https://sistemas.anm.gov.br/arrecadacao/extra/relatorios/arrecadacao_cfem_muni.aspx?ano=2024&uf=PA)
retornou HTTP 200; os quatro valores de fevereiro abaixo continuam iguais aos
da captura local. Essa conferência visual de células não prova identidade dos
bytes da página ou explica a diferença no CSV. Os demais anos não foram
reconsultados nesta etapa.

## Capturas e cobertura

O SHA-256 é dos bytes dos arquivos Markdown locais. Nos dez anos selecionados,
ele coincide com o SHA-256 registrado nas referências. Nos oito anos excluídos,
o hash não consta no JSON de referências porque nenhuma célula foi selecionada.

| Ano | Células iguais / comparadas | Selecionado | SHA-256 da captura local |
| ---: | ---: | :---: | --- |
| 2008 | 65/65 | Sim | `60e3ed406a3c5385d014b9e11075df0c11f08229cf33d7ec47143d85a1d03c5d` |
| 2009 | 63/63 | Sim | `2dbd4ecfd7b92f5fbab67f92ebccb2754582be6a48c682cdf55994d3b93b62e4` |
| 2010 | 64/64 | Sim | `9eff4ef55ca7578f76777f67aa1fa8bfc6f5b62cc83b3f2353355be49d5821fa` |
| 2011 | 66/68 | Não | `92d1175fff9e820183a971b1d5533c57a78c01c88002182491dc88567d155c7d` |
| 2012 | 69/70 | Não | `da1c776e00cf5ca2035b183628b1e93b5974cb1028f28cfe06df64aaaec13b01` |
| 2013 | 63/63 | Sim | `ee99590a0d7c91b6e16b01f1a17f12ac270fbd5ec4d91edbf0e4762b0df786d3` |
| 2014 | 58/59 | Não | `6d4a5c92a4119270505d2676e46cee376a314abc7b38f5f8ca754eea045d237e` |
| 2015 | 67/67 | Sim | `3389ea68303194e4100d4808d9dd8aebd44877b81d17630d36d0130c73c0074e` |
| 2016 | 68/68 | Sim | `f801a5d1ff6051c9e6f893eee2583fc53860be74c84b9c66e265028810dededf` |
| 2017 | 67/67 | Sim | `072e97818f68b6cd8497a2180f94686e7644c625a052adc3a8250845f27c3ebc` |
| 2018 | 71/71 | Sim | `6f9fd645305fadfa13339c4f0268a4bea5329af5a8572209a8f62fcff31b506b` |
| 2019 | 62/63 | Não | `74af5a9f2d71783c8ab9b4466f8e4684fa27e8819a09d64a24a8d9d212ffd574` |
| 2020 | 60/60 | Sim | `45d30bc5bde89437bf2a42195e59e035f1b6075da518a94c7997f3fc5c52cd9d` |
| 2021 | 63/65 | Não | `b70547cb7911770492828401514ae1f2fc2e216873edb184566271cbe714c4d8` |
| 2022 | 72/73 | Não | `92c67bf2d40c8f5391c5a8a2c2d49e7ea50a7f8a23b62d7a75c93a4f613ba93f` |
| 2023 | 81/84 | Não | `027f66fb4822fdd4703d35f5109d0b6d6de44688962b01bd188e3b85726ab9fe` |
| 2024 | 77/81 | Não | `a0ecefae5f9e18c8bddc5f2e45fddbafc3df453fc5ad651d5ac8fca2905a09fa` |
| 2025 | 81/81 | Sim | `6ca8600e14ad898ee56cedda0a6caa0c16d04e5814db01c5c1ade961d9783ce1` |

Os oito anos excluídos somam 563 células examinadas, incluindo 548 iguais e 15
divergentes. A exclusão do ano inteiro é o critério usado pelo gerador local;
ela não significa arrecadação zero.

## As 15 diferenças a investigar

Valores em reais, com duas casas decimais. Os valores da tabela municipal foram
reconstituídos do relatório de diferenças e do lote, e conferidos nas capturas
locais; os quatro de fevereiro de 2024 também foram conferidos na página da ANM
em 24/11/2026.

| Período | Município (IBGE) | ANM | CSV agregado | Diferença |
| --- | --- | ---: | ---: | ---: |
| 04/2011 | Eldorado do Carajás (1502954) | 14.719,98 | 14.843,86 | +123,88 |
| 03/2011 | Marabá (1504208) | 424.531,79 | 425.001,44 | +469,65 |
| 07/2012 | Marabá (1504208) | 48.991,96 | 49.899,44 | +907,48 |
| 06/2014 | Marabá (1504208) | 711.575,12 | 711.675,12 | +100,00 |
| 07/2019 | Marabá (1504208) | 9.110.551,61 | 9.110.568,44 | +16,83 |
| 10/2021 | Marabá (1504208) | 16.058.185,04 | 16.058.642,73 | +457,69 |
| 09/2021 | Parauapebas (1505536) | 311.672.565,83 | 311.674.276,15 | +1.710,32 |
| 11/2022 | Marabá (1504208) | 12.312.135,55 | 12.312.362,57 | +227,02 |
| 01/2023 | Marabá (1504208) | 19.139.314,44 | 19.139.398,92 | +84,48 |
| 08/2023 | Marabá (1504208) | 13.565.052,20 | 13.565.064,20 | +12,00 |
| 09/2023 | Marabá (1504208) | 12.672.486,86 | 12.672.498,86 | +12,00 |
| 02/2024 | Canaã dos Carajás (1502152) | 105.934.383,43 | 211.859.194,00 | +105.924.810,57 |
| 02/2024 | Curionópolis (1502772) | 6.312.525,10 | 12.212.117,48 | +5.899.592,38 |
| 02/2024 | Marabá (1504208) | 14.299.913,00 | 28.332.578,73 | +14.032.665,73 |
| 02/2024 | Parauapebas (1505536) | 117.494.136,48 | 234.782.508,09 | +117.288.371,61 |

Todas as diferenças são positivas. Em 02/2024, as quatro diferenças são da
ordem dos respectivos valores oficiais; isso orienta a análise do detalhe das
linhas do CSV e das edições históricas, mas ainda não estabelece a causa.

## Próxima verificação

1. Arquivar as 18 capturas e o gerador em lugar versionado ou com retenção
   comprovável, com URL, data e SHA-256. Separar o hash da extração Markdown do
   hash de uma eventual resposta HTTP bruta.
2. Produzir relatório completo com os dois valores, filtros, contagem de linhas
   do CSV e identificação da edição para cada comparação; impedir validação se
   a captura não estiver disponível ou não conferir com o SHA-256 declarado.
3. Investigar as linhas que formam cada diferença, começando por 02/2024;
   comparar edições históricas do CSV com a tabela municipal e registrar a
   conclusão antes de atualizar referências ou republicar os oito anos.

Este registro é de execução, não altera o status das regras de negócio. A
publicação de um subconjunto de células de lote reprovado continua condicionada
à RN-VPU-01.
