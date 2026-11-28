# Pipeline do Pink Sheet: preços de ferro e cobre, da coleta à API

Como rodar os preços globais de minério de ferro e cobre do World Bank de ponta a ponta. O padrão que cada fonte segue está em [padrao-de-pipeline-de-fonte.md](padrao-de-pipeline-de-fonte.md); o que cada execução encontrou fica em [registros/](../registros/). Este guia não traz resultados datados.

## O que é publicado

Três indicadores, todos `nivel_territorial = global`, sem município (RN-MOD-19):

| Indicador | Medida | Período | Unidade |
| --- | --- | --- | --- |
| `preco_minerio_ferro_contrato` | Contrato anual (`mes` vazio) | 1985 a 2005 | `¢/dmtu` |
| `preco_minerio_ferro_spot` | Spot mensal, 62% Fe, cfr China | de janeiro de 2009 | `USD/dmt` |
| `preco_cobre` | Mensal, LME grau A | de janeiro de 2000 | `USD/t` |

O contrato e o spot nunca vão no mesmo eixo sem aviso (RN-TMP-13, RN-TMP-14). O filtro municipal da API não esconde essas séries.

## A cadeia

```
World Bank (planilhas mensal e anual) → fontes/pink_sheet.py → validacao/pink_sheet.py → publicacao/ → api/
```

| Etapa | O que faz | Onde está |
| --- | --- | --- |
| Fonte | Acha na página do World Bank os endereços das planilhas mensal e anual (o código do endereço muda a cada edição), baixa as duas e guarda cada uma com o SHA-256 e a origem num `indice.json` (RN-FON-13, RN-FON-14). Lê as colunas pelo nome e confere a unidade; layout novo falha (RN-VPU-04). Ausente fica ausente | `backend/src/observatorio/fontes/pink_sheet.py` |
| Validação | Compara a média anual da mensal com a planilha anual da mesma edição, com tolerância menor que 1 unidade da última casa dela (RN-VPU-12, exceção de 27/11/2026). Ano fechado e conferido sai `validado`; o ano corrente, incompleto, sai `provisório` e sem média (RN-TMP-12). Ano incompleto fora do ano corrente, sem referência ou divergente fica fora, com o motivo, sem reprovar o lote. Uma correção do World Bank em ano já publicado vale se passar na conferência e aparece em `anos_alterados` | `backend/src/observatorio/validacao/pink_sheet.py` |
| Publicação | Um parquet por indicador no pacote parcial da fonte; a série validada não pode encolher (RN-VPU-02) | `backend/src/observatorio/publicacao/pacote.py` |
| API | Dimensão `economica`, com `valor` como texto decimal | `backend/src/observatorio/api/` |

## Rodar

Da raiz do repositório (a leitura das planilhas usa o extra `coleta`):

```
uv run --project backend --extra coleta python -m observatorio.coleta pinksheet
uv run --project backend --extra coleta python -m observatorio.coleta pinksheet --somente-se-mudou
```

Com `--somente-se-mudou`, termina em `sem_mudanca` se as duas planilhas têm o mesmo SHA-256 do relatório publicado. A saída é um resumo em JSON; o relatório completo (conferidos, excluídos e o motivo, anos alterados) fica em `output/observatorio/qualidade/pinksheet-*.json` e as planilhas em `output/observatorio/bruto/pinksheet/`.

## Agenda

`coletar-pinksheet.yml` tenta uma vez por dia nos dias 4 a 10 de cada mês, às 07:00 UTC, e só publica quando as planilhas mudaram. A publicação vai para uma Release `fonte-pinksheet-*` (com as planilhas brutas) e chama `publicar-pacote.yml`. No dia 10, sem edição nova no mês, abre uma issue. Como os outros, só vale a partir da `main`.

## Limites conhecidos

- A conferência é com outra planilha do mesmo publicador. Uma checagem com o FMI (27/11/2026) está em [registros/pink-sheet-2026-11-27.md](../registros/pink-sheet-2026-11-27.md).
- Dezembro de 2008, sozinho no ano, fica fora por não poder ser conferido, embora a RN-TMP-13 fale em dezembro de 2008.
- O FRED não foi portado; continua só no laboratório (RN-FNT-05).
