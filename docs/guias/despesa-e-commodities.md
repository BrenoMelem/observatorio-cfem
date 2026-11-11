# Coletas locais de despesa e commodities

Estes adaptadores ampliam o protótipo local. Não definem a arquitetura de produção nem alteram o status das regras de negócio.

## SICONFI, DCA Anexo I-E

Execute `uv run python -m scripts.financas.dca_lote --ano 2024`. O script consulta os 12 códigos IBGE como texto, valida exercício, anexo, paginação e as colunas de despesa empenhada, liquidada e paga, sem somar os três estágios. As linhas são guardadas em `output/observatorio/tratado/siconfi/` e o relatório em `output/observatorio/qualidade/`. A rota `/api/v1/despesa-funcao` responde 503 enquanto não houver lote homologado.

Ainda faltam decidir as contas e o recorte função/subfunção, além de uma reconciliação independente (RN-FNT-04, RN-TMP-04 e RN-VPU-07). Nenhuma dessas decisões foi presumida e nenhuma despesa foi publicada.

## Pink Sheet, ferro e cobre (fonte principal)

Execute `uv run python -m scripts.commodities.pink_sheet`. O script lê a página do World Bank, acha o link do arquivo mensal (o endereço muda a cada edição), baixa, confere as colunas `Iron ore, cfr spot` e `Copper` e as unidades, e publica as observações com estado `provisório` em `output/observatorio/publicado/commodities.json`. Cada edição baixada fica em `output/observatorio/bruto/pink-sheet/`, com o endereço e o SHA-256 no relatório de qualidade. Se a página ou a planilha mudarem de forma, o script falha com aviso e não altera o lote publicado. O relatório lista os anos em que o ferro repete o valor anual em cada mês (até 2005). Regras: RN-FNT-05, RN-FNT-06 e RN-TMP-13. Não há agendamento: a coleta mensal automática ainda não foi montada.

## FRED, ferro e cobre (reserva)

O FRED é só reserva das commodities (RN-FNT-05) e nunca é emendado com o Pink Sheet. Ele grava no mesmo `commodities.json`, então rode um ou outro, não os dois em sequência sem querer. O ferro do FRED só serve de reserva a partir de dez/2008.


Defina `FRED_API_KEY` no ambiente e execute `uv run python -m scripts.commodities.fred`. O script coleta `PIORECRUSDM` e `PCOPPUSDM` como séries globais mensais, preserva cada mês da resposta, inclusive valores ausentes, e publica observações com estado `provisório` em `output/observatorio/publicado/commodities.json`. A API expõe `/api/v1/commodities` e `/api/v1/commodities.csv`; o filtro `indicador` aceita `preco_minerio_ferro` ou `preco_cobre`. Nenhuma observação recebe município. Não há cálculo de média anual.

O recorte de exibição e o início efetivo do ferro continuam em aberto (divergência 17). O relatório de qualidade registra essa pendência. Uma reconciliação independente é necessária antes da homologação.

## Duplicatas da CFEM

Execute `uv run python -m scripts.cfem.analisar_duplicatas CAMINHO/CFEM_Arrecadacao.csv`. O relatório vai para `output/observatorio/qualidade/duplicatas-cfem.json`. A comparação usa os 14 campos completos apenas em memória; o JSON não contém CPF/CNPJ nem linhas brutas. A decisão sobre o tratamento continua com o mantenedor.

Resultados datados das execuções (despesa, commodities e duplicatas) estão em [registros/verificacoes.md](../registros/verificacoes.md).
