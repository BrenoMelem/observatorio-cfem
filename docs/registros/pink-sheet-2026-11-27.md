# Pink Sheet (ferro e cobre): diagnóstico e decisões de 27/11/2026

Registro datado da preparação da fonte para o produto. Só recebe acréscimos.

## Entrada
- Edição de nov/2026 (dados até out/2026), arquivo mensal `CMO-Historical-Data-Monthly.xlsx`, `Last-Modified` de 03/11/2026. Coletor de laboratório: `uv run python -m scripts.commodities.pink_sheet`.
- 558 linhas, sem nulos: contrato do ferro 21 anos (1985 a 2005), spot do ferro 215 meses (dez/2008 a out/2026), cobre 322 meses (jan/2000 a out/2026).

## Conferência (27/11/2026)
- Planilha anual da mesma edição: 64 séries-ano comparáveis dentro de 1 unidade da última casa publicada (cobre a inteiro, ferro a 0,1).
- PDF `CMO-Pink-Sheet-November-2026`: ago, set e out/2026 de cobre (14.326; 14.474; 14.508) e de ferro (96,3; 97,7; 90,8), as médias anuais de 2023 a 2025 e as médias trimestrais de jan–mar e jul–set/2026 coincidem com o coletor.
- Não verificado: contrato do ferro de 1985 a 1989 (o FMI começa em 1990) e a unidade `¢/dmtu` por fonte externa; o ferro spot só confere em tendência com o FMI, não em valor.

## Conferência com o FMI (27/11/2026, via DBnomics, série `IMF/PCPS` mundial, USD)
O FRED estava inacessível; as séries dele (`PIORECRUSDM`, `PCOPPUSDM`) vêm do FMI, então a comparação foi feita nos dados do FMI (publicador independente do World Bank), até jun/2025.
- Cobre, 306 meses (2000 a 2025): mediana da diferença 0,04%, máximo 1,22% (jan/2009); de 2014 a 2021 os valores coincidem.
- Ferro spot, 199 meses (dez/2008 a jun/2025): mediana 0,41%, p95 3,7%, máximo 8,66% (set/2021). Mesma trajetória, mas o FMI usa outra cotação; não bate valor a valor.
- Contrato do ferro, 1990 a 2005: a razão entre a média anual do FMI e o contrato do Pink Sheet é constante (43,2 ±0,1%) em 16 anos, o que confirma a forma da série, não a unidade. O FMI não cobre 1985 a 1989.

## Decisões do mantenedor nesta data
1. Referência e tolerância: planilha anual, menor que 1 unidade da última casa (exceção em RN-VPU-12); registrado nas regras.
2. Estado: anos fechados `validado`, ano corrente `provisório` (RN-TMP-12); ano incompleto (spot de 2008) não é conferido.
3. Manifesto: ids `preco_minerio_ferro_contrato`, `preco_minerio_ferro_spot` e `preco_cobre`, unidades `¢/dmtu`, `USD/dmt`, `USD/t`.
4. Revisão do World Bank: a edição nova prevalece se passar na conferência; as mudanças em relação ao parcial anterior vão para o relatório.
5. Agenda: tentativas diárias nos dias 4 a 10 de cada mês, 07:00 UTC; só publica quando o SHA-256 do arquivo é novo; issue de falha se nenhuma edição nova aparecer até o dia 10.
6. FRED: não portado por ora.
7. PRs: dois empilhados (peças comuns para série global; depois a fonte, o workflow e a documentação).

## O que continua pendente
- Código do produto, testes, workflow e execução com dado real (fases 3 a 5 da skill).
- Opcional: o PDF como segunda referência dos meses recentes.

## Execução do produto (27/11/2026, dado real)
- Comando: `uv run --project backend --extra coleta python -m observatorio.coleta pinksheet`, com `OBS_DATA_DIR` e `OBS_PUBLICADO_DIR` em `tmp/pinksheet/real`. Edição de nov/2026 (planilhas baixadas na hora; SHA-256 de cada uma no `indice.json` do bruto).
- Resultado: aprovado, 558 linhas lidas. Contrato do ferro: 21 anos validados. Spot: 17 anos validados (2009 a 2025), 1 provisório (2026), 1 excluído (2008, 1 mês de 12). Cobre: 26 anos validados (2000 a 2025) e 2026 provisório. Nenhum ano divergente; `anos_alterados` vazio (primeira publicação).
- API (`/api/v1/dimensoes/economica`, filtro `municipio_id=1505536`): as séries globais aparecem apesar do filtro; ago/set/out de 2026 do cobre e do spot batem com o PDF da edição (14.326, 14.474, 14.508; 96,3, 97,7, 90,8). O CSV responde 200.
- Decisões de implementação sem regra por trás, a revisar: (a) o filtro municipal não esconde série global; (b) dezembro de 2008 fica fora do spot, porque o ano de 2008 não fecha e só o ano corrente pode ser provisório; (c) a planilha anual usada é a aba `Annual Prices (Nominal)`; (d) `anos_alterados` compara uma impressão digital dos valores de cada ano, não o valor antigo e o novo.
- Workflow testado de verdade em 28/11/2026 numa branch temporária com gatilho `push` (apagada depois): o job `coletar` e o `publicar` (via `workflow_call`) terminaram com sucesso; a Release `fonte-pinksheet-*` trouxe `publicado.tar.gz`, `qualidade-pinksheet.json` (aprovado, mesmos números acima) e `pinksheet-bruto.tar.gz`; o pacote montado tinha os sete indicadores (CFEM, despesa por função e os três preços). As Releases de teste foram apagadas e a Latest (`anm-*`) e as issues ficaram como antes.
- Não verificado: o gatilho `schedule` (só vale na `main`), a execução `--somente-se-mudou` no CI e a issue do dia 10.
