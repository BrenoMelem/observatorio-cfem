"""Coleta a DCA (Anexo I-E) do SICONFI para os 12 municípios e grava um lote tratado, sem homologar.

Script de teste/laboratório (não é o produto). Porte do protótipo em Node (despesa-siconfi.mjs).
A seleção final de contas e a reconciliação independente ainda dependem de decisão (RN-FNT-04,
RN-TMP-04, RN-VPU-07); nenhum lote é homologado aqui. Para o CSV simples por função, ver `dca_csv.py`.

Uso:
    uv run python -m scripts.financas.dca_lote [--ano 2025]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlencode

from scripts.comum.arquivos import (
    PASTA_PADRAO, Buscar, agora, buscar_http, escrever_json, escrever_json_atomico, escrever_texto,
    id_execucao, iso_utc, ler_json_ou_vazio,
)
from scripts.comum.municipios import MUNICIPIOS

ESTAGIOS = {
    "Despesas Empenhadas": "despesa_funcao_empenhada",
    "Despesas Liquidadas": "despesa_funcao_liquidada",
    "Despesas Pagas": "despesa_funcao_paga",
}


class ContratoSiconfiError(Exception):
    """A resposta do SICONFI mudou de forma."""


def _numero(valor) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def validar_pagina(payload, codigo: str, ano: int, deslocamento: int) -> list[dict]:
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list) \
            or not isinstance(payload.get("hasMore"), bool):
        raise ContratoSiconfiError("Paginação DCA alterada")
    limite = payload.get("limit")
    if payload["hasMore"] and (not payload["items"] or not isinstance(limite, int) or limite <= 0):
        raise ContratoSiconfiError("Paginação DCA inconsistente")
    for item in payload["items"]:
        if (_numero(item.get("exercicio")) != ano or str(item.get("cod_ibge")) != codigo
                or "Anexo I-E" not in str(item.get("anexo") or "")):
            raise ContratoSiconfiError(f"{codigo}: exercício, ente ou anexo divergente")
        valor = item.get("valor")
        if (not isinstance(item.get("conta"), str) or not isinstance(item.get("coluna"), str)
                or valor is None or valor == "" or _numero(valor) is None):
            raise ContratoSiconfiError(f"{codigo}: contrato de conta, coluna ou valor alterado")
    if deslocamento > 100_000:
        raise ContratoSiconfiError("Paginação DCA excedeu limite de segurança")
    return payload["items"]


def executar_despesa(pasta_dados: str | Path = PASTA_PADRAO, ano: int | None = None,
                     buscar: Buscar = buscar_http, agora_fn: Callable[[], datetime] = agora) -> dict:
    instante_dt = agora_fn()
    ano = ano if ano is not None else instante_dt.year - 1
    if not 2013 <= ano <= instante_dt.year:
        raise ValueError("Exercício inválido")
    pasta = Path(pasta_dados)
    pasta_rel, pasta_bruto, pasta_tratado = pasta / "qualidade", pasta / "bruto" / "siconfi", pasta / "tratado" / "siconfi"
    for p in (pasta_rel, pasta_bruto, pasta_tratado):
        p.mkdir(parents=True, exist_ok=True)
    instante = iso_utc(instante_dt)
    execucao = id_execucao(instante)
    relatorio = {
        "execucao": execucao, "atualizado_em": instante, "indicador": "despesa_por_funcao", "exercicio": ano,
        "situacao": "bloqueado", "linhas_lidas": 0, "municipios_presentes": [], "anos": [ano], "nulos": 0,
        "duplicatas": 0, "faixa_valores": None, "divergencia_fonte_primaria": "Reconciliação independente pendente",
        "pendencias": ["Seleção das contas e granularidade função/subfunção",
                       "Tratamento de retificações (RN-TMP-04)", "Reconciliação independente (RN-VPU-07)"],
        "erro": None,
    }
    try:
        todas: list[dict] = []
        for codigo in MUNICIPIOS:
            deslocamento = paginas = 0
            while True:
                params = urlencode({"an_exercicio": ano, "id_ente": codigo,
                                    "no_anexo": "Anexo I-E" if ano == 2013 else "DCA-Anexo I-E",
                                    "offset": deslocamento, "limit": 5000})
                status, corpo = buscar(f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca?{params}")
                if not 200 <= status < 300:
                    raise ContratoSiconfiError(f"{codigo}: HTTP {status}")
                escrever_texto(pasta_bruto / f"{execucao}-{codigo}-{paginas}.json", corpo)
                try:
                    payload = json.loads(corpo)
                except json.JSONDecodeError as erro:
                    raise ContratoSiconfiError(f"{codigo}: JSON inválido") from erro
                itens = validar_pagina(payload, codigo, ano, deslocamento)
                todas.extend(
                    {"indicador": ESTAGIOS[i["coluna"]], "municipio_id": codigo, "municipio_nome": MUNICIPIOS[codigo],
                     "exercicio": ano, "conta": i["conta"], "cod_conta": i.get("cod_conta"), "rotulo": i.get("rotulo"),
                     "coluna": i["coluna"], "valor": float(i["valor"]), "anexo": i.get("anexo")}
                    for i in itens if i["coluna"] in ESTAGIOS
                )
                relatorio["linhas_lidas"] += len(itens)
                deslocamento += len(itens)
                paginas += 1
                if not payload["hasMore"]:
                    break
                if paginas > 100:
                    raise ContratoSiconfiError(f"{codigo}: excesso de páginas")
            if all(any(t["municipio_id"] == codigo and t["indicador"] == ind for t in todas)
                   for ind in ESTAGIOS.values()):
                relatorio["municipios_presentes"].append(codigo)
        if len(relatorio["municipios_presentes"]) != 12:
            raise ContratoSiconfiError("DCA sem cobertura dos 12 municípios")
        chaves: set[tuple] = set()
        for linha in todas:
            chave = (linha["municipio_id"], linha["coluna"], linha["rotulo"], linha["conta"])
            if chave in chaves:
                relatorio["duplicatas"] += 1
            chaves.add(chave)
        if relatorio["duplicatas"] or relatorio["nulos"]:
            raise ContratoSiconfiError("Lote com duplicatas ou nulos")
        valores = [t["valor"] for t in todas]
        relatorio["faixa_valores"] = {"minimo": min(valores), "maximo": max(valores)}
        escrever_json_atomico(pasta_tratado / f"dca-{ano}.json", todas, execucao)
        return relatorio
    except Exception as erro:
        relatorio["erro"] = f"{type(erro).__name__}: {erro}"
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise
    finally:
        escrever_json(pasta_rel / f"{execucao}-despesa-siconfi.json", relatorio)


def ler_despesa_publicada(pasta_dados: str | Path) -> list[dict]:
    return ler_json_ou_vazio(Path(pasta_dados) / "publicado" / "despesa-siconfi.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ano", type=int, help="exercício (padrão: ano anterior)")
    args = parser.parse_args(argv)
    try:
        r = executar_despesa(ano=args.ano)
    except Exception as erro:  # noqa: BLE001
        print(getattr(erro, "relatorio", {}).get("erro") or str(erro), file=sys.stderr)
        return 1
    print(json.dumps({"situacao": r["situacao"], "exercicio": r["exercicio"], "execucao": r["execucao"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
