# Pipeline do PIB municipal: PIB e VAB do IBGE, da coleta à API

Como rodar o PIB dos Municípios do IBGE (SIDRA, agregado 5938) de ponta a ponta. O padrão que cada fonte segue está em [padrao-de-pipeline-de-fonte.md](padrao-de-pipeline-de-fonte.md); o que cada execução encontrou fica em [registros/](../registros/). Este guia não traz resultados datados.

## O que é publicado

Sete indicadores anuais (`mes` vazio), por município da RI Carajás, desde 2010 (RN-FNT-02, RN-TMP-16), em `BRL mil nominal`. São mil reais inteiros, como o SIDRA publica, sem conversão:

| Indicador | Variável do SIDRA |
| --- | --- |
| `pib_municipal` | 37, PIB a preços correntes |
| `pib_impostos_liquidos` | 543, impostos líquidos de subsídios sobre produtos |
| `vab_total` | 498, VAB total |
| `vab_agropecuaria` | 513, VAB da agropecuária |
| `vab_industria` | 517, VAB da indústria (pode ser negativo) |
| `vab_servicos` | 6575, VAB dos serviços, exceto administração pública |
| `vab_administracao_publica` | 525, VAB da administração, defesa, educação, saúde e seguridade públicas |

Nos anos em que o IBGE divulga só o PIB, os componentes saem como lacuna (`natureza_valor = ausente`), nunca zero (RN-MOD-10). PIB per capita e participação da RI (RN-IND-09) ainda não são calculados.

## A cadeia

```
SIDRA 5938 (períodos e dados) → fontes/pib_ibge.py → validacao/pib_ibge.py → publicacao/ → api/
```

| Etapa | O que faz | Onde está |
| --- | --- | --- |
| Fonte | Lê a lista de anos do agregado (com a data de modificação de cada um) e pede, num só pedido, as sete variáveis dos 12 municípios desde 2010. Guarda as duas respostas com a URL e o SHA-256 num `indice.json` (RN-FON-13, RN-FON-14). Confere o nome e a unidade de cada variável (RN-VPU-04) e se a resposta traz exatamente os 12 municípios pedidos, com o nome conferido sem acento (RN-FNT-19, RN-TER-07). `...` é ausente, `..` não se aplica, `X` não divulgado e `-` zero | `backend/src/observatorio/fontes/pib_ibge.py` |
| Validação | Sem referência externa: o SIDRA é a única publicadora (exceção de RN-VPU-07 de 27/11/2026). Em cada município e ano com os sete valores, confere "soma dos setores = VAB total" (até 2 mil reais) e "VAB total + impostos = PIB" (até 1 mil reais), a tolerância do arredondamento (exceção de RN-VPU-12). Fora disso, o município e ano saem da publicação com o motivo, sem reprovar o lote. Uma revisão do IBGE em ano já publicado prevalece e aparece em `anos_alterados` | `backend/src/observatorio/validacao/pib_ibge.py` |
| Publicação | Um parquet por indicador no pacote parcial da fonte; a série validada não pode encolher (RN-VPU-02) | `backend/src/observatorio/publicacao/pacote.py` |
| API | Dimensão `economica`, com `valor` como texto decimal | `backend/src/observatorio/api/` |

## Rodar

Da raiz do repositório:

```
uv run --project backend python -m observatorio.coleta pib
uv run --project backend python -m observatorio.coleta pib --somente-se-mudou
```

Com `--somente-se-mudou`, termina em `sem_mudanca` se as datas de modificação dos anos e o SHA-256 da resposta forem iguais aos do relatório publicado. A saída é um resumo em JSON; o relatório completo (conferência, excluídos e o motivo, negativos, anos alterados) fica em `output/observatorio/qualidade/pib-*.json` e as respostas brutas em `output/observatorio/bruto/pib/`.

## Agenda

`coletar-pib.yml` verifica uma vez por mês, no dia 15, às 07:30 UTC, e só publica quando o SIDRA mudou (RN-TMP-02, decisão de 27/11/2026). O IBGE divulga uma edição por ano, em dezembro, com dois anos de defasagem. A publicação vai para uma Release `fonte-pib-*` (com as respostas brutas) e chama `publicar-pacote.yml`. Falha abre ou comenta uma issue. Como os outros, só vale a partir da `main`.

## Limites conhecidos

- Os valores são mil reais inteiros. Uma soma de vários municípios acumula até 0,5 mil reais de arredondamento por parcela. A base de dados do IBGE no FTP (`Pib_Municipios`) traz os mesmos números com três casas, mas não é usada (decisão de 27/11/2026).
- Não há conferência com publicação independente. As identidades contábeis pegam variável trocada ou erro de leitura, mas não um erro do próprio IBGE.
- O PIB per capita e a participação da RI no PIB do Pará e do Brasil (RN-IND-09) dependem da população no produto e dos níveis UF e Brasil do mesmo agregado; ainda não foram feitos.
