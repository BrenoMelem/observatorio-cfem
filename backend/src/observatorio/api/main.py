"""Aplicação FastAPI da camada publicada."""

from fastapi import FastAPI

from observatorio.api.controllers.dimensoes import router
from observatorio.api.repositories.publicacao import (
    PublicacaoInvalida,
    manifesto_publicado,
    pasta_publicada,
    populacao_publicada,
)

app = FastAPI(title="Observatório CFEM — camada publicada", version="0.1.0")
app.include_router(router)


@app.get("/saude")
def saude() -> dict[str, str]:
    """Pronto só quando o manifesto e a população publicados podem ser lidos e validados."""
    pasta = pasta_publicada()
    try:
        manifesto_publicado(pasta)
        estado = "pronto" if populacao_publicada(pasta) else "sem_publicacao"
    except PublicacaoInvalida as erro:
        return {"estado": "publicacao_invalida", "motivo": str(erro)}
    return {"estado": estado}
