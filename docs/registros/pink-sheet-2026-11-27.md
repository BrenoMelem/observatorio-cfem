# Pink Sheet (ferro e cobre): diagnóstico e decisões de 27/11/2026

Registro datado da preparação da fonte para o produto. Só recebe acréscimos.

## Entrada
- Edição de nov/2026 (dados até out/2026), arquivo mensal `CMO-Historical-Data-Monthly.xlsx`, `Last-Modified` de 03/11/2026. Coletor de laboratório: `uv run python -m scripts.commodities.pink_sheet`.
- 558 linhas, sem nulos: contrato do ferro 21 anos (1985 a 2005), spot do ferro 215 meses (dez/2008 a out/2026), cobre 322 meses (jan/2000 a out/2026).

## Conferência (27/11/2026)
- Planilha anual da mesma edição: 64 séries-ano comparáveis dentro de 1 unidade da última casa publicada (cobre a inteiro, ferro a 0,1).
- PDF `CMO-Pink-Sheet-November-2026`: ago, set e out/2026 de cobre (14.326; 14.474; 14.508) e de ferro (96,3; 97,7; 90,8), as médias anuais de 2023 a 2025 e as médias trimestrais de jan–mar e jul–set/2026 coincidem com o coletor.
- Não verificado: contrato do ferro (1985 a 2005) e meses de 2008 a 2022 não têm segunda referência além da anual; todas as fontes são do mesmo publicador.

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
