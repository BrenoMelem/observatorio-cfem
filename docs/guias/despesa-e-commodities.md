# Coletas locais de despesa e commodities

Estes adaptadores ampliam o protótipo local. Não definem a arquitetura de produção nem alteram o status das regras de negócio.

## SICONFI, DCA Anexo I-E

Execute `uv run python -m scripts.financas.dca_lote --ano 2024`. O script consulta os 12 códigos IBGE como texto, valida exercício, anexo, paginação e as colunas de despesa empenhada, liquidada e paga, sem somar os três estágios. As linhas são guardadas em `output/observatorio/tratado/siconfi/` e o relatório em `output/observatorio/qualidade/`. A rota `/api/v1/despesa-funcao` responde 503 enquanto não houver lote homologado.

O escopo foi decidido em 11/11/2026 (RN-FNT-04): só a DCA, função e subfunção, com a linha "Despesas (Exceto Intraorçamentárias)" como controle de fechamento, e a série desde 2013 (anexo `Anexo I-E` em 2013, `DCA-Anexo I-E` de 2014 em diante). O tratamento de retificações foi decidido em 20/11/2026 (RN-TMP-04); a reconciliação independente (RN-VPU-07) foi decidida em 25/11/2026. No laboratório, `dca_lote` não publica. A despesa por função conferida com o RREO e a MSC (RN-FNT-04) é publicada pelo produto: veja [pipeline-siconfi.md](pipeline-siconfi.md).

## Pink Sheet, ferro e cobre (fonte principal)

Execute `uv run python -m scripts.commodities.pink_sheet`. O script lê a página do World Bank, acha o link do arquivo mensal (o endereço muda a cada edição), baixa, confere as colunas `Iron ore, cfr spot` e `Copper` e as unidades, e publica as observações com estado `provisório` em `output/observatorio/publicado/commodities.json`. Cada edição baixada fica em `output/observatorio/bruto/pink-sheet/`, com o endereço e o SHA-256 no relatório de qualidade. Se a página ou a planilha mudarem de forma, o script falha com aviso e não altera o lote publicado. Desde 21/11/2026 o ferro sai em duas séries separadas (RN-TMP-13, RN-TMP-14): `preco_minerio_ferro_contrato`, anual, em ¢/dmtu, de 1985 a 2005 (o ano só é aceito se os 12 meses da planilha repetirem o mesmo valor; senão o lote falha), e `preco_minerio_ferro_spot`, mensal, em `$/dmt`, de dezembro de 2008 em diante. O trecho de 2006 a novembro de 2008 fica fora. O cobre (`preco_cobre`) sai mensal desde 2000. Regras: RN-FNT-05, RN-FNT-06 e RN-TMP-13. O produto tem a sua coleta e o seu agendamento (guia: [pipeline-pinksheet.md](pipeline-pinksheet.md)); este script é só do laboratório.

## FRED, ferro e cobre (reserva)

O FRED é só reserva das commodities (RN-FNT-05) e nunca é emendado com o Pink Sheet. Ele grava no mesmo `commodities.json`, então rode um ou outro, não os dois em sequência sem querer. O ferro do FRED só serve de reserva a partir de dez/2008, e o script só publica a partir daí, como `preco_minerio_ferro_spot`.


Defina `FRED_API_KEY` no ambiente e execute `uv run python -m scripts.commodities.fred`. O script coleta `PIORECRUSDM` e `PCOPPUSDM` como séries globais mensais, preserva cada mês da resposta, inclusive valores ausentes, e publica observações com estado `provisório` em `output/observatorio/publicado/commodities.json`. A API expõe `/api/v1/commodities` e `/api/v1/commodities.csv`; o filtro `indicador` aceita `preco_minerio_ferro_contrato`, `preco_minerio_ferro_spot` ou `preco_cobre`. Nenhuma observação recebe município. Não há cálculo de média anual.

O início do ferro no FRED foi decidido em 10/11/2026 (divergência 17) e o recorte das duas séries em 11/11/2026 (RN-TMP-13). Uma reconciliação independente é necessária antes da homologação.

## Duplicatas da CFEM

Execute `uv run python -m scripts.cfem.analisar_duplicatas CAMINHO/CFEM_Arrecadacao.csv`. O relatório vai para `output/observatorio/qualidade/duplicatas-cfem.json`. A comparação usa os 14 campos completos apenas em memória; o JSON não contém CPF/CNPJ nem linhas brutas. A decisão sobre o tratamento continua com o mantenedor.

Resultados datados das execuções (despesa, commodities e duplicatas) estão em [registros/verificacoes.md](../registros/verificacoes.md).
