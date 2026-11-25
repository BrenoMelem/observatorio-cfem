"""Rotas de consulta da camada publicada por dimensão (Fase 1)."""

import csv
import io
import re
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import Response

from observatorio.api.dtos.publicacao import Erro, RespostaDimensao, StatusIndicador
from observatorio.api.repositories.publicacao import PublicacaoInvalida
from observatorio.api.services.dimensoes import DIMENSOES, consultar, status_geral

router = APIRouter(prefix="/api/v1")

# Descrições do OpenAPI. A validação continua em `_consultar`, para manter os 404 e 422 como estão.
DIMENSAO = Path(
    description="Dimensão do observatório (RN-ENT-12). A CFEM arrecadada fica na `economica`.",
    json_schema_extra={"enum": list(DIMENSOES)},
)
MUNICIPIO = Query(
    None,
    description="Código IBGE de 7 dígitos de um dos 12 municípios da RI Carajás. Omitido: todos.",
    examples=["1505536"],
)
ANO_INICIO = Query(None, ge=1900, description="Primeiro ano do recorte, inclusive.", examples=[2015])
ANO_FIM = Query(None, ge=1900, description="Último ano do recorte, inclusive.", examples=[2025])
PERIODICIDADE = Query(
    "mensal",
    description=(
        "`mensal`: uma observação por mês. `anual`: soma da CFEM só nos anos com os 12 meses validados; "
        "os anos omitidos aparecem em `notas` (RN-CFE-05)."
    ),
)
CATEGORIA = Query(
    None,
    description=(
        "Código da categoria dentro do indicador (RN-MOD-03): na despesa por função, `12` (função), `12.361` "
        "(subfunção), `12.demais` (Demais Subfunções) ou `total`. Omitido: todas as categorias."
    ),
    examples=["12"],
)
ERROS: dict[int | str, dict[str, object]] = {
    404: {"model": Erro, "description": "Dimensão desconhecida."},
    503: {"model": Erro, "description": "Pacote publicado inválido, ilegível ou sem manifesto (RN-VPU-03)."},
}
EXEMPLO_CSV = (
    "indicador;municipio_id;municipio_nome;nivel_territorial;ano;mes;valor;unidade;natureza_valor;"
    "estado_validacao;fonte;edicao_fonte;atualizado_em;versao_tratamento;categoria;categoria_nome;metodo;"
    "limitacoes\n"
    "cfem_arrecadada;1505536;Parauapebas;município;2025;1;120784171.37;BRL nominal;informado;validado;"
    "ANM, CFEM_Arrecadacao.csv;54b112be…;2026-11-25T11:44:04+00:00;1.0.0;;;…;…\n"
)


def _consultar(
    dimensao: str,
    municipio_id: str | None,
    ano_inicio: int | None,
    ano_fim: int | None,
    periodicidade: Literal["mensal", "anual"] = "mensal",
    categoria: str | None = None,
) -> RespostaDimensao:
    if dimensao not in DIMENSOES:
        raise HTTPException(404, "Dimensão desconhecida")
    if municipio_id is not None and re.fullmatch(r"\d{7}", municipio_id) is None:
        raise HTTPException(422, "municipio_id deve ter sete dígitos")
    if ano_inicio is not None and ano_fim is not None and ano_inicio > ano_fim:
        raise HTTPException(422, "ano_inicio maior que ano_fim")
    try:
        return consultar(
            dimensao, municipio_id, ano_inicio, ano_fim, periodicidade=periodicidade, categoria=categoria
        )
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro


@router.get(
    "/dimensoes/{dimensao}.csv",
    tags=["dimensoes"],
    summary="Observações de uma dimensão em CSV",
    response_class=Response,
    responses={
        200: {
            "description": (
                "CSV em UTF-8 com BOM, separado por ponto e vírgula. Cada linha traz fonte, edição, método e "
                "limitações (RN-ENT-05). Texto que começa com `=`, `+`, `-` ou `@` ganha um apóstrofo."
            ),
            "content": {"text/csv": {"schema": {"type": "string"}, "example": EXEMPLO_CSV}},
        },
        **ERROS,
    },
)
def dimensao_csv(
    dimensao: str = DIMENSAO,
    municipio_id: str | None = MUNICIPIO,
    ano_inicio: int | None = ANO_INICIO,
    ano_fim: int | None = ANO_FIM,
    periodicidade: Literal["mensal", "anual"] = PERIODICIDADE,
    categoria: str | None = CATEGORIA,
) -> Response:
    """Os mesmos filtros e observações da rota JSON, para download (RN-ENT-03)."""
    resposta = _consultar(dimensao, municipio_id, ano_inicio, ano_fim, periodicidade, categoria)
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
        "categoria",
        "categoria_nome",
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
    return Response("﻿" + saida.getvalue(), media_type="text/csv; charset=utf-8")


@router.get(
    "/dimensoes/{dimensao}",
    response_model=RespostaDimensao,
    tags=["dimensoes"],
    summary="Observações conferidas de uma dimensão",
    responses=ERROS,
)
def dimensao(
    dimensao: str = DIMENSAO,
    municipio_id: str | None = MUNICIPIO,
    ano_inicio: int | None = ANO_INICIO,
    ano_fim: int | None = ANO_FIM,
    periodicidade: Literal["mensal", "anual"] = PERIODICIDADE,
    categoria: str | None = CATEGORIA,
) -> RespostaDimensao:
    """Devolve só observações conferidas do pacote publicado (RN-ENT-01, RN-VPU-10).

    No ano ainda aberto, os meses conferidos saem com `estado_validacao` = `provisório` (RN-CFE-06).

    Indicador sem publicação aparece em `status` com o motivo, sem observação inventada; temas ainda sem
    indicador aparecem em `lacunas`. Filtro inválido (`municipio_id` sem 7 dígitos, `ano_inicio` maior que
    `ano_fim`) responde 422.
    """
    return _consultar(dimensao, municipio_id, ano_inicio, ano_fim, periodicidade, categoria)


@router.get(
    "/indicadores/status",
    tags=["indicadores"],
    summary="Situação de todos os indicadores do manifesto",
    responses={503: ERROS[503]},
)
def indicadores_status() -> list[StatusIndicador]:
    """Lista cada indicador do manifesto, publicado ou não, com o motivo da ausência (RN-ENT-04)."""
    try:
        return status_geral()
    except PublicacaoInvalida as erro:
        raise HTTPException(503, detail=str(erro)) from erro
