# Emissões do SEEG (laboratório)

Este adaptador é de teste e não define a arquitetura de produção (RN-FNT-14, RN-FON-15).

## Planilha municipal

O SEEG não tem API: a planilha é baixada por edição. Em 10/11/2026 a edição 14.0 (atualizada em 09/11/2026) tinha o arquivo municipal de 229 MB e o nacional de 207 MB; por isso o bruto fica **fora do Git** e pode ser arquivado numa Release do GitHub, como se faz com a ANM (RN-TMP-18). No Git ficam só o recorte e os metadados.

Execute `uv run python -m scripts.emissoes.seeg` para baixar e ler, ou `uv run python -m scripts.emissoes.seeg --arquivo CAMINHO` para usar uma planilha já baixada. A leitura da aba `Dados` leva alguns minutos.

O script:

- baixa a planilha para `output/observatorio/bruto/seeg/` (fora do Git) e registra o tamanho e o SHA-256;
- confere a aba `Dados` e as colunas; se o contrato mudar, falha com aviso e não altera o lote publicado;
- reconstitui o código IBGE a partir de `ID Território`, que vem como "1" mais os 7 dígitos do IBGE;
- soma por município, tipo (na edição 14.0: `Emissão`, `Emissão NCI` e `Remoção`, sem compensar um com o outro), setor e ano, e publica em `output/observatorio/publicado/emissoes-seeg.json`, com estado `provisório`;
- grava o relatório em `output/observatorio/qualidade/` com a edição, o endereço, os municípios encontrados e ausentes, os nomes divergentes e a citação pedida pelo SEEG.

A unidade da planilha não foi confirmada: o nome do arquivo diz CO2e (GWP-AR5) e a aba `Leia antes` não trouxe texto na leitura de 10/11/2026. O campo de unidade do resultado diz isso.

## Arquivar a edição numa Release (manual)

Depois de conferir o relatório, a edição bruta pode ir para uma Release com tag própria, por exemplo:

`gh release create seeg-14.0 CAMINHO/Dados-municipais-resumido-CO2e-GWP-AR5-14.0.xlsx --title "SEEG 14.0 (bruto)" --notes "Baixado em AAAA-MM-DD. SHA-256 no relatório de qualidade."`

O SEEG pede a citação: "Fonte: SEEG – Sistema de Estimativa de Emissões e Remoções de Gases de Efeito Estufa, Observatório do Clima, acessado em [data] – seeg.eco.br".
