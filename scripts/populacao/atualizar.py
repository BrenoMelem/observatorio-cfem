"""Coleta, valida e reconcilia a população estimada do IBGE (SIDRA 6579/9324) para os 12 municípios.

Script de teste/laboratório (não é o produto). Porte do protótipo em Node (populacao.mjs).

Uso:
    uv run python -m scripts.populacao.atualizar [--ano 2025]

Variável de ambiente: OBS_DATA_DIR (padrão output/observatorio).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from scripts.comum.arquivos import (
    PASTA_PADRAO, Buscar, agora, buscar_http, escrever_json, escrever_json_atomico, escrever_texto,
    id_execucao, iso_utc, ler_json_ou_vazio,
)
from scripts.comum.municipios import CAMPOS, MUNICIPIOS

INDICADOR = "populacao_estimada"
VERSAO = "1.0.0"
RAIZ = Path(__file__).resolve().parents[2]


class ContratoSidraError(Exception):
    """A resposta do SIDRA mudou de forma."""


class ValidacaoError(Exception):
    """O lote não passou na validação."""


def _contrato(ok: bool, mensagem: str) -> None:
    if not ok:
        raise ContratoSidraError(mensagem)


def _valida(ok: bool, mensagem: str) -> None:
    if not ok:
        raise ValidacaoError(mensagem)


def extrair_sidra(payload, codigo: str, ano_alvo: int | None = None) -> dict:
    _contrato(isinstance(payload, list) and len(payload) == 1, f"{codigo}: resposta deve conter uma variável")
    variavel = payload[0]
    _contrato(isinstance(variavel, dict) and str(variavel.get("id")) == "9324", f"{codigo}: variável SIDRA mudou")
    _contrato(variavel.get("unidade") == "Pessoas", f"{codigo}: unidade SIDRA mudou")
    resultados = variavel.get("resultados")
    _contrato(isinstance(resultados, list) and len(resultados) == 1, f"{codigo}: resultados SIDRA mudaram")
    resultado = resultados[0]
    _contrato(resultado.get("classificacoes") == [], f"{codigo}: classificação inesperada")
    series = resultado.get("series")
    _contrato(isinstance(series, list) and len(series) == 1, f"{codigo}: séries SIDRA mudaram")
    serie = series[0]
    localidade = serie.get("localidade")
    _contrato(isinstance(localidade, dict) and str(localidade.get("id")) == codigo,
              f"{codigo}: código do município diverge")
    _contrato(localidade.get("nome") == f"{MUNICIPIOS[codigo]} (PA)", f"{codigo}: nome do município diverge")
    _contrato((localidade.get("nivel") or {}).get("id") == "N6", f"{codigo}: nível territorial diverge")
    periodos = serie.get("serie")
    _contrato(isinstance(periodos, dict) and len(periodos) > 0, f"{codigo}: períodos ausentes")
    anos = list(periodos)
    _contrato(all(re.fullmatch(r"\d{4}", a) for a in anos), f"{codigo}: período SIDRA mudou")
    ano = ano_alvo if ano_alvo is not None else max(int(a) for a in anos)
    _contrato(str(ano) in anos, f"{codigo}: ano {ano} ausente no SIDRA")
    valor = periodos[str(ano)]
    _contrato(isinstance(valor, str) and re.fullmatch(r"\d+", valor) is not None,
              f"{codigo}: valor do ano {ano} inválido ou ausente")
    return {"ano": ano, "valor": int(valor), "linhas_lidas": len(anos)}


def validar_lote(observacoes: list[dict], anterior: list[dict] | None = None) -> bool:
    anterior = anterior or []
    _valida(len(observacoes) == 12, "Lote deve conter os 12 municípios")
    chaves: set[str] = set()
    for o in observacoes:
        _valida(o["municipio_id"] in MUNICIPIOS, f"Município fora do escopo: {o['municipio_id']}")
        _valida(o["municipio_nome"] == MUNICIPIOS[o["municipio_id"]], f"Nome divergente: {o['municipio_id']}")
        _valida(isinstance(o["valor"], int) and 1 <= o["valor"] <= 5_000_000,
                f"População fora da faixa plausível: {o['municipio_id']}")
        _valida(o["natureza_valor"] == "informado" and o["estado_validacao"] == "validado",
                f"Estado inválido: {o['municipio_id']}")
        _valida(o["municipio_id"] not in chaves, f"Município duplicado: {o['municipio_id']}")
        chaves.add(o["municipio_id"])
    _valida(len({o["ano"] for o in observacoes}) == 1, "Anos diferentes no lote")
    novos = {f"{o['ano']}:{o['municipio_id']}" for o in observacoes}
    mantidas = {f"{o['ano']}:{o['municipio_id']}" for o in anterior if o["ano"] != observacoes[0]["ano"]}
    _valida(len(novos) + len(mantidas) >= len(anterior), "Série encolheu em relação à publicação anterior")
    return True


def reconciliar(observacoes: list[dict], referencia: dict) -> list:
    ano_ref = (referencia or {}).get("ano")
    _valida((referencia or {}).get("fonte")
            == f"IBGE - Estimativas da População {ano_ref}, publicação independente do SIDRA",
            "Fonte de reconciliação não identificada")
    _valida(referencia["ano"] == observacoes[0]["ano"], "Referência independente não cobre o ano mais recente")
    valores = referencia.get("valores") or {}
    _valida(len(valores) == 12, "Referência independente incompleta")
    divergencias = [
        {"municipio_id": o["municipio_id"], "sidra": o["valor"], "referencia": valores.get(o["municipio_id"])}
        for o in observacoes if valores.get(o["municipio_id"]) != o["valor"]
    ]
    _valida(not divergencias, f"Reconciliação falhou: {json.dumps(divergencias)}")
    return divergencias


def ler_publicado(pasta_dados: str | Path) -> list[dict]:
    return ler_json_ou_vazio(Path(pasta_dados) / "publicado" / "populacao.json")


def csv_populacao(observacoes: list[dict]) -> str:
    from scripts.comum.arquivos import csv_observacoes

    return csv_observacoes(observacoes, CAMPOS)


def executar(pasta_dados: str | Path = PASTA_PADRAO, buscar: Buscar = buscar_http,
             caminho_referencia: str | Path | None = None, ano_alvo: int | None = None,
             agora_fn: Callable[[], datetime] = agora) -> dict:
    pasta = Path(pasta_dados)
    pasta_bruto, pasta_rel, pasta_pub = pasta / "bruto" / "sidra", pasta / "qualidade", pasta / "publicado"
    for p in (pasta_bruto, pasta_rel, pasta_pub):
        p.mkdir(parents=True, exist_ok=True)
    instante = iso_utc(agora_fn())
    exec_id = id_execucao(instante)
    relatorio = {"execucao": exec_id, "atualizado_em": instante, "indicador": INDICADOR, "situacao": "bloqueado",
                 "linhas_lidas": 0, "municipios_presentes": [], "anos": [], "nulos": 0, "duplicatas": 0,
                 "faixa_valores": None, "divergencia_fonte_primaria": None, "erro": None}
    try:
        anterior = ler_publicado(pasta)
        extraidos = []
        for codigo in MUNICIPIOS:
            url = ("https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/all/variaveis/9324"
                   f"?localidades=N6%5B{codigo}%5D")
            status, corpo = buscar(url)
            _contrato(200 <= status < 300, f"{codigo}: HTTP {status} do SIDRA")
            escrever_texto(pasta_bruto / f"{exec_id}-{codigo}.json", corpo)
            try:
                payload = json.loads(corpo)
            except json.JSONDecodeError as erro:
                raise ContratoSidraError(f"{codigo}: JSON inválido") from erro
            dado = extrair_sidra(payload, codigo, ano_alvo)
            extraidos.append({"codigo": codigo, **dado, "hash": hashlib.sha256(corpo.encode()).hexdigest()})
            relatorio["linhas_lidas"] += dado["linhas_lidas"]
        observacoes = [
            {"indicador": INDICADOR, "municipio_id": e["codigo"], "municipio_nome": MUNICIPIOS[e["codigo"]],
             "nivel_territorial": "município", "ano": e["ano"], "mes": None, "valor": e["valor"],
             "unidade": "pessoas", "natureza_valor": "informado", "estado_validacao": "validado",
             "fonte": "IBGE SIDRA, agregado 6579, variável 9324", "edicao_fonte": str(e["ano"]),
             "atualizado_em": instante, "versao_tratamento": VERSAO}
            for e in extraidos
        ]
        relatorio["municipios_presentes"] = [o["municipio_id"] for o in observacoes]
        relatorio["anos"] = sorted({o["ano"] for o in observacoes})
        valores = [o["valor"] for o in observacoes]
        relatorio["faixa_valores"] = {"minimo": min(valores), "maximo": max(valores)}
        validar_lote(observacoes, anterior)
        ref = Path(caminho_referencia) if caminho_referencia else (
            RAIZ / "data" / f"referencia-populacao-{observacoes[0]['ano']}.json")
        referencia = json.loads(ref.read_text(encoding="utf-8"))
        relatorio["divergencia_fonte_primaria"] = reconciliar(observacoes, referencia)
        mantidas = [o for o in anterior if o["ano"] != observacoes[0]["ano"]]
        publicado = sorted(mantidas + observacoes, key=lambda o: (o["ano"], o["municipio_id"]))
        escrever_json_atomico(pasta_pub / "populacao.json", publicado, exec_id)
        relatorio["situacao"] = "publicado"
        relatorio["hashes_brutos"] = [{"municipio_id": e["codigo"], "sha256": e["hash"]} for e in extraidos]
        return relatorio
    except Exception as erro:
        relatorio["erro"] = f"{type(erro).__name__}: {erro}"
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise
    finally:
        escrever_json(pasta_rel / f"{exec_id}.json", relatorio)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ano", type=int, help="ano de referência (padrão: o mais recente do SIDRA)")
    args = parser.parse_args(argv)
    if args.ano is not None and not 2000 <= args.ano <= 2100:
        parser.error("--ano exige um ano válido")
    try:
        r = executar(ano_alvo=args.ano)
    except Exception as erro:  # noqa: BLE001
        print(getattr(erro, "relatorio", {}).get("erro") or str(erro), file=sys.stderr)
        return 1
    print(json.dumps({"situacao": r["situacao"], "ano": r["anos"][0],
                      "municipios": len(r["municipios_presentes"]), "execucao": r["execucao"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
