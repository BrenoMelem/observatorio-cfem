# Coletas locais de despesa e commodities

Estes adaptadores ampliam o protótipo local. Não definem a arquitetura de produção nem alteram o status das regras de negócio.

## SICONFI, DCA Anexo I-E

Execute `uv run python -m scripts.financas.dca_lote --ano 2024`. O script consulta os 12 códigos IBGE como texto, valida exercício, anexo, paginação e as colunas de despesa empenhada, liquidada e paga, sem somar os três estágios. As linhas são guardadas em `output/observatorio/tratado/siconfi/` e o relatório em `output/observatorio/qualidade/`. A rota `/api/v1/despesa-funcao` responde 503 enquanto não houver lote homologado.

Em 03/11/2026, a consulta de 2024 leu 2.537 linhas nos 12 municípios. A consulta de 2025 leu 2.534 linhas, mas Bom Jesus do Tocantins (`1501576`) retornou zero linhas. Por isso, o lote de 2025 foi bloqueado por cobertura. A DCA não informa na resposta um campo de retificação. Ainda faltam decidir as contas e o recorte função/subfunção, além de uma reconciliação independente (RN-FNT-04, RN-TMP-04 e RN-VPU-07). Nenhuma dessas decisões foi presumida e nenhuma despesa foi publicada.

## FRED, ferro e cobre

Defina `FRED_API_KEY` no ambiente e execute `uv run python -m scripts.commodities.fred`. O script coleta `PIORECRUSDM` e `PCOPPUSDM` como séries globais mensais, preserva cada mês da resposta, inclusive valores ausentes, e publica observações com estado `provisório` em `output/observatorio/publicado/commodities.json`. A API expõe `/api/v1/commodities` e `/api/v1/commodities.csv`; o filtro `indicador` aceita `preco_minerio_ferro` ou `preco_cobre`. Nenhuma observação recebe município. Não há cálculo de média anual.

O recorte de exibição e o início efetivo do ferro continuam em aberto (divergência 17). O relatório de qualidade registra essa pendência. Uma reconciliação independente é necessária antes da homologação. Em 03/11/2026, a variável `FRED_API_KEY` não estava disponível neste ambiente, portanto a coleta real do FRED não foi executada; os testes usam respostas simuladas.

## Duplicatas da CFEM

Execute `uv run python -m scripts.cfem.analisar_duplicatas CAMINHO/CFEM_Arrecadacao.csv`. O relatório vai para `output/observatorio/qualidade/duplicatas-cfem.json`. A comparação usa os 14 campos completos apenas em memória; o JSON não contém CPF/CNPJ nem linhas brutas. Na leitura local de 03/11/2026, foram 2.433.952 linhas nacionais, 10.827 linhas no recorte, 129 duplicatas integrais em 31 grupos município/ano/mês; as 129 duplicatas tinham `DataCriacao` igual à primeira ocorrência. A decisão sobre o tratamento continua com o mantenedor.
