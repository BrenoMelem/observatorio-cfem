"""Sonda: lista o status das entregas da DCA no SICONFI (homologada ou retificada) para os 12 municípios.

Script de teste/laboratório (não é o produto). Responde a RN-TMP-04 (retificações do SICONFI): mostra
se a API expõe uma entrega por município e exercício (a vigente) ou várias versões. Usa o endpoint
público `extrato_entregas` (sem chave). Status observados: `HO` (homologada) e `RE` (retificada).

Uso:
    uv run python -m scripts.sondas.siconfi_entregas [--anos 2022-2024]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

import httpx

from scripts.comum.municipios import MUNICIPIOS

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/extrato_entregas"
DCA = "Balanço Anual (DCA)"


def entregas_dca(itens: list[dict]) -> list[dict]:
    """Só as entregas da DCA, com status e data do status."""
    return [{"status": i.get("status_relatorio"), "data_status": i.get("data_status"),
             "forma_envio": i.get("forma_envio")} for i in itens if i.get("entregavel") == DCA]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--anos", default="2022-2024")
    args = parser.parse_args(argv)
    inicio, fim = (int(a) for a in args.anos.split("-"))
    contagem: Counter = Counter()
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for codigo, nome in MUNICIPIOS.items():
            for ano in range(inicio, fim + 1):
                resposta = cliente.get(API, params={"id_ente": codigo, "an_referencia": ano}, timeout=60)
                resposta.raise_for_status()
                dca = entregas_dca(resposta.json()["items"])
                contagem[len(dca)] += 1
                for e in dca:
                    print(f"{nome:26} {ano} {e['status']} {e['data_status']}")
    print("entregas da DCA por município e exercício:", dict(contagem))
    return 0


if __name__ == "__main__":
    sys.exit(main())
