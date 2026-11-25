# Referências da ANM automatizadas e ano aberto como provisório — 25/11/2026

Retrato da pendência 4 do [registro da manhã](pipeline-cfem-2026-11-25.md), feito depois de
[pipeline-cfem-2026-11-25-referencias.md](pipeline-cfem-2026-11-25-referencias.md). Não muda o status
de nenhuma regra.

## Decisões do mantenedor nesta data

Tomadas em 25/11/2026, ao planejar a automação:

1. **Atualização da referência:** quando a tabela da ANM muda, o workflow abre um PR para revisão; a
   referência nova só vale depois do merge.
2. **Código:** o coletor fica no produto (`backend/`), e não no laboratório.
3. **Frequência:** mensal.
4. **Ano corrente:** os meses já fechados entram na referência.
5. **Estado dos meses do ano aberto:** saem como "provisório", como diz a RN-CFE-06, e não como
   "validado".
6. **Mês que a ANM ainda está lançando** (abaixo de 50% da mediana de registros, exceção de 08/11/2026
   da RN-CFE-06): fica fora da publicação, sem reprovar o lote.

A decisão 5 aplica a RN-CFE-06 como está escrita e não abre exceção. Ela substitui, na implementação, a
decisão de 23/11/2026 da demonstração ("meses de ano incompleto não entram"), registrada no
[plano de 23/11/2026](../guias/plano-pipeline-cfem-2026-11-23.md).

## Por que "mês fechado" não basta

Na edição de 25/11/2026 do arquivo da ANM, a mediana de registros por mês de 2004 a 2025 é 8.365. Em
2026:

| Mês | Registros | Situação |
| --- | ---: | --- |
| Janeiro a junho | 9.993 a 20.174 | acima de 50% da mediana: provisório |
| Julho | 1.834 | abaixo: aguardando volume |
| Agosto a outubro | 259 a 373 | abaixo: aguardando volume |
| Novembro | 64 | mês corrente, sem referência |

Julho a outubro já fecharam no calendário, mas a ANM ainda não lançou a maior parte dos registros.
Publicá-los mostraria uma queda que não existe.

## Execução

- **Coletor** (`python -m observatorio.referencias`) contra a ANM, com data 25/11/2026: 45 páginas, de
  2004 a 2026. Mudou só o Pará em 2026 (52 células novas, de janeiro a outubro); nenhum valor de 2004 a
  2025 mudou e nenhuma captura antiga foi regravada.
- **Coleta** com o `.csv.gz` da Release `anm-2026-11-25-0325` e a referência nova: **aprovada**, 0 erros.
  1.463 células validadas de 2004 a 2025, 47 provisórias em 2026 (janeiro a junho) e 5 células aguardando
  volume (julho a outubro). Restam 22 observações sem referência, as de 2003.
- **API** local e Docker, com a imagem reconstruída: Parauapebas tem janeiro a junho de 2026 como
  provisório; o total anual de 2026 é recusado com nota, e o de 2025 continua R$ 1.102.944.678,86.
- **Workflow** `atualizar-referencias-anm.yml`: não executado no GitHub, porque só roda a partir da
  branch padrão. Os passos do coletor e da coleta foram reproduzidos localmente.
- **Conferências:** no backend, `ruff`, `mypy`, `lint-imports` e `pytest`; no laboratório, `ruff check
  scripts` e `pytest`.

## Mudança de lugar das capturas

As capturas saíram de `docs/registros/evidencias-anm-2026-11-25/` para `data/evidencias-anm/`, porque
passam a ser atualizadas todo mês e `registros/` só recebe acréscimos. O histórico de cada página fica no
Git. As capturas em Markdown de 23/11/2026 continuam em `docs/registros/evidencias-anm-2026-11-23/`.
