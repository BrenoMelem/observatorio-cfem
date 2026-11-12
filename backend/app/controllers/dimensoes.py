"""Rotas de consulta da camada publicada por dimensão (Fase 1)."""
import csv
import io
import re

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.dtos.publicacao import RespostaDimensao
from app.repositories.publicacao import PublicacaoInvalida
from app.services.dimensoes import DIMENSOES, consultar, manifesto

router = APIRouter(prefix="/api/v1")


def _consultar(dimensao: str, municipio_id: str | None, ano_inicio: int | None, ano_fim: int | None):
    if dimensao not in DIMENSOES:
        raise HTTPException(404, "Dimensão desconhecida")
    if municipio_id is not None and re.fullmatch(r"\d{7}", municipio_id) is None:
        raise HTTPException(422, "municipio_id deve ter sete dígitos")
    if ano_inicio is not None and ano_fim is not None and ano_inicio > ano_fim:
        raise HTTPException(422, "ano_inicio maior que ano_fim")
    try:
        return consultar(dimensao, municipio_id, ano_inicio, ano_fim)
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro


@router.get("/dimensoes/{dimensao}.csv")
def dimensao_csv(dimensao: str, municipio_id: str | None = None,
                 ano_inicio: int | None = Query(None, ge=1900), ano_fim: int | None = Query(None, ge=1900)):
    resposta = _consultar(dimensao, municipio_id, ano_inicio, ano_fim)
    saida = io.StringIO()
    campos = ["indicador", "municipio_id", "municipio_nome", "nivel_territorial", "ano", "mes", "valor",
              "unidade", "natureza_valor", "estado_validacao", "fonte", "edicao_fonte", "atualizado_em",
              "versao_tratamento", "metodo", "limitacoes"]
    escritor = csv.DictWriter(saida, fieldnames=campos, delimiter=";")
    escritor.writeheader()
    for observacao in resposta.dados:
        linha = observacao.model_dump()
        meta = resposta.metadados[observacao.indicador]
        linha["metodo"], linha["limitacoes"] = meta.metodo, meta.limitacoes
        escritor.writerow(linha)
    return Response("\ufeff" + saida.getvalue(), media_type="text/csv; charset=utf-8")


@router.get("/dimensoes/{dimensao}", response_model=RespostaDimensao)
def dimensao(dimensao: str, municipio_id: str | None = None,
             ano_inicio: int | None = Query(None, ge=1900), ano_fim: int | None = Query(None, ge=1900)):
    return _consultar(dimensao, municipio_id, ano_inicio, ano_fim)


@router.get("/indicadores/status")
def indicadores_status():
    try:
        resposta = consultar("social")
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro
    por_id = {s.indicador: s for s in resposta.status}
    for nome in manifesto():
        if nome not in por_id:
            dimensao_nome = next((d for d, ids in DIMENSOES.items() if nome in ids), None)
            if dimensao_nome:
                s = consultar(dimensao_nome).status
                por_id[nome] = next(item for item in s if item.indicador == nome)
    return list(por_id.values())
