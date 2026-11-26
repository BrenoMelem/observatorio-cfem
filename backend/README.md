# Back-end de produção

Projeto `uv` com o pacote `observatorio` em `src/` ([ADR-013](../docs/adr/ADR-013-organizacao-do-repositorio.md)). Separado do laboratório: não importa nada de `scripts/`.

| Pasta | O que vai nela | Situação |
| --- | --- | --- |
| `src/observatorio/config.py` | único lugar que lê variáveis de ambiente ([ADR-017](../docs/adr/ADR-017-padroes-de-codigo.md)) | pronto |
| `src/observatorio/modelo/` | esquema comum da observação, lote, pacote e territórios (RN-MOD, RN-TER) | CFEM arrecadada; despesa por função (categoria opcional) |
| `src/observatorio/fontes/` | um módulo por fonte, com o contrato do ADR-017 e polars ([ADR-018](../docs/adr/ADR-018-biblioteca-de-processamento-de-dados.md)) | `cfem_arrecadacao.py`, `siconfi.py` |
| `src/observatorio/validacao/` | regras de qualidade e relatório de cada lote (RN-VPU) | `cfem.py`, `siconfi.py` |
| `src/observatorio/publicacao/` | pacote imutável, trocado só quando o lote passa (RN-VPU-01, RN-VPU-03, ADR-014) | `pacote.py` |
| `src/observatorio/coleta.py` | linha de comando que encadeia fonte, validação e publicação | CFEM, SICONFI |
| `src/observatorio/api/` | FastAPI em camadas: `controllers`, `services`, `repositories`, `dtos` (ADR-010, ADR-017) | Fase 1 e CFEM |
| `demo/` | `grafico-cfem.html`, demonstração separada do front oficial | |
| `tests/` | espelha as pastas do pacote | |

Regra de dependência (ADR-013): `modelo` não importa nenhum outro subpacote; `api` importa só `modelo`, `config` e a leitura do pacote publicado, nunca `fontes`, `validacao` ou `publicacao`.

## Rodar sem Docker

Da raiz do repositório (os caminhos padrão valem a partir dela):

```bash
uv sync --project backend
uv run --project backend uvicorn observatorio.api.main:app
uv run --project backend pytest backend
```

As conferências do CI (`.github/workflows/ci.yml`, ADR-012), rodadas de dentro de `backend/`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy              # --strict, em src e tests (ADR-017)
uv run lint-imports      # regra de dependência entre os subpacotes (ADR-013)
uv run pytest
```

O Python fica em 3.12 (`backend/.python-version`, ADR-008).

## Rodar com Docker

Ambiente provisório do [ADR-015](../docs/adr/ADR-015-hospedagem-provisoria-e-segredos.md): a API e o PostgreSQL do [ADR-016](../docs/adr/ADR-016-armazenamento-dos-dados-de-usuarios.md), que nenhum código usa ainda.

```bash
cp backend/.env.example .env      # na raiz; troque a senha do PostgreSQL
docker compose up --build         # API em http://localhost:8000
```

`OBS_API_PORTA` muda a porta do computador (padrão 8000) e `OBS_CORS_ORIGENS` libera a demo ou o front. O contêiner roda sem root (UID 1000) e só lê o pacote.

A imagem não traz dados. O pacote publicado entra por volume, só leitura, a partir de `OBS_PUBLICADO_HOST` (padrão: `output/observatorio/publicado/`).

## O pacote publicado

A API lê só o pacote publicado (RN-ENT-01), da pasta `OBS_PUBLICADO_DIR`. O pacote é montado por `publicacao/` ([ADR-014](../docs/adr/ADR-014-formato-do-pacote-publicado.md)):

- `pacote.json`: o ponteiro para a versão em vigor, com o SHA-256 de cada arquivo. É trocado por último, só quando o lote é aprovado.
- `versoes/<hash>/`: a versão imutável, com `indicadores.json` (manifesto, RN-MOD-25), um parquet por indicador publicado (`cfem_arrecadada.parquet`, `despesa_funcao_*.parquet`), um relatório de qualidade por fonte (`qualidade-cfem.json`, `qualidade-siconfi.json`) e `consumo_assistente.json`.
- Cada fonte publica o seu pacote parcial (só os indicadores dela, com a mesma estrutura) e `publicacao/montagem.py` junta o último parcial de cada fonte no pacote servido: `python -m observatorio.coleta montar --parcial PASTA [--parcial PASTA ...]`. No GitHub, quem faz isso é `publicar-pacote.yml` (decisão de 25/11/2026, ADR-011).
- `populacao.json`: as observações de população da Fase 1, ainda sem fonte em `fontes/`. Na primeira publicação, se existir na pasta, é copiado para dentro da versão.

## Rotas

`GET /api/v1/dimensoes/{social|economica|ambiental|institucional}`, o mesmo caminho com `.csv`, `GET /api/v1/indicadores/status` e `GET /saude`. Filtros: `municipio_id`, `ano_inicio`, `ano_fim` e `periodicidade` (`mensal` ou `anual`; o anual só soma anos com 12 meses validados). Valor monetário é texto decimal no JSON. O Swagger gerado pela aplicação fica em `/docs` e a especificação em `/openapi.json`; a cópia versionada para o front é [docs/api/openapi-producao.yaml](../docs/api/openapi-producao.yaml). O CSV inclui fonte, edição, método e limitações em cada linha. O manifesto descreve os sete indicadores conhecidos; os demais gráficos do site ainda não têm identificador e não recebem números desta API. Valores fictícios não entram na camada publicada.

A população, a CFEM arrecadada e a despesa por função só são expostas quando existe publicação válida no esquema comum. Commodities e indicadores sem pipeline aparecem como lacunas. A despesa por função usa os campos opcionais `categoria` e `categoria_nome` (RN-MOD-03, exceção de 25/11/2026), e as rotas por dimensão aceitam o filtro `categoria`; pacotes antigos, sem essas colunas, continuam válidos. A versão dos dados (`versao_dados`) é um hash do pacote inteiro lido na requisição (manifesto e observações), igual em todas as dimensões. O pacote é lido uma vez por requisição. O status (`/api/v1/indicadores/status`) lista todos os indicadores do manifesto, inclusive os que ainda não têm dimensão na API. `503` indica pacote publicado inválido, ilegível ou sem manifesto (ou manifesto sem um indicador da dimensão, ou sem `fonte`, `metodo` e `limitacoes`); `404`, dimensão desconhecida; `422`, filtro inválido. A ausência de `populacao.json` não é erro: a resposta traz `sem_dado_validado` e `dados: []`. O `/saude` responde `pronto` (manifesto e ao menos uma observação publicada válidos), `sem_publicacao` (manifesto válido, sem observação) ou `publicacao_invalida`, com o motivo.

## Da coleta à API

O passo a passo (obter o CSV da Release, coletar, subir a API, abrir o Swagger e a demo) e as variáveis de ambiente estão no guia [pipeline-cfem.md](../docs/guias/pipeline-cfem.md). Em resumo, da raiz:

```bash
uv run --project backend python -m observatorio.coleta cfem --arquivo tmp/CFEM_Arrecadacao.csv --referencias data/referencia-cfem-mensal-anm.json --referencias-nacionais data/referencia-cfem-nacional-anm.json --evidencias data/evidencias-anm
uv run --project backend uvicorn observatorio.api.main:app   # Swagger em http://127.0.0.1:8000/docs
```

A CLI confere o SHA-256 de cada captura indicada nas referências (o HTML original da página da ANM, guardado em `.html.gz`; as capturas antigas em Markdown continuam aceitas), reconcilia cada município/mês com a tabela oficial da ANM e compara os totais nacionais (RN-CFE-12). As referências são geradas por `scripts/cfem/referencias_anm.py` (ver o guia). Os resultados e as pendências de cada execução estão em [docs/registros/](../docs/registros/).

A despesa por função do SICONFI roda com `uv run --project backend python -m observatorio.coleta siconfi` (guia: [pipeline-siconfi.md](../docs/guias/pipeline-siconfi.md)).
