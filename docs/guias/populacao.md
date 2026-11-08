# Pipeline de população estimada

Requer [uv](https://docs.astral.sh/uv/) (Python 3.12 ou mais novo). A fonte é o SIDRA, agregado 6579, variável 9324. A lista fixa dos 12 municípios está em `scripts/comum/municipios.py` e corresponde a `RN-TER-01`.

## Executar

```bash
uv run python -m scripts.populacao.atualizar
uv run python -m scripts.populacao.atualizar --ano 2025
uv run python -m scripts.servidor.servidor
uv run pytest scripts/testes/test_populacao.py
```

O primeiro comando descobre o ano mais recente no SIDRA. `--ano` permite recompor um ano já publicado, desde que exista `data/referencia-populacao-ANO.json`. `OBS_DATA_DIR` altera o diretório local de armazenamento; `PORT` altera a porta HTTP (padrão 3000).

Rotas: `/api/v1/populacao`, `/api/v1/populacao?municipio_id=1502152`, `/api/v1/populacao.csv`, `/api/v1/status` e `/status`. Sem lote homologado, as rotas de dados retornam HTTP 503. Nenhuma rota lê a camada bruta.

Cada execução grava um relatório em `output/observatorio/qualidade/`. Uma falha de contrato, cobertura, faixa, encolhimento ou reconciliação bloqueia a publicação e deixa a anterior disponível. Os arquivos em `output/` são locais e ignorados pelo Git.

## Homologação e limites

As referências de 2025 e 2026 vêm de tabelas independentes do IBGE, vinculadas nos arquivos JSON em `data/`. A comparação é exata por código e ano. Para publicar anos adicionais, registrar primeiro uma tabela independente da mesma edição.

Este é um protótipo local. O ADR-005 registra as decisões de engenharia pendentes de aprovação antes de hospedar a API. A coleta da CFEM arrecadada ainda depende de validar e aprovar este padrão, além da verificação da lacuna de Bom Jesus do Tocantins em 2025.

Resultados datados das execuções (População (SIDRA)) estão em [registros/verificacoes.md](../registros/verificacoes.md).
