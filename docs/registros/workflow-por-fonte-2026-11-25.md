# Um workflow por fonte e um geral para o pacote (25/11/2026)

## Decisões do mantenedor nesta data

| Pergunta | Decisão |
| --- | --- |
| Como as coletas de várias fontes publicam o pacote? | Um workflow por fonte e um geral que monta o pacote servido pela API (resposta do mantenedor à escolha "a revisar" do PR do SICONFI) |
| Como o geral é acionado? | `workflow_call` ao fim de cada coleta, "se o pacote/dados for válido": só quando a fonte foi aprovada; também à mão |
| Onde cada fonte guarda o resultado aprovado? | Release por fonte (`fonte-cfem-*`, `fonte-siconfi-*`) |

## O que mudou

- `coletar-cfem.yml` e `coletar-siconfi.yml` partem só do pacote parcial anterior da própria fonte (a CFEM, na falta de `fonte-cfem-*`, do antigo `pacote-cfem-*`), publicam `fonte-*` e chamam o geral se o lote foi aprovado. Voltaram a ter grupos de concorrência próprios.
- `publicar-pacote.yml` baixa o último parcial de cada fonte, roda `observatorio.coleta montar` e cria a Release `pacote-AAAA-MM-DD-HHMM`; falha abre a issue "Montagem do pacote falhou" e o pacote anterior continua valendo (RN-VPU-03). Grupo de concorrência `publicar-pacote`.
- `publicacao/montagem.py`: confere o hash de cada arquivo dos parciais, recusa indicador repetido e manifesto sem algum indicador, e troca o ponteiro por último.
- Isso substitui o encadeamento provisório do PR do SICONFI (todas as coletas partindo do pacote mais recente). ADR-011, guias e a skill `adicionar-fonte` foram atualizados.

## Como foi conferido

`backend/`: `ruff check`, `ruff format --check`, `mypy` estrito, `lint-imports` e `pytest` (66 testes; `test_montagem.py` cobre a junção das duas fontes servida pela API, parcial corrompido que conserva o pacote anterior, indicador repetido e lista vazia). Sintaxe YAML dos três workflows lida com PyYAML.

## O que não foi verificado

- Nada de `schedule` ou `workflow_dispatch`, que só valem a partir da `main`; o resto foi exercitado (seção seguinte).
- O caminho de falha dos workflows (issue aberta quando a montagem ou a coleta reprova) não foi exercitado no GitHub.
- `actionlint` não estava instalado.

## Teste no GitHub, em branch temporária (25/11/2026)

Branch `teste/workflows-tmp`, com `push` como gatilho de `coletar-cfem.yml` e `coletar-siconfi.yml` (só nela), sobre os dados reais. Resultado: os dois workflows terminaram com sucesso, inclusive o `publicar-pacote.yml` chamado por `workflow_call`. A CFEM partiu do `pacote-cfem-2026-11-25-1253` (fallback), criou `fonte-cfem-*` e um pacote só com a CFEM; o SICONFI criou `fonte-siconfi-*` e o pacote seguinte reuniu `cfem_arrecadada` (2026) e as três despesas (2025), com `qualidade-cfem.json` e `qualidade-siconfi.json`. Isso confirma que uma fonte não apaga a outra. O teste apontou um defeito, corrigido antes do merge: o pacote era criado com `--latest=true` e tomaria o posto de Latest da `anm-*`; passou a `--latest=false`. Depois do teste, as 4 Releases, as tags e a branch foram apagadas; a Latest voltou a ser `anm-2026-11-25-1358` e não ficou issue aberta.
