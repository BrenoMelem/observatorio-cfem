"""Aplicação FastAPI da camada publicada; o OpenAPI gerado aqui é o contrato do front."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from observatorio import config
from observatorio.api.controllers.dimensoes import router
from observatorio.api.dtos.publicacao import Saude
from observatorio.api.repositories.publicacao import (
    PublicacaoInvalida,
)
from observatorio.api.services.dimensoes import ler_pacote

DESCRICAO = """
Dados públicos sobre a CFEM e indicadores dos 12 municípios da Região de Integração Carajás (PA).

A API lê **só o pacote publicado** (RN-ENT-01): um lote entra no pacote apenas depois de validado contra
publicação oficial independente, e um lote reprovado não substitui o anterior (RN-VPU-01, RN-VPU-03).

- **Ausência não é zero.** Município ou mês sem observação é lacuna (RN-CFE-07).
- **Dinheiro é texto decimal** (`"120784171.37"`), para não perder centavos (RN-CFE-11).
- **`versao_dados`** identifica o pacote publicado; serve para invalidar cache no front.
- Somente leitura, sem autenticação.
"""
TAGS = [
    {"name": "dimensoes", "description": "Observações por dimensão do observatório, em JSON ou CSV."},
    {"name": "indicadores", "description": "Situação de publicação de cada indicador."},
    {"name": "saude", "description": "Estado do pacote publicado."},
]

app = FastAPI(
    title="Observatório CFEM — camada publicada",
    version="0.1.0",
    description=DESCRICAO.strip(),
    openapi_tags=TAGS,
)
app.include_router(router)
if config.carregar().cors_origens:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.carregar().cors_origens),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


@app.get(
    "/saude",
    response_model=Saude,
    response_model_exclude_none=True,
    tags=["saude"],
    summary="Estado do pacote publicado",
)
def saude() -> Saude:
    """Pronto só com manifesto e ao menos uma observação publicada lidos e validados (RN-ENT-01)."""
    try:
        pacote = ler_pacote()
    except PublicacaoInvalida as erro:
        return Saude(estado="publicacao_invalida", motivo=str(erro))
    return Saude(estado="pronto" if pacote.populacao else "sem_publicacao")
