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
uv run --project backend ruff check backend
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
