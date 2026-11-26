# Preparação da CFEM arrecadada

A coleta usa o arquivo **completo** `https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv`, chave `CodigoMunicipio`, valores de `ValorRecolhido` e mês do campo `Mês`. O leitor lê o CSV em fluxo, em Windows-1252, exige o cabeçalho de 14 colunas observado em 30/10/2026 e soma valores internamente em precisão de quatro casas decimais. Somente os 12 códigos do escopo entram no recorte. O CSV nacional pode conter CPF/CNPJ e deve permanecer em `tmp/` ou na camada bruta ignorada pelo Git.

```bash
uv run python -m scripts.cfem.preparar tmp/CFEM_Arrecadacao.csv
uv run pytest scripts/testes/test_cfem.py
```

O relatório é escrito em `output/observatorio/tratado/cfem/relatorio.json` mesmo quando duplicatas bloqueiam o lote. Ele registra contagens, cobertura por mês, ausências e faixas sem exportar identificadores pessoais. Quando o lote passa nas checagens de estrutura e duplicidade, os arquivos tratados provisórios ficam na mesma pasta. Um total anual só é calculado quando o arquivo nacional tem 12 meses **e** o município tem valor em todos eles; a soma usa precisão decimal antes do arredondamento ao centavo. Ausência de município em mês existente é `ausente`, jamais zero. Este script é de laboratório e não publica. A CFEM arrecadada é coletada, reconciliada com a tabela oficial da ANM (RN-VPU-07) e publicada pelo produto: veja [pipeline-cfem.md](pipeline-cfem.md). A API do protótipo (`scripts/servidor`) não oferece CFEM.

Resultados datados das execuções (CFEM arrecadada) estão em [registros/verificacoes.md](../registros/verificacoes.md).
