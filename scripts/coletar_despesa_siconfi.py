"""Collect municipal expenditure by function (SICONFI, DCA Anexo I-E) for the Carajas RI.

Test script, not production code. It queries the public SICONFI API (no login, no key)
once per municipality and year and writes a CSV with one row per (stage, account).
Only public aggregates are fetched. The CSV is written outside the repo by default.

Usage:
    python scripts/coletar_despesa_siconfi.py --inicio 2022 --fim 2026 --saida despesa.csv
"""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
ANEXO = "DCA-Anexo I-E"

# Codigos IBGE dos 12 municipios da RI Carajas (docs/regras-de-negocio/territorio.md).
MUNICIPIOS = {
    "Bom Jesus do Tocantins": 1501576,
    "Brejo Grande do Araguaia": 1501758,
    "Canaã dos Carajás": 1502152,
    "Curionópolis": 1502772,
    "Eldorado do Carajás": 1502954,
    "Marabá": 1504208,
    "Palestina do Pará": 1505494,
    "Parauapebas": 1505536,
    "Piçarra": 1505635,
    "São Domingos do Araguaia": 1507151,
    "São Geraldo do Araguaia": 1507458,
    "São João do Araguaia": 1507508,
}


def consultar(exercicio, id_ente):
    """Return the API response for one municipality and year."""
    params = urllib.parse.urlencode(
        {"an_exercicio": exercicio, "no_anexo": ANEXO, "id_ente": id_ente}
    )
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inicio", type=int, default=2022)
    ap.add_argument("--fim", type=int, default=2026)
    ap.add_argument("--saida", default="despesa_funcao_ri_carajas.csv")
    args = ap.parse_args()

    linhas, resumo = [], []
    for nome, codigo in MUNICIPIOS.items():
        for ano in range(args.inicio, args.fim + 1):
            try:
                dados = consultar(ano, codigo)
            except OSError as erro:
                resumo.append((nome, ano, "erro", str(erro)[:60]))
                continue
            itens = dados["items"]
            resumo.append((nome, ano, len(itens), dados["hasMore"]))
            for r in itens:
                linhas.append(
                    (nome, codigo, ano, r["coluna"], r["conta"], r["valor"], r["populacao"])
                )
            time.sleep(0.3)

    with open(args.saida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["municipio", "cod_ibge", "exercicio", "estagio", "conta", "valor", "populacao"])
        w.writerows(linhas)

    print(f"{len(linhas)} linhas gravadas em {args.saida}")
    for nome, ano, qtd, mais in resumo:
        marca = "SEM DADOS" if qtd in (0, "erro") else ""
        print(f"{nome:28} {ano}  linhas={qtd}  hasMore={mais}  {marca}")


if __name__ == "__main__":
    main()
