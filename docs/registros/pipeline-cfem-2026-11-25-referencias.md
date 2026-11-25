# Referências oficiais da CFEM de 2004 a 2025 — 25/11/2026

Retrato da ampliação das referências da validação da arrecadação (pendências 1, 2 e 11 do
[registro da manhã](pipeline-cfem-2026-11-25.md)). Complementa
[pipeline-cfem-2026-11-25-tarde.md](pipeline-cfem-2026-11-25-tarde.md). Não muda o status de nenhuma regra.

## Captura

- **Páginas:** `arrecadacao_cfem_muni.aspx?ano=AAAA&uf=PA` e `arrecadacao_cfem_ano.aspx?ano=AAAA` da ANM,
  de 2003 a 2025, baixadas em 25/11/2026 com `scripts/cfem/referencias_anm.py`. A verificação TLS ficou
  ligada, com o certificado intermediário `scripts/cfem/certificados/sectigo-ov-r36.pem`. As 46 páginas
  responderam HTTP 200.
- **Arquivo:** o corpo HTTP original de cada página, comprimido, em
  `docs/registros/evidencias-anm-2026-11-25/`, depois movida para [data/evidencias-anm/](../../data/evidencias-anm/) para receber as atualizações mensais (44 arquivos, 832 KB; as duas páginas de 2003
  foram retiradas, ver abaixo). O SHA-256 registrado em cada referência é o do HTML, e não o do `.gz`.
  Isso resolve o limite das capturas de 23/11/2026, que eram extrações em Markdown e não o corpo HTTP.
- **Conferência interna:** em cada linha extraída, a soma dos 12 meses fecha com a coluna Total da página.

## Resultado

| Item | Antes (23/11/2026) | Agora |
| --- | --- | --- |
| Células municipais de referência | 669 (10 anos) | **1.463** (2004 a 2025) |
| Totais nacionais | 10 anos | **22 anos** (2004 a 2025) |
| Das 669 células e 10 totais anteriores | | todos presentes e iguais |

Coleta com o `.csv.gz` da Release `anm-2026-11-25-0325`: **aprovada**, 0 erros. As 1.463 células
coincidem ao centavo (RN-VPU-12). O controle nacional (RN-CFE-12) ficou entre 0,0000% e 0,4393% (2008)
nos 22 anos. Restam 74 observações sem referência: as de 2003 e as de 2026. Na API, Parauapebas passa de
10 para 22 anos completos na série anual.

**2003 fica de fora.** Com as referências de 2003, a coleta foi reprovada com 22 erros: o arquivo da ANM
não tem janeiro a abril de 2003 no país inteiro, e a validação não homologa ano com mês nacional ausente.
Essa regra da implementação foi mantida. As referências começam em 2004 e as páginas de 2003 foram
retiradas da pasta de evidências.

**2026 fica de fora** por ser o ano corrente: a tabela muda a cada mês, e uma referência fixa reprovaria o
lote na tolerância zero assim que a ANM atualizasse o mês.

## Repetições integrais (pendência 11)

`scripts/cfem/analisar_duplicatas.py` passou a somar o valor das repetições. Na edição de 25/11/2026, as
28 repetições do recorte somam **R$ 22.973,97** em toda a série; a maior parte está em Parauapebas, 2020
(R$ 13.956,81). Todas têm a mesma `DataCriacao` da linha original. Como a tabela oficial coincide ao
centavo com as repetições somadas, a própria ANM parece contá-las. Isso foi registrado como nota de
evidência de RN-VPU-11, sem mudar a regra.

## Conferências

No backend: `ruff check`, `ruff format --check`, `mypy`, `lint-imports` e `pytest`. No laboratório:
`ruff check scripts` e `pytest`, com testes novos do extrator.

## O que continua pendente

- **Automação da referência (pendência 4).** O script é de laboratório e roda à mão. Para rodar no
  workflow, falta portá-lo para o produto e decidir quando a referência nova substitui a anterior, porque
  uma mudança de valor pede revisão humana.
- **Ano corrente:** um critério para incluir os meses fechados do ano corrente.
