# Imagem só da API (ADR-015): sem dados dentro; o pacote publicado entra por volume.
FROM ghcr.io/astral-sh/uv:0.13.7 AS uv

FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    OBS_PUBLICADO_DIR=/dados/publicado PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# Dependências primeiro, para aproveitar o cache entre builds; sem o grupo dev nem o extra "coleta".
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 1000 observatorio
USER observatorio
EXPOSE 8000
CMD ["uvicorn", "observatorio.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
