"""Coleta as séries de preço de ferro e cobre do FRED e publica uma camada provisória.

Script de teste/laboratório (não é o produto). Porte do protótipo em Node (commodities-fred.mjs).
Preserva os meses ausentes (valor ".") como `ausente` e não corta a série (divergência 17).

Uso:
    FRED_API_KEY=... uv run python -m scripts.commodities.fred

A chave entra só por variável de ambiente e nunca é gravada (sai como [REDACTED] nos relatórios).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlencode

from scripts.comum.arquivos import (
    PASTA_PADRAO, Buscar, agora, buscar_http, csv_observacoes, escrever_json, escrever_json_atomico,
    escrever_texto, id_execucao, iso_utc, ler_json_ou_vazio,
)
from scripts.comum.municipios import CAMPOS

SERIES = {
    "PIORECRUSDM": {"indicador": "preco_minerio_ferro", "unidade": "USD/dmt"},
    "PCOPPUSDM": {"indicador": "preco_cobre", "unidade": "USD/t"},
}


class ContratoFredError(Exception):
    """A resposta do FRED mudou de forma."""


def extrair_fred(meta: dict, corpo: dict, serie: str, instante: str) -> list[dict]:
    config = SERIES.get(serie)
    series_meta = (meta or {}).get("seriess")
    if (not config or not isinstance(series_meta, list) or len(series_meta) != 1
            or series_meta[0].get("id") != serie or series_meta[0].get("frequency_short") != "M"
            or series_meta[0].get("units") != "U.S. Dollars per Metric Ton"):
        raise ContratoFredError(f"{serie}: metadados inesperados")
    observacoes = (corpo or {}).get("observations")
    if (not isinstance(observacoes, list) or not observacoes
            or int(corpo.get("count") or -1) != len(observacoes)):
        raise ContratoFredError(f"{serie}: observações incompletas ou paginação inesperada")
    chaves: set[str] = set()
    linhas: list[dict] = []
    for item in observacoes:
        data, texto = item.get("date"), item.get("value")
        if not isinstance(data, str) or not re.fullmatch(r"\d{4}-\d{2}-01", data) or not isinstance(texto, str):
            raise ContratoFredError(f"{serie}: data ou valor inválido")
        ano, mes = int(data[:4]), int(data[5:7])
        if not 1 <= mes <= 12 or data in chaves:
            raise ContratoFredError(f"{serie}: mês inválido ou duplicado")
        chaves.add(data)
        try:
            valor = None if texto == "." else float(texto)
        except ValueError as erro:
            raise ContratoFredError(f"{serie}: preço inválido") from erro
        if valor is not None and (not math.isfinite(valor) or valor < 0):
            raise ContratoFredError(f"{serie}: preço inválido")
        linhas.append({
            "indicador": config["indicador"], "municipio_id": None, "municipio_nome": None,
            "nivel_territorial": "global", "ano": ano, "mes": mes, "valor": valor, "unidade": config["unidade"],
            "natureza_valor": "ausente" if valor is None else "zero real" if valor == 0 else "informado",
            "estado_validacao": "provisório", "fonte": f"FRED, série {serie} (IMF)",
            "edicao_fonte": series_meta[0].get("last_updated"), "atualizado_em": instante,
            "versao_tratamento": "1.0.0",
        })
    linhas.sort(key=lambda r: (r["ano"], r["mes"]))
    for anterior, atual in zip(linhas, linhas[1:]):
        if atual["ano"] * 12 + atual["mes"] != anterior["ano"] * 12 + anterior["mes"] + 1:
            raise ContratoFredError(f"{serie}: lacuna na sequência mensal")
    return linhas


def executar_commodities(pasta_dados: str | Path = PASTA_PADRAO, chave_api: str | None = None,
                         buscar: Buscar = buscar_http,
                         agora_fn: Callable[[], datetime] = agora) -> dict:
    chave_api = chave_api if chave_api is not None else os.environ.get("FRED_API_KEY")
    if not chave_api or not re.fullmatch(r"[a-z0-9]{32}", chave_api):
        raise ValueError("FRED_API_KEY ausente ou inválida")
    pasta = Path(pasta_dados)
    pasta_rel, pasta_bruto, pasta_pub = pasta / "qualidade", pasta / "bruto" / "fred", pasta / "publicado"
    for p in (pasta_rel, pasta_bruto, pasta_pub):
        p.mkdir(parents=True, exist_ok=True)
    instante = iso_utc(agora_fn())
    execucao = id_execucao(instante)
    relatorio = {
        "execucao": execucao, "atualizado_em": instante, "indicador": "commodities", "situacao": "bloqueado",
        "linhas_lidas": 0, "municipios_presentes": [], "anos": [], "nulos": 0, "duplicatas": 0,
        "faixa_valores": {}, "divergencia_fonte_primaria": "Reconciliação independente pendente; valores provisórios",
        "pendencia_ferro": "Divergência 17: início em 1980 ou 1992 e recorte de exibição em aberto; nenhuma linha foi cortada.",
        "erro": None,
    }
    try:
        todos: list[dict] = []
        for serie in SERIES:
            def obter(endpoint: str, rotulo: str) -> dict:
                url = f"https://api.stlouisfed.org/fred/series{endpoint}?" + urlencode(
                    {"series_id": serie, "api_key": chave_api, "file_type": "json"})
                status, corpo = buscar(url)
                if not 200 <= status < 300:
                    raise ContratoFredError(f"{serie}: HTTP {status}")
                escrever_texto(pasta_bruto / f"{execucao}-{serie}-{rotulo}.json", corpo)
                try:
                    return json.loads(corpo)
                except json.JSONDecodeError as erro:
                    raise ContratoFredError(f"{serie}: JSON inválido") from erro

            meta, observacoes = obter("", "meta"), obter("/observations", "observations")
            linhas = extrair_fred(meta, observacoes, serie, instante)
            todos.extend(linhas)
            relatorio["linhas_lidas"] += len(linhas)
            relatorio["nulos"] += sum(1 for r in linhas if r["valor"] is None)
            valores = [r["valor"] for r in linhas if r["valor"] is not None]
            relatorio["faixa_valores"][serie] = {"minimo": min(valores), "maximo": max(valores)} if valores else None
            if not valores:
                raise ContratoFredError(f"{serie}: série sem valores")
        relatorio["anos"] = sorted({r["ano"] for r in todos})
        escrever_json_atomico(pasta_pub / "commodities.json", todos, execucao)
        relatorio["situacao"] = "publicado_provisorio"
        return relatorio
    except Exception as erro:
        relatorio["erro"] = f"{type(erro).__name__}: {str(erro).replace(chave_api, '[REDACTED]')}"
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise
    finally:
        escrever_json(pasta_rel / f"{execucao}-commodities.json", relatorio)


def ler_commodities_publicadas(pasta_dados: str | Path) -> list[dict]:
    return ler_json_ou_vazio(Path(pasta_dados) / "publicado" / "commodities.json")


def csv_commodities(linhas: list[dict]) -> str:
    return csv_observacoes(linhas, CAMPOS)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args(argv)
    try:
        r = executar_commodities()
    except Exception as erro:  # noqa: BLE001
        print(getattr(erro, "relatorio", {}).get("erro") or str(erro), file=sys.stderr)
        return 1
    print(json.dumps({"situacao": r["situacao"], "linhas": r["linhas_lidas"], "execucao": r["execucao"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
