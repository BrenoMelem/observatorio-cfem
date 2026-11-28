# PIB municipal (IBGE SIDRA 5938): diagnóstico, decisões e execução de 27/11/2026

Registro datado da preparação da fonte para o produto. Só recebe acréscimos.

## Entrada

- SIDRA, agregado 5938 (referência 2010), variáveis 37, 543, 498, 513, 517, 6575 e 525, os 12 municípios da RI Carajás, 2010 a 2023. Datas de modificação: 2010 a 2013 em 14/12/2016; 2021 a 2023 em 19/12/2025.
- Para o piloto: base de dados do IBGE no FTP, `Pib_Municipios/2022_2023/base/base_de_dados_2010_2023_xlsx.zip` (`Last-Modified` de 23/12/2025).

## Piloto (27/11/2026, `uv run python -m scripts.sondas.pib_municipal_ibge --xlsx ...`)

- 1.176 valores do SIDRA (12 × 14 × 7). 144 são `...`: em 2022 e 2023, só o PIB existe; impostos, VAB total e os quatro setores vêm vazios nos 12 municípios, no SIDRA e na base do FTP.
- SIDRA × base do FTP: 1.032 valores comparados, todos dentro de 0,5 mil reais (maior diferença 0,499). O SIDRA arredonda a mil reais; a base traz três casas.
- Identidades com os inteiros do SIDRA (2010–2021, 144 casos): soma dos setores − VAB = 0 em 83, ±1 em 59, ±2 em 2; VAB + impostos − PIB = 0 em 111, ±1 em 33. Com a base de três casas, as duas fecham em todos.
- VAB da indústria negativo em 2012 em quatro municípios: 1501576 (−2.890), 1501758 (−1.252), 1507151 (−1.750) e 1507508 (−456).

## Decisões do mantenedor nesta data

1. Publicar o valor do SIDRA, sem conferir com a base do FTP, "afinal é o mesmo dado". A escolha da fonte foi delegada; o SIDRA venceu pelo critério de automação (rota da RN-FNT-02, JSON estável, data de modificação por ano).
2. Regra geral: RN-VPU-07 ganhou a exceção da fonte oficial única, homologada pelas conferências internas; RN-VPU-12, a tolerância do arredondamento da própria fonte (até 2 e até 1 mil reais nas identidades do PIB). Registrado nas regras.
3. Escopo: o PIB e os seis componentes, sete indicadores.
4. VAB negativo: publicar como o IBGE publica.
5. Revisão: a edição nova prevalece; as mudanças vão para o relatório (`anos_alterados`).
6. Agenda: verificação mensal; só publica se as datas de modificação ou a resposta mudaram.
7. Manifesto: ids `pib_municipal`, `pib_impostos_liquidos`, `vab_total`, `vab_agropecuaria`, `vab_industria`, `vab_servicos`, `vab_administracao_publica`; unidade `BRL mil nominal`; dimensão econômica; desde 2010.
8. PR empilhado sobre o #59 (Pink Sheet).

## Execução do produto (27/11/2026, dado real)

- Comando: `uv run --project backend python -m observatorio.coleta pib`, com `OBS_DATA_DIR` e `OBS_PUBLICADO_DIR` em `tmp/pib/real`. SHA-256 da resposta de dados: `afc1ad13a115362ab62551d367f464fa97ad0fddc08073a4e02bb24498d800eb`.
- Resultado: aprovado, 1.176 linhas lidas e publicáveis. 144 municípios e anos com as identidades fechadas, 24 sem todos os componentes (2022 e 2023), nenhum excluído. Os quatro negativos de 2012 publicados.
- Segunda execução com `--somente-se-mudou`: `sem_mudanca`.
- API (`/api/v1/dimensoes/economica?municipio_id=1505536`): PIB de Parauapebas 49.756.255 mil reais em 2021 e 26.421.067 em 2023, `validado`; na base do FTP, 49.756.254,884 e 26.421.066,668. VAB da indústria de 2023 sai como `ausente`. O CSV e o Swagger respondem 200.
- Escolhas de implementação sem regra por trás, a revisar: (a) o dia 15 às 07:30 UTC na agenda mensal; (b) `sem_mudanca` exige datas de modificação **e** SHA-256 da resposta iguais, o que também pega uma correção sem mudança de data; (c) `0` no SIDRA (arredondamento a zero) vira `zero real`, porque o modelo não aceita `informado` com valor zero; não ocorre na série atual.

## O que não foi verificado

- O workflow `coletar-pib.yml` não rodou no GitHub (nem em branch temporária); `actionlint` não está instalado, a sintaxe foi conferida só como YAML.
- O gatilho `schedule` (só vale na `main`).
- O comportamento numa edição nova do IBGE, quando 2024 entrar e anos antigos forem revisados.

## O que continua pendente

- PIB per capita e participação da RI no PIB do Pará e do Brasil (RN-IND-09): dependem da população no produto e dos níveis UF e Brasil.
- 2002–2009 existem no agregado 5938, mas ficam fora pela RN-TMP-16.
