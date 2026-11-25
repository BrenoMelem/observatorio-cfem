# Reexecução da fatia CFEM e pendências — 25/11/2026

Retrato da reexecução da CLI feita após o merge do PR #47 na `develop`. Complementa
[pipeline-cfem-2026-11-24.md](pipeline-cfem-2026-11-24.md) e
[inventario-reconciliacao-cfem-2026-11-24.md](inventario-reconciliacao-cfem-2026-11-24.md), que
continuam valendo como retrato de 24/11/2026. Não muda o status de nenhuma regra.

## O que foi executado

- **Entrada:** `arrecadacao.csv.gz` da Release `anm-2026-11-24-1924`, descompactado em
  `tmp/CFEM_Arrecadacao.csv` (fora do Git). SHA-256 do bruto lido pela CLI:
  `4b43854140bf60b0800fa5d72d90a235ff95c78ef7d8f04cb846faed0a849464`. A origem registrada no lote
  continua sendo a URL da ANM. O download direto da ANM falhou na verificação TLS, porque o servidor
  não envia o certificado intermediário; a verificação ficou ligada (ver pendência 9).
- **Comando:** o do [backend/README.md](../../backend/README.md), com `--arquivo tmp/CFEM_Arrecadacao.csv`,
  as 669 referências municipais, as referências nacionais e as capturas de
  `evidencias-anm-2026-11-23/`.
- **1ª tentativa: reprovada, por erro de ambiente.** `Permission denied` em
  `output/observatorio/publicado/.publicando`: a pasta pertence ao root (criada em 21/11/2026; a
  origem, provavelmente o Docker, não foi confirmada). A publicação anterior foi preservada
  (RN-VPU-03). O relatório dessa tentativa ficou em `output/observatorio/qualidade/`, fora do Git.
- **2ª tentativa: aprovada.** Com `OBS_DATA_DIR=output/pipeline-cfem-2026-11-25` e
  `OBS_PUBLICADO_DIR=output/pipeline-cfem-2026-11-25/publicado`:

| Item | Resultado |
| --- | --- |
| Linhas lidas | 2.319.355 |
| Recorte dos 12 municípios | 10.730 linhas |
| Repetições integrais no recorte | 28 (somadas e registradas, RN-VPU-11) |
| Municípios com linha no recorte | 11 de 12; **São Domingos do Araguaia (1507151) não aparece** (pergunta 2 de RN-CFE-10) |
| Reconciliação município/mês | 669 células, todas com diferença 0,00 |
| Controle nacional (RN-CFE-12) | 10 anos, diferença entre 0,0000% e 0,4393% (maior: 2008); nenhum acima de 1% |
| Erros | 0 |
| Versão do pacote | `429da52a012d5082d4df62d4b3c84df54b0fe6037fdb9bf3209a831a70e68ecc` |
| Relatório local | `output/pipeline-cfem-2026-11-25/qualidade/cfem-20261125T014749-c6748d22.json` |

Também passaram nesta data: `ruff check`, `ruff format --check`, `mypy`, `lint-imports` (2 contratos
mantidos) e `pytest` do backend (36 testes), e `ruff check scripts` e `pytest` do laboratório
(61 testes). A API e a demo **não** foram reabertas sobre o pacote novo nesta execução.

## Achado: a ANM republicou o CSV em 23/11/2026 e isso coincide com as 15 diferenças

O relatório `diferencas.md` da Release `anm-2026-11-23-1956` registra, para a arrecadação,
2.434.196 → 2.319.355 linhas (9 adicionadas, 114.850 removidas). A edição usada em 23 e 24/11 para
as 15 diferenças tinha 2.433.952 linhas (leitura de 30/10/2026).

No recorte dos 12 municípios, as linhas removidas somam **exatamente** as 15 diferenças do
[inventário de 24/11/2026](inventario-reconciliacao-cfem-2026-11-24.md): Eldorado do Carajás 2011
(R$ 123,88), Marabá 2011 (R$ 469,65), 2012 (R$ 907,48), 2014 (R$ 100,00), 2019 (R$ 16,83), 2021
(R$ 457,69), 2022 (R$ 227,02), 2023 (R$ 108,48 em quatro linhas, igual a 84,48 + 12,00 + 12,00),
Parauapebas 2021 (R$ 1.710,32) e as quatro de fevereiro de 2024 (Canaã R$ 105.924.810,57,
Curionópolis R$ 5.899.592,38, Marabá R$ 14.032.665,73, Parauapebas R$ 117.288.371,61).

**Conferência feita em 25/11/2026** (script local, fora do Git): a soma por município e mês da
edição nova do CSV contra as 18 capturas municipais versionadas (2008 a 2025), em decimal, sem
arredondar. Resultado: **1.232 células iguais em 1.232 comparadas**, inclusive as 563 dos oito anos
que a referência de 23/11 tinha excluído (as 15 divergentes passaram a coincidir).

**Limite:** a causa é inferida da coincidência dos valores. A ANM não confirmou que removeu linhas
repetidas ou espúrias, e as capturas Markdown não são o corpo HTTP original. Essa conferência não
entrou em `data/referencia-cfem-mensal-anm.json`, que continua com 669 células de dez anos.

Outros efeitos da edição nova: as repetições integrais do recorte caem de 129 para 28 e o recorte
de 10.827 para 10.730 linhas; o número de linhas de 2026 de Marabá cai em 66 (R$ 1.023,10).

## Pendências e recomendação de cada uma

Cada pendência ficou com uma recomendação. As de 1 a 7 vêm do registro de 24/11/2026; de 8 a 11 são
novas desta execução. Nenhuma recomendação foi executada nesta data, salvo onde está escrito.

| # | Pendência | Recomendação | Situação em 25/11/2026 |
| ---: | --- | --- | --- |
| 1 | Divergências dos oito anos (2011, 2012, 2014, 2019, 2021 a 2024) | Acrescentar as 563 células desses anos a `referencia-cfem-mensal-anm.json` a partir das capturas versionadas, com URL, data e hash; rodar a CLI e republicar. Citar a Release `anm-2026-11-23-1956` como a edição que concilia. Manter tolerância zero (RN-VPU-12) | Evidência obtida (1.232/1.232); referência não ampliada |
| 2 | Controle nacional (RN-CFE-12) | O controle já está na CLI e passou nos dez anos. Falta transcrever os totais nacionais dos oito anos acima e dos anos fora das capturas (2003 a 2007, 2026 parcial), com URL, data e hash | Parcial: implementado, cobertura de dez anos |
| 3 | Ausências municipais, inclusive São Domingos do Araguaia | Manter como lacuna, nunca zero (RN-CFE-07/09, decididas). Enviar as perguntas 2 e 3 de RN-CFE-10 à ANM por canal e responsável a definir | Sem canal definido |
| 4 | Automação da referência | Coletor das tabelas `arrecadacao_cfem_muni.aspx` e `arrecadacao_cfem_ano.aspx` que guarde o corpo HTTP bruto e o SHA-256 numa Release, no padrão de [arquivo-anm.md](../guias/arquivo-anm.md), e compare edições. A CLI deve ler o CSV da Release mais recente quando a ANM falhar | Não iniciado |
| 5 | Assistente (RN-ENT-07/08, PROPOSTA) | PR separado: busca determinística, controle somente leitura, mock com citações e casos de recusa. As metas de RN-ENT-08 seguem adiadas pelo mantenedor | Não iniciado |
| 6 | Integração com o front da equipe | Depende de autorização para editar o front. Enviar o contrato da API (rotas e esquema) ao responsável pelo front e manter a demo local até lá | Aguarda autorização |
| 7 | Docker e navegador | Subir o daemon, rodar `docker compose build api` com o pacote montado, validar CORS e conferir o gráfico e a tabela no navegador antes de 26/11/2026 | Não feito; a CLI foi reexecutada, a demo não |
| 8 | Edição do CSV mudou entre execuções | Registrar a edição (SHA-256 do bruto) em cada relatório, como já é feito, e citar a Release de origem. A Release `anm-*` é a fonte arquivada e reproduzível | Documentado aqui |
| 9 | Download direto da ANM falha no TLS | Usar `OBS_ANM_CA=scripts/cfem/certificados/sectigo-ov-r36.pem` (já previsto em `config.py` e no [guia](../guias/arquivo-anm.md)). Não desligar a verificação | Não testado nesta data |
| 10 | `output/observatorio/publicado` pertence ao root | O mantenedor deve devolver a pasta ao usuário (`chown`) ou apagá-la, ou o Docker deve rodar com o UID do usuário. Convém a CLI dar mensagem clara de permissão | Contornado com `OBS_PUBLICADO_DIR` |
| 11 | Duplicatas (RN-VPU-11): 129 na leitura de 30/10, 28 na edição de 25/11 | Medir o efeito em reais das 28 e atualizar a nota da seção 4 de `pendencias.md` quando o mantenedor reconfirmar o lote | Contagem registrada; efeito em reais não medido |

O relatório desta execução registra ainda 868 observações do recorte sem referência
correspondente; a recomendação 1 reduz esse número. Os 1.919 itens de ausência municipal seguem a
pendência 3.
