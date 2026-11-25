# Back-end de produção

Projeto `uv` com o pacote `observatorio` em `src/` ([ADR-013](../docs/adr/ADR-013-organizacao-do-repositorio.md)). Separado do laboratório: não importa nada de `scripts/`.

| Pasta | O que vai nela | Situação |
| --- | --- | --- |
| `src/observatorio/config.py` | único lugar que lê variáveis de ambiente ([ADR-017](../docs/adr/ADR-017-padroes-de-codigo.md)) | pronto |
| `src/observatorio/modelo/` | esquema comum da observação, territórios e unidades (RN-MOD, RN-TER) | vazio (PB-03) |
| `src/observatorio/fontes/` | um módulo por fonte, com o contrato do ADR-017 e polars ([ADR-018](../docs/adr/ADR-018-biblioteca-de-processamento-de-dados.md)) | vazio |
| `src/observatorio/validacao/` | regras de qualidade e relatório de cada lote (RN-VPU) | vazio |
| `src/observatorio/publicacao/` | pacote imutável, trocado só quando o lote passa (RN-VPU-01, RN-VPU-03, ADR-014) | vazio |
| `src/observatorio/api/` | FastAPI em camadas: `controllers`, `services`, `repositories`, `dtos` (ADR-010, ADR-017) | Fase 1 |
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

A imagem não traz dados. O pacote publicado entra por volume, só leitura, a partir de `OBS_PUBLICADO_HOST` (padrão: `output/observatorio/publicado/`).

## O pacote publicado

A API lê só o pacote publicado (RN-ENT-01), da pasta `OBS_PUBLICADO_DIR`:

- `indicadores.json`: o manifesto de indicadores (RN-MOD-25), que vai dentro do pacote (ADR-014). Sem ele, as rotas de dimensão e de status respondem `503`.
- `populacao.json`: as observações de população homologadas.

Enquanto não houver gerador de pacote em `publicacao/`, o manifesto é copiado à mão da origem, `data/indicadores.json`, para a pasta publicada:

```bash
mkdir -p output/observatorio/publicado && cp data/indicadores.json output/observatorio/publicado/
```

## Rotas da Fase 1

`GET /api/v1/dimensoes/{social|economica|ambiental|institucional}`, o mesmo caminho com `.csv`, `GET /api/v1/indicadores/status` e `GET /saude`. Filtros: `municipio_id`, `ano_inicio`, `ano_fim`. O CSV inclui fonte, edição, método e limitações em cada linha. O manifesto descreve os sete indicadores conhecidos; os demais gráficos do site ainda não têm identificador e não recebem números desta API. Valores fictícios não entram na camada publicada.

A população só é exposta quando existe publicação válida no esquema comum. CFEM, commodities, despesa e indicadores sem pipeline aparecem como lacunas. A versão dos dados (`versao_dados`) é um hash do pacote inteiro lido na requisição (manifesto e observações), igual em todas as dimensões. O pacote é lido uma vez por requisição. O status (`/api/v1/indicadores/status`) lista todos os indicadores do manifesto, inclusive os que ainda não têm dimensão na API. `503` indica pacote publicado inválido, ilegível ou sem manifesto (ou manifesto sem um indicador da dimensão, ou sem `fonte`, `metodo` e `limitacoes`); `404`, dimensão desconhecida; `422`, filtro inválido. A ausência de `populacao.json` não é erro: a resposta traz `sem_dado_validado` e `dados: []`. O `/saude` responde `pronto` (manifesto e população válidos), `sem_publicacao` (manifesto válido, sem população) ou `publicacao_invalida`, com o motivo.

## Pipeline CFEM e demo (implementação inicial de 24/11/2026)

Da raiz, com o CSV real fora do Git:

```bash
uv run --project backend python -m observatorio.coleta cfem --arquivo tmp/CFEM_Arrecadacao.csv --referencias data/referencia-cfem-mensal-anm.json --referencias-nacionais data/referencia-cfem-nacional-anm.json --evidencias docs/registros/evidencias-anm-2026-11-23
uv run --project backend uvicorn observatorio.api.main:app
```

`OBS_DATA_DIR` escolhe onde gravar bruto e qualidade; `OBS_PUBLICADO_DIR`
escolhe o pacote. Os padrões são `output/observatorio` e
`output/observatorio/publicado`. `OBS_MANIFESTO` aponta para
`data/indicadores.json`. `OBS_ANM_CA` é opcional para cadeia TLS; sem
`--arquivo`, a CLI faz GET na ANM com User-Agent. `OBS_CORS_ORIGENS` aceita
origens separadas por vírgula e tem padrão vazio. Para servir a demo de outra
origem, configure a origem exata, por exemplo `http://127.0.0.1:8765`.

O pacote novo usa `pacote.json` como ponteiro para `versoes/<hash>/`, com
`cfem_arrecadada.parquet`, `indicadores.json`, `consumo_assistente.json` e
relatório de qualidade. A API mantém leitura da população JSON da Fase 1 e
oferece `periodicidade=mensal|anual` na dimensão econômica e no CSV. Valor
monetário é texto decimal no JSON; anual só é calculado com 12 meses validados.

O HTML `demo/grafico-cfem.html` é demonstração separada do front oficial.
Sirva a pasta localmente, abra o HTML e informe o endereço da API. Consulte
`docs/registros/pipeline-cfem-2026-11-24.md` para as lacunas, anos excluídos e
próximos passos. A CLI confere os SHA-256 das capturas Markdown indicados nas
referências e compara os totais nacionais dos anos selecionados com as tabelas
oficiais da ANM (RN-CFE-12). As capturas são extrações, não respostas HTTP
originais. A presença dos arquivos não dispensa revisar sua proveniência e
investigar as 15 divergências antes de uso operacional.
