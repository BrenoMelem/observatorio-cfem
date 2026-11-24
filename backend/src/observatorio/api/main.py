"""Aplicação FastAPI da camada publicada."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observatorio import config
from observatorio.api.controllers.dimensoes import router
from observatorio.api.repositories.publicacao import (
    PublicacaoInvalida,
)
from observatorio.api.services.dimensoes import ler_pacote

app = FastAPI(title="Observatório CFEM — camada publicada", version="0.1.0")
app.include_router(router)
if config.carregar().cors_origens:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.carregar().cors_origens),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


@app.get("/saude")
def saude() -> dict[str, str]:
    """Pronto só quando o manifesto e a população publicados podem ser lidos e validados."""
    try:
        estado = "pronto" if ler_pacote().populacao else "sem_publicacao"
    except PublicacaoInvalida as erro:
        return {"estado": "publicacao_invalida", "motivo": str(erro)}
    return {"estado": estado}
