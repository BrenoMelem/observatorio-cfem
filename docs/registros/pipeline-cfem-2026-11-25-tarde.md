# Cadeia completa da CFEM e pendências resolvidas — 25/11/2026 (tarde)

> **Nota de 26/11/2026:** os números de referência deste retrato (669 células, dez anos, 868 observações sem referência) foram superados no mesmo dia. A situação conferida está em [pipeline-cfem-2026-11-26.md](pipeline-cfem-2026-11-26.md).

Retrato da preparação do pipeline para a apresentação de 26/11/2026, na branch
`docs/pipeline-apresentavel`. Complementa [pipeline-cfem-2026-11-25.md](pipeline-cfem-2026-11-25.md),
que continua valendo como retrato da manhã. Não muda o status de nenhuma regra. O passo a passo está no
[guia](../guias/pipeline-cfem.md).

## O que foi executado

- **Entrada:** `arrecadacao.csv.gz` da Release `anm-2026-11-25-0325`, lido direto pela coleta, sem
  descompactar à mão. Diferença para a edição anterior: 1 linha adicionada e 1 removida, fora do recorte.
  SHA-256 do CSV: `54b112bef22b4bfc8e9d0cf02b3119d93a5969b948c7b1b0e02c65c9a7c3ca7f`.
- **Origem registrada:** a URL do arquivo na Release (`--origem`), e não mais a da ANM.
- **Resultado:** aprovado, sem erros. 2.319.355 linhas lidas, 10.730 no recorte, 28 repetições integrais,
  669 células conciliadas, 868 observações sem referência (não publicadas). Mesmos números da manhã.
- **API local** (porta 8090) e **Docker** (porta 8091): `/saude` = `pronto`; Canaã dos Carajás 2025 =
  R$ 1.248.202.989,59 e Parauapebas 2025 = R$ 1.102.944.678,86, iguais à tabela oficial; Swagger,
  `/openapi.json` e CSV com HTTP 200; CORS liberado para a demo. No contêiner, UID 1000 e pacote montado
  só para leitura. As portas 8000, 8001 e 8080 estavam ocupadas por outro programa na máquina usada.
- **Conferências:** no backend, `ruff check`, `ruff format --check`, `mypy`, `lint-imports` e `pytest`
  (42 testes); no laboratório, `ruff check scripts` e `pytest` (61 testes).
- **Workflow `coletar-cfem.yml`:** não executado no GitHub, porque só roda a partir da branch padrão.
  Simulados localmente: a escolha da Release `anm-*`, a ida e volta do pacote anterior por `tar` (aprovado)
  e a saída 1 na reprovação.

## Situação das pendências do registro da manhã

| # | Pendência | Situação em 25/11/2026, tarde |
| ---: | --- | --- |
| 1 | Referência mensal dos oito anos | Sem mudança: evidência obtida, arquivo não ampliado |
| 2 | Controle nacional | Sem mudança: cobertura de dez anos |
| 3 | Ausências municipais | Sem mudança: sem canal com a ANM |
| 4 | Automação | **Parcial.** A coleta lê o `.csv.gz` da Release e há workflow diário que publica o pacote como Release `pacote-cfem-*` e abre issue na falha (ADR-011, ADR-015). Falta o coletor da tabela oficial de referência |
| 5 | Assistente | Sem mudança |
| 6 | Integração com o front | **Contrato pronto para envio:** Swagger descrito e `docs/api/openapi-producao.yaml`, conferido no CI. O envio depende do responsável pelo front |
| 7 | Docker e navegador | **Docker conferido.** A conferência visual da demo no navegador fica com o mantenedor |
| 8 | Edição do CSV | **Resolvida:** o relatório registra o SHA-256 e a Release de origem |
| 9 | TLS da ANM | Contornada: a coleta usa a Release; o GET direto com `OBS_ANM_CA` não foi testado |
| 10 | Pasta com dono root | **Mitigada:** o contêiner roda sem root e só lê; a coleta explica o erro de permissão; o guia manda criar a pasta antes do Docker |
| 11 | Duplicatas | **Parcial:** o manifesto não cita mais 129; o efeito em reais segue não medido |

Também nesta data: o texto de `limitacoes` da CFEM no manifesto foi atualizado, e a demo aceita o
endereço da API por `?api=`.
