# Situação real da CFEM e das Releases — 26/11/2026

Retrato conferido em 26/11/2026, por volta das 12h UTC, depois do merge dos PRs #52, #53 e #54 na
`develop`. Atualiza os números de [pipeline-cfem-2026-11-25.md](pipeline-cfem-2026-11-25.md) e de
[pipeline-cfem-2026-11-25-tarde.md](pipeline-cfem-2026-11-25-tarde.md), que ainda usavam a referência
de 23/11/2026 (669 células, dez anos, 868 observações sem referência). Os números corretos daquela tarde
já estão em [pipeline-cfem-2026-11-25-referencias.md](pipeline-cfem-2026-11-25-referencias.md) e
[referencias-anm-automaticas-2026-11-25.md](referencias-anm-automaticas-2026-11-25.md). Não muda o
status de nenhuma regra.

## Releases no GitHub

| Release | Conteúdo | Situação |
| --- | --- | --- |
| `anm-2026-11-25-1358` (Latest) | `arrecadacao.csv.gz`, `distribuicao.csv.gz`, `autuacao.csv.gz`, `diferencas.md` | Edição mais recente dos arquivos da ANM |
| `pacote-cfem-2026-11-25-1253` | `publicado.tar.gz`, `qualidade-cfem.json` | Único pacote publicado. Criado pelo `coletar-cfem.yml` da `main` (disparo manual de 25/11/2026), sobre a edição `anm-2026-11-25-0325` |
| `fonte-cfem-*`, `fonte-siconfi-*`, `pacote-*` | | **Não existem.** Os workflows que as criam (#54) estão só na `develop` |

O relatório `qualidade-cfem.json` dessa Release já tem a referência ampliada e o ano aberto: situação
`aprovado`, 0 erros, 1.515 células conferidas, 47 provisórias, 5 aguardando volume e 22 observações
sem referência. Versão do pacote: `4d0f38dc40d8614d85dcd67055a9a1171db1d1fec18297c4cc5cecb30941e904`.

## Coleta real com a edição mais recente

- **Entrada:** `arrecadacao.csv.gz` da Release `anm-2026-11-25-1358`, SHA-256 do CSV
  `6307cbfccc63dec138cb41de891aba9e82f611347782604ae0b46bc3a4e6d83b`. Pacote anterior:
  `pacote-cfem-2026-11-25-1253`.
- **Comando:** o mesmo do `coletar-cfem.yml`, com `--referencias data/referencia-cfem-mensal-anm.json`,
  `--referencias-nacionais data/referencia-cfem-nacional-anm.json` e `--evidencias data/evidencias-anm`,
  da branch `develop` de 26/11/2026. Saída fora do Git, em `tmp/`.
- **Resultado:** aprovado, 0 erros.

| Item | Valor |
| --- | ---: |
| Linhas lidas | 2.319.359 |
| Linhas no recorte dos 12 municípios | 10.730 |
| Repetições integrais no recorte | 28 |
| Células município-mês conferidas ao centavo, 2004 a 2025 (validadas) | 1.463 |
| Células de 2026 conferidas (provisórias, janeiro a junho) | 47 |
| Células de 2026 aguardando volume (julho a outubro) | 5 |
| Células com diferença | 0 |
| Observações sem referência (todas de 2003) | 22 |
| Totais nacionais conferidos (RN-CFE-12), maior diferença | 22 anos, 0,4393% em 2008 |
| Municípios com linha no arquivo | 11 de 12 |
| Itens de ausência municipal (município e mês sem linha, 2003 a 2026) | 1.919 |
| Observações publicadas | 1.510 (1.463 validadas, 47 provisórias) |

Os números são os mesmos da Release de 25/11/2026: a edição `anm-2026-11-25-1358` tem 4 linhas a
mais no arquivo nacional, e o recorte continua com 10.730 linhas. A versão nova do pacote
(`9d638734a633334da0b6092c4605bc269719ad178f6dd15b2dd348484d750fb5`) tem as mesmas contagens por
estado de validação; os valores não foram comparados linha a linha.

### Onde estão as lacunas

- **2003:** o arquivo da ANM não tem janeiro a abril de 2003 no país inteiro, e a validação não homologa
  ano com mês nacional ausente. As 22 observações de 2003 ficam fora.
- **2026:** julho a outubro ficam fora porque a ANM ainda não lançou o volume normal de registros
  (exceção de 08/11/2026 da RN-CFE-06); novembro é o mês corrente. Janeiro a junho saem como provisórios.
- **Municípios:** observações publicadas por município, de 2004 a 2026: Parauapebas e Marabá 270,
  Canaã dos Carajás 262, Eldorado do Carajás 238, São Geraldo do Araguaia 171, Curionópolis 135,
  Palestina do Pará 99, Piçarra 29, São João do Araguaia 16, Brejo Grande do Araguaia 14 e Bom Jesus do
  Tocantins 6. São Domingos do Araguaia não tem linhas (RN-CFE-09). Os meses sem linha ficam ausentes,
  com causa não confirmada, nunca zero (RN-CFE-07).

## Situação das pendências do registro de 25/11/2026

| # | Pendência | Situação em 26/11/2026 |
| ---: | --- | --- |
| 1 | Referência mensal dos oito anos | **Resolvida** em 25/11/2026: 1.463 células de 2004 a 2025, todas iguais ao centavo |
| 2 | Controle nacional | **Resolvida** em 25/11/2026: 22 anos, de 2004 a 2025 |
| 3 | Ausências municipais | Sem mudança: sem canal com a ANM |
| 4 | Automação da referência | **Implementada** (`python -m observatorio.referencias` e `atualizar-referencias-anm.yml`, que está na `main`). Ainda não rodou no GitHub: o agendamento é no dia 5 |
| 5 | Assistente | Sem mudança |
| 6 | Integração com o front | Contrato pronto; envio depende do responsável pelo front |
| 7 | Docker e navegador | Docker conferido em 25/11/2026; a demo no navegador fica com o mantenedor |
| 8 | Edição do CSV | Resolvida: o relatório registra o SHA-256 e a Release de origem |
| 9 | TLS da ANM | Contornada pela Release |
| 10 | Pasta com dono root | Mitigada |
| 11 | Duplicatas | Efeito medido em 25/11/2026: R$ 22.973,97 nas 28 repetições; a regra não mudou |

## Achados desta data

- **Agendamentos do GitHub não dispararam.** Às 12h15 UTC de 26/11/2026, a última execução agendada do
  `arquivar-anm.yml` era a de 00h02 UTC; as de 04h, 08h e 12h UTC não aparecem. O `coletar-cfem.yml`
  (05h30 UTC) não tem nenhuma execução agendada desde que chegou à `main` em 25/11/2026, só o disparo
  manual. Os dois workflows estão ativos. A causa não foi investigada.
- **A `main` está atrás da `develop`.** Na `main` estão `arquivar-anm.yml`, `atualizar-referencias-anm.yml`,
  `ci.yml` e a versão antiga de `coletar-cfem.yml`, que publica `pacote-cfem-*`. `coletar-siconfi.yml` e
  `publicar-pacote.yml` só existem na `develop`. Enquanto não houver merge na `main`, o pacote servido
  continua só com a CFEM.

## O que não foi verificado

- Nenhum workflow foi disparado nesta data.
- A API não foi reaberta sobre a versão nova do pacote.
