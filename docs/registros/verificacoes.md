# Registro de verificações

Resultados datados das coletas e leituras de teste, retirados dos guias em `docs/guias/` para que eles só digam como usar. Cada item é o texto original, sem alteração. Não são regras: as regras e o que mudou delas estão em [regras-de-negocio](../regras-de-negocio/README.md).

Há também um relatório mais longo, [duplicatas-cfem-2026-10-30.md](duplicatas-cfem-2026-10-30.md).

| Tema | Data | Guia de origem |
| --- | --- | --- |
| População (SIDRA) | 30/10/2026 | [populacao.md](../guias/populacao.md) |
| CFEM arrecadada | 30/10/2026 | [cfem.md](../guias/cfem.md) |
| Despesa (DCA do SICONFI) | 03/11/2026 | [despesa-e-commodities.md](../guias/despesa-e-commodities.md) |
| Commodities (FRED) | 03/11/2026 | [despesa-e-commodities.md](../guias/despesa-e-commodities.md) |
| Duplicatas da CFEM | 03/11/2026 | [despesa-e-commodities.md](../guias/despesa-e-commodities.md) |

## População (SIDRA), 30/10/2026

A resposta SIDRA de 2026 foi conferida nos 12 códigos em 30/10/2026.

## CFEM arrecadada, 30/10/2026

Na execução de 30/10/2026, o arquivo tinha 2.433.952 linhas, com 129 duplicatas exatas no recorte, e a ANM já continha meses nacionais de janeiro a outubro de 2026. Bom Jesus do Tocantins só apareceu em janeiro de 2025 e não apareceu em 2026; São Domingos do Araguaia continuou ausente. Essas lacunas não têm causa confirmada.

## Despesa (DCA do SICONFI), 03/11/2026

Em 03/11/2026, a consulta de 2024 leu 2.537 linhas nos 12 municípios. A consulta de 2025 leu 2.534 linhas, mas Bom Jesus do Tocantins (`1501576`) retornou zero linhas. Por isso, o lote de 2025 foi bloqueado por cobertura. A DCA não informa na resposta um campo de retificação.

## Commodities (FRED), 03/11/2026

Em 03/11/2026, a variável `FRED_API_KEY` não estava disponível neste ambiente, portanto a coleta real do FRED não foi executada; os testes usam respostas simuladas.

## Duplicatas da CFEM, 03/11/2026

Na leitura local de 03/11/2026, foram 2.433.952 linhas nacionais, 10.827 linhas no recorte, 129 duplicatas integrais em 31 grupos município/ano/mês; as 129 duplicatas tinham `DataCriacao` igual à primeira ocorrência.
