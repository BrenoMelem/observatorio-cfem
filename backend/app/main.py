"""Aplicação FastAPI da camada publicada."""
from fastapi import FastAPI

from app.controllers.dimensoes import router
from app.repositories.publicacao import PUBLICADO

app = FastAPI(title="Observatório CFEM — camada publicada", version="0.1.0")
app.include_router(router)


@app.get("/saude")
def saude():
    return {"estado": "pronto" if (PUBLICADO / "populacao.json").is_file() else "sem_publicacao",
            "pasta_publicada": str(PUBLICADO)}
