"""Aplicação FastAPI da camada publicada."""
from fastapi import FastAPI

from observatorio.api.controllers.dimensoes import router
from observatorio.api.repositories.publicacao import pasta_publicada

app = FastAPI(title="Observatório CFEM — camada publicada", version="0.1.0")
app.include_router(router)


@app.get("/saude")
def saude():
    pasta = pasta_publicada()
    return {"estado": "pronto" if (pasta / "populacao.json").is_file() else "sem_publicacao",
            "pasta_publicada": str(pasta)}
