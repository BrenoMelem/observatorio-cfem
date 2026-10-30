# Preparação da CFEM arrecadada

A coleta usa o arquivo **completo** `https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv`, chave `CodigoMunicipio`, valores de `ValorRecolhido` e mês do campo `Mês`. O parser lê o CSV em fluxo, em Windows-1252, exige o cabeçalho de 14 colunas observado em 30/10/2026 e soma valores internamente em precisão de quatro casas decimais. Somente os 12 códigos do escopo entram no recorte. O CSV nacional pode conter CPF/CNPJ e deve permanecer em `tmp/` ou na camada bruta ignorada pelo Git.

```powershell
node scripts/preparar-cfem.mjs tmp/CFEM_Arrecadacao.csv
node --test test/cfem.test.mjs
```

O relatório é escrito em `output/observatorio/tratado/cfem/relatorio.json` mesmo quando duplicatas bloqueiam o lote. Ele registra contagens, cobertura por mês, ausências e faixas sem exportar identificadores pessoais. Quando o lote passa nas checagens de estrutura e duplicidade, os arquivos tratados provisórios ficam na mesma pasta. Um total anual só é calculado quando o arquivo nacional tem 12 meses **e** o município tem valor em todos eles; a soma usa precisão decimal antes do arredondamento ao centavo. Ausência de município em mês existente é `ausente`, jamais zero. A publicação da CFEM continua bloqueada até revisão das duplicatas e reconciliação com publicação independente da ANM, conforme RN-VPU-07 e RN-VPU-11. A API atual não oferece CFEM porque só lê a camada homologada.

Na execução de 30/10/2026, o arquivo tinha 2.433.952 linhas, com 129 duplicatas exatas no recorte, e a ANM já continha meses nacionais de janeiro a outubro de 2026. Bom Jesus do Tocantins só apareceu em janeiro de 2025 e não apareceu em 2026; São Domingos do Araguaia continuou ausente. Essas lacunas não têm causa confirmada.
