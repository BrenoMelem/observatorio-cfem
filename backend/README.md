# Back-end — Fase 1

API de leitura da camada publicada, separada dos scripts de laboratório. Lê somente `populacao.json` de `OBS_PUBLICADO_DIR`; por padrão, procura `output/observatorio/publicado/` na raiz. Não coleta dados nem cria publicação. O arquivo deve vir do pipeline homologado. Se não existir, a resposta traz `sem_dado_validado` e `dados: []`.

```powershell
uv sync --project backend
uv run --project backend uvicorn app.main:app --app-dir backend
uv run --project backend pytest
uv run --project backend ruff check backend/app backend/tests
```

Rotas: `GET /api/v1/dimensoes/{social|economica|ambiental|institucional}`, o mesmo caminho com `.csv`, `GET /api/v1/indicadores/status` e `GET /saude`. Filtros: `municipio_id`, `ano_inicio`, `ano_fim`. O CSV inclui fonte, edição, método e limitações em cada linha. O manifesto `data/indicadores.json` descreve os sete indicadores conhecidos; os demais gráficos do site ainda não têm identificador e não recebem números desta API. Valores fictícios não entram na camada publicada.

A população só é exposta quando existe publicação válida no esquema comum. CFEM, commodities, despesa e indicadores sem pipeline aparecem como lacunas. O selo de dado real das páginas estáticas não comprova homologação. A versão dos dados é um hash do conteúdo lido. `503` indica arquivo publicado inválido; `404`, dimensão desconhecida; `422`, filtro inválido. A ausência de arquivo não é erro operacional.
