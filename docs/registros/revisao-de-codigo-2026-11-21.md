# Revisão de código de 21/11/2026

O `/code-review` rodado sobre o PR #41 (estrutura inicial do produto) olhou também o código já presente na `develop` e apontou 10 pontos. Por decisão do mantenedor de 21/11/2026, os pontos que afetam a dimensão econômica (a primeira versão, RN-ENT-12) foram resolvidos, e os demais ficam registrados aqui.

## Resolvidos

| # | Ponto | Onde foi resolvido |
| --- | --- | --- |
| 1 | Manifesto sem um indicador, ou sem `fonte`, `metodo` e `limitacoes`, gerava erro 500 na API | PR #41 |
| 2 | Erro de leitura do pacote (permissão, pasta no lugar do arquivo) gerava erro 500 | PR #41 |
| 3 | `/saude` dizia "pronto" sem manifesto ou com população inválida | PR #41 |
| 4 | `scripts/commodities/pink_sheet.py` publicava o ferro como série única em `USD/dmt` | PR #39 (contrato e spot separados, RN-TMP-13 e 14) |
| 5 | `scripts/financas/conferir_fonte_cfem.py` não tratava ponto de milhar nem espaços no valor e no código da ANM | branch `fix/laboratorio-economia`. O arquivo de distribuição de 19/11/2026 (2.239.128 linhas) não tem nenhum dos dois casos; a leitura foi alinhada com `distribuicao_municipal.py` e `reconciliar_distribuicao.py` |
| 6 | `versao_dados` não incluía o manifesto e era vazio nas dimensões sem população | PR #41 |
| 7 | O status ignorava indicador do manifesto fora do mapa de dimensões, lia o pacote várias vezes por requisição e comparava edições e datas como texto | PR #41 |
| 8 | Funções da API sem tipo de retorno | PR #41 |
| 10 | `scripts/financas/dca_anexos.py`: campo nulo (`cod_ibge` ou `exercicio`) no SICONFI derrubava a coleta inteira | branch `fix/laboratorio-economia` (vira divergência de contrato, registrada no resumo) |

## Pendentes

| # | Ponto | Situação |
| --- | --- | --- |
| 9a | O Pink Sheet grava `nivel_territorial = "global"`, valor que o esquema comum não prevê: RN-MOD-03 diz "município ou RI", e o DTO da API aceita só esses dois | É da economia, mas depende de decisão sobre a regra: RN-MOD-19 proíbe atribuir o preço internacional a um município, e nenhuma regra diz como o esquema representa uma série global |
| 9b | `scripts/emissoes/seeg.py` grava `nivel_territorial = "municipio"`, sem acento, diferente do `município` do esquema comum (RN-MOD-03) | Não é da economia (emissões, dimensão ambiental). Corrigir quando o SEEG for portado para `backend/src/observatorio/fontes/` ou antes de publicar emissões |
