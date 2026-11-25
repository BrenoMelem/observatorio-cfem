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

- Os workflows não rodaram no GitHub: `schedule`, `workflow_dispatch` e a chamada `workflow_call` entre arquivos só valem a partir da `main`. Depois do merge, dispare `coletar-siconfi.yml` com `forcar` à mão e confira que o `publicar-pacote.yml` roda ao fim.
- A primeira execução depois do merge: se nenhuma Release `fonte-*` existir, a CFEM parte do `pacote-cfem-*` antigo e o SICONFI parte do zero; o geral cria o primeiro `pacote-AAAA-MM-DD-HHMM`. Convém rodar a CFEM com `forcar` antes, para o parcial `fonte-cfem-*` existir.
- `actionlint` não estava instalado.
