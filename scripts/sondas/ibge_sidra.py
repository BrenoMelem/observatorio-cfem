"""Sonda: confere nome e estimativa de população de 2025 dos 12 municípios no IBGE (Localidades + SIDRA 6579/9324).

Script de teste/laboratório (não é o produto). Porte de probe_ibge_sidra.ps1. Confere a estimativa
publicada, não o Censo 2022. A verificação do certificado TLS permanece ligada.

Uso:
    uv run python -m scripts.sondas.ibge_sidra [--saida output/validacao-ibge-populacao-2025.json]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from scripts.comum.arquivos import escrever_json
from scripts.comum.municipios import MUNICIPIOS

SAIDA_PADRAO = Path("output/validacao-ibge-populacao-2025-2026-10-15.json")


def _linha(cliente: httpx.Client, codigo: str, esperado: str) -> dict:
    linha = {"ibge_code": codigo, "expected_name": esperado, "official_name": None, "locality_id_matches": False,
             "name_matches": False, "estimate_2025_persons": None, "series_id_matches": False, "error": None}
    try:
        localidade = cliente.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo}", timeout=45)
        localidade.raise_for_status()
        dados = localidade.json()
        linha["official_name"] = str(dados["nome"])
        linha["locality_id_matches"] = str(dados["id"]) == codigo
        linha["name_matches"] = linha["official_name"] == esperado
        serie = cliente.get(
            f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2025/variaveis/9324?localidades=N6[{codigo}]",
            timeout=60)
        serie.raise_for_status()
        observacao = serie.json()[0]["resultados"][0]["series"][0]
        linha["series_id_matches"] = str(observacao["localidade"]["id"]) == codigo
        valor = str(observacao["serie"]["2025"])
        if re.fullmatch(r"\d+", valor):
            linha["estimate_2025_persons"] = int(valor)
        else:
            linha["error"] = f"Non-numeric or absent SIDRA value: {valor}"
    except Exception as erro:  # noqa: BLE001
        linha["error"] = str(erro)
    return linha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args(argv)
    with httpx.Client() as cliente:
        linhas = [_linha(cliente, c, n) for c, n in MUNICIPIOS.items()]
    validas = sum(1 for r in linhas if r["locality_id_matches"] and r["name_matches"]
                  and r["series_id_matches"] and r["estimate_2025_persons"] is not None)
    escrever_json(args.saida, {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(), "source": "IBGE Localidades + API de Agregados/SIDRA",
        "aggregate": "6579", "variable": "9324", "variable_name": "População residente estimada", "unit": "Pessoas",
        "period": "2025", "expected_municipalities": len(MUNICIPIOS), "valid_rows": validas, "rows": linhas,
        "note": "This checks the published estimate, not Censo 2022 population. TLS certificate verification remained enabled."})
    print(f"{validas}/{len(MUNICIPIOS)} valid municipal observations; saved {args.saida}")
    if validas != len(MUNICIPIOS):
        for r in linhas:
            if r["error"] or not r["name_matches"] or not r["series_id_matches"]:
                print(r["ibge_code"], r["error"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
