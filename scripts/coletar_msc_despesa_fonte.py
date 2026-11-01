"""Collect expenditure by function and resource source (MSC, SICONFI) for the Carajas RI.

Test script, not production code. The DCA (see coletar_despesa_siconfi.py) has no field for
the origin of the money. The MSC (Matriz de Saldos Contabeis, orcamentaria, class 6) does:
every expenditure line carries `fonte_recursos`, `funcao` and `subfuncao`. Source 708 is
"Transferencia da Uniao referente a Compensacao Financeira de Recursos Minerais" (Portaria
STN 710/2021, Anexo I); in the MSC it shows as 1708, where the leading digit is the group
(1 = recursos do exercicio corrente) and the other three are the source.

The script queries the public SICONFI API (no login, no key), one call per municipality and
month, keeps only the lines that have a function, and sums them by account, nature (D or C),
source and function. D and C are kept apart because the sign of each account was not
mapped, and the accounts are NOT mapped to the stages (empenhada, liquidada, paga):
`conta_contabil` and `natureza_conta` are written as is. The CSV goes outside the repo
by default. Each municipality is written as soon as it finishes, and a rerun skips the
municipalities already in the output file.

Usage:
    python scripts/coletar_msc_despesa_fonte.py --inicio 2023 --fim 2026 --saida msc.csv
    python scripts/coletar_msc_despesa_fonte.py --inicio 2026 --fim 2026 --municipio 1502152
"""

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from collections import defaultdict

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/msc_orcamentaria"

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


def consultar(id_ente, ano, mes, tipo_matriz):
    """Return all lines of the movement (period_change) of class 6 for one municipality and month.

    The API returns at most `limit` lines per page (5000); the following pages are read with
    `offset` until `hasMore` is false.
    """
    itens, offset = [], 0
    while True:
        params = urllib.parse.urlencode(
            {
                "id_ente": id_ente,
                "an_referencia": ano,
                "me_referencia": mes,
                "co_tipo_matriz": tipo_matriz,
                "classe_conta": 6,
                "id_tv": "period_change",
                "offset": offset,
            }
        )
        req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            pagina = json.load(resp)
        itens.extend(pagina["items"])
        if not pagina["hasMore"]:
            return {"items": itens, "hasMore": False}
        offset += pagina["limit"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inicio", type=int, default=2023)
    ap.add_argument("--fim", type=int, default=2026)
    ap.add_argument("--municipio", type=int, help="codigo IBGE; omitido = os 12 municipios")
    ap.add_argument("--tipo-matriz", default="MSCC", choices=["MSCC", "MSCE"])
    ap.add_argument("--saida", default="msc_despesa_fonte_ri_carajas.csv")
    args = ap.parse_args()

    alvos = {n: c for n, c in MUNICIPIOS.items() if args.municipio in (None, c)}
    if not alvos:
        ap.error(f"codigo {args.municipio} nao esta entre os 12 municipios da RI")

    colunas = [
        "municipio", "cod_ibge", "ano", "mes", "conta_contabil", "natureza_conta",
        "ano_fonte_recursos", "fonte_recursos", "funcao", "subfuncao", "valor",
    ]
    # Retomada: municipios ja gravados na saida sao pulados.
    feitos = set()
    existe = os.path.exists(args.saida)
    if existe:
        with open(args.saida, newline="", encoding="utf-8") as f:
            feitos = {int(r["cod_ibge"]) for r in csv.DictReader(f)}

    for nome, codigo in alvos.items():
        if codigo in feitos:
            print(f"{nome}: ja gravado, pulando", flush=True)
            continue
        soma = defaultdict(float)
        for ano in range(args.inicio, args.fim + 1):
            meses_com_dado = 0
            for mes in range(1, 13):
                dados = None
                for _tentativa in range(3):
                    try:
                        dados = consultar(codigo, ano, mes, args.tipo_matriz)
                        break
                    except OSError as erro:
                        time.sleep(5)
                if dados is None:
                    print(f"{nome} {ano}-{mes:02d}: ERRO apos 3 tentativas ({erro})", flush=True)
                    continue
                itens = dados["items"]
                if not itens:
                    continue
                meses_com_dado += 1
                for r in itens:
                    if not r["funcao"]:
                        continue
                    chave = (
                        nome, codigo, ano, mes, r["conta_contabil"], r["natureza_conta"],
                        r["ano_fonte_recursos"], r["fonte_recursos"], r["funcao"], r["subfuncao"],
                    )
                    soma[chave] += r["valor"]
                time.sleep(0.3)
            print(f"{nome} {ano}: meses com dado = {meses_com_dado}", flush=True)

        # Grava o municipio inteiro de uma vez, para a retomada nao ver municipio pela metade.
        with open(args.saida, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(colunas)
                existe = True
            for chave, valor in sorted(soma.items()):
                w.writerow([*chave, round(valor, 2)])
        print(f"{nome}: {len(soma)} linhas gravadas em {args.saida}", flush=True)

    print("concluido", flush=True)


if __name__ == "__main__":
    main()
