"""Rotas de consulta da camada publicada por dimensão (Fase 1)."""

import csv
import io
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from observatorio.api.dtos.publicacao import RespostaDimensao, StatusIndicador
from observatorio.api.repositories.publicacao import PublicacaoInvalida
from observatorio.api.services.dimensoes import DIMENSOES, consultar, status_geral

router = APIRouter(prefix="/api/v1")


def _consultar(
    dimensao: str,
    municipio_id: str | None,
    ano_inicio: int | None,
    ano_fim: int | None,
    periodicidade: Literal["mensal", "anual"] = "mensal",
) -> RespostaDimensao:
    if dimensao not in DIMENSOES:
        raise HTTPException(404, "Dimensão desconhecida")
    if municipio_id is not None and re.fullmatch(r"\d{7}", municipio_id) is None:
        raise HTTPException(422, "municipio_id deve ter sete dígitos")
    if ano_inicio is not None and ano_fim is not None and ano_inicio > ano_fim:
        raise HTTPException(422, "ano_inicio maior que ano_fim")
    try:
        return consultar(dimensao, municipio_id, ano_inicio, ano_fim, periodicidade=periodicidade)
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro


@router.get("/dimensoes/{dimensao}.csv")
def dimensao_csv(
    dimensao: str,
    municipio_id: str | None = None,
    ano_inicio: int | None = Query(None, ge=1900),
    ano_fim: int | None = Query(None, ge=1900),
    periodicidade: Literal["mensal", "anual"] = "mensal",
) -> Response:
    resposta = _consultar(dimensao, municipio_id, ano_inicio, ano_fim, periodicidade)
    saida = io.StringIO()
    campos = [
        "indicador",
        "municipio_id",
        "municipio_nome",
        "nivel_territorial",
        "ano",
        "mes",
        "valor",
        "unidade",
        "natureza_valor",
        "estado_validacao",
        "fonte",
        "edicao_fonte",
        "atualizado_em",
        "versao_tratamento",
        "metodo",
        "limitacoes",
    ]
    escritor = csv.DictWriter(saida, fieldnames=campos, delimiter=";")
    escritor.writeheader()
    for observacao in resposta.dados:
        linha = observacao.model_dump()
        meta = resposta.metadados[observacao.indicador]
        linha["metodo"], linha["limitacoes"] = meta.metodo, meta.limitacoes
        escritor.writerow(
            {
                chave: "'" + valor
                if isinstance(valor, str) and valor.startswith(("=", "+", "-", "@"))
                else valor
                for chave, valor in linha.items()
            }
        )
    return Response("\ufeff" + saida.getvalue(), media_type="text/csv; charset=utf-8")


@router.get("/dimensoes/{dimensao}", response_model=RespostaDimensao)
def dimensao(
    dimensao: str,
    municipio_id: str | None = None,
    ano_inicio: int | None = Query(None, ge=1900),
    ano_fim: int | None = Query(None, ge=1900),
    periodicidade: Literal["mensal", "anual"] = "mensal",
) -> RespostaDimensao:
    return _consultar(dimensao, municipio_id, ano_inicio, ano_fim, periodicidade)


@router.get("/indicadores/status")
def indicadores_status() -> list[StatusIndicador]:
    try:
        return status_geral()
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro
