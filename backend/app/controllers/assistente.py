"""Endpoint do assistente com limite de entrada e controle local de taxa."""
import os
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.dtos.assistente import Pergunta, Resposta
from app.llm.redator import redator
from app.repositories.publicacao import PublicacaoInvalida
from app.services.assistente import responder

router = APIRouter(prefix="/api/v1")
JANELAS: dict[str, deque[float]] = defaultdict(deque)


@router.post("/assistente", response_model=Resposta)
async def assistente(request: Request):
    if int(request.headers.get("content-length", "0")) > 8_192:
        raise HTTPException(413, "Entrada excede 8 KiB")
    corpo = await request.body()
    if len(corpo) > 8_192:
        raise HTTPException(413, "Entrada excede 8 KiB")
    chave = request.client.host if request.client else "desconhecido"
    agora = time.monotonic()
    janela = JANELAS[chave]
    while janela and agora - janela[0] >= 60:
        janela.popleft()
    if len(janela) >= int(os.getenv("OBS_ASSISTENTE_LIMITE_MINUTO", "20")):
        raise HTTPException(429, "Limite de consultas por minuto")
    janela.append(agora)
    try:
        entrada = Pergunta.model_validate_json(corpo)
        if any(len(h) > 500 for h in entrada.historico):
            raise HTTPException(422, "Histórico muito longo")
        return responder(entrada, redator())
    except ValidationError as erro:
        raise HTTPException(422, detail=erro.errors(include_context=False)) from erro
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro
    except RuntimeError as erro:
        raise HTTPException(503, detail=str(erro)) from erro
