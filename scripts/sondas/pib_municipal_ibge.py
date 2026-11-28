"""Sonda: piloto do PIB municipal (SIDRA 5938) nos 12 municípios da RI Carajás, 2010 a 2023.

Script de teste/laboratório (não é o produto). Mede, com os valores do SIDRA (mil reais inteiros), quanto as
identidades contábeis diferem por arredondamento (soma dos setores = VAB; VAB + impostos = PIB), conta os
valores ausentes e negativos e, se receber a base de dados do IBGE em xlsx (FTP `Pib_Municipios`), compara
célula a célula. Base da exceção de RN-VPU-07 e RN-VPU-12 de 27/11/2026.

Uso:
    uv run python -m scripts.sondas.pib_municipal_ibge [--xlsx "PIB dos Municípios - base de dados 2010-2023.xlsx"]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import httpx

from scripts.comum.municipios import MUNICIPIOS

SIDRA = "https://servicodados.ibge.gov.br/api/v3/agregados/5938"
ANOS = range(2010, 2024)
VARIAVEIS = {"37": "pib", "543": "impostos", "498": "vab", "513": "agro", "517": "industria", "6575": "servicos",
             "525": "adm"}
COLUNAS_XLSX = {"agro": 32, "industria": 33, "servicos": 34, "adm": 35, "vab": 36, "impostos": 37, "pib": 38}
SETORES = ("agro", "industria", "servicos", "adm")

Chave = tuple[str, str, str]


def sidra() -> dict[Chave, str]:
    """Valor como texto, por (município, ano, variável), num só pedido com os 12 municípios (RN-FNT-19)."""
    saida: dict[Chave, str] = {}
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, timeout=120) as cliente:
        resposta = cliente.get(f"{SIDRA}/periodos/{'|'.join(map(str, ANOS))}/variaveis/{'|'.join(VARIAVEIS)}",
                               params={"localidades": f"N6[{','.join(MUNICIPIOS)}]"})
        resposta.raise_for_status()
        for variavel in resposta.json():
            for serie in variavel["resultados"][0]["series"]:
                for ano, valor in serie["serie"].items():
                    saida[(serie["localidade"]["id"], ano, VARIAVEIS[variavel["id"]])] = valor
    return saida


def identidades(api: dict[Chave, str]) -> tuple[Counter[Decimal], Counter[Decimal]]:
    """Diferenças (setores − VAB) e (VAB + impostos − PIB) nos anos com todos os componentes."""
    setores: Counter[Decimal] = Counter()
    pib: Counter[Decimal] = Counter()
    for municipio in MUNICIPIOS:
        for ano in map(str, ANOS):
            if any(api[(municipio, ano, v)] == "..." for v in VARIAVEIS.values()):
                continue
            valor = {v: Decimal(api[(municipio, ano, v)]) for v in VARIAVEIS.values()}
            setores[sum((valor[s] for s in SETORES), Decimal(0)) - valor["vab"]] += 1
            pib[valor["vab"] + valor["impostos"] - valor["pib"]] += 1
    return setores, pib


def comparar_xlsx(api: dict[Chave, str], caminho: Path) -> None:
    from openpyxl import load_workbook

    planilha = load_workbook(caminho, read_only=True).active
    referencia: dict[Chave, object] = {}
    for linha in planilha.iter_rows(min_row=2, values_only=True):
        if str(linha[6]) in MUNICIPIOS and int(linha[0]) in ANOS:
            for nome, coluna in COLUNAS_XLSX.items():
                referencia[(str(linha[6]), str(linha[0]), nome)] = linha[coluna]
    comparados, maior, fora = 0, Decimal(0), []
    for chave, valor in api.items():
        if valor == "...":
            continue
        comparados += 1
        diferenca = abs(Decimal(str(referencia[chave])) - Decimal(valor))
        maior = max(maior, diferenca)
        if diferenca > Decimal("0.5"):
            fora.append((chave, valor, referencia[chave]))
    print(f"xlsx: {comparados} valores comparados; {len(fora)} fora de 0,5 mil reais; maior diferença {maior}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--xlsx", type=Path)
    args = parser.parse_args(argv)
    api = sidra()
    print(f"valores do SIDRA: {len(api)} (esperado {len(MUNICIPIOS) * len(ANOS) * len(VARIAVEIS)})")
    ausentes = Counter((ano, v) for (_, ano, v), valor in api.items() if valor == "...")
    print("ausentes ('...') por (ano, variável):", sorted(ausentes.items()))
    print("negativos:", sorted((k, v) for k, v in api.items() if v.startswith("-")))
    setores, pib = identidades(api)
    print("setores − VAB:", sorted(setores.items()))
    print("VAB + impostos − PIB:", sorted(pib.items()))
    if args.xlsx:
        comparar_xlsx(api, args.xlsx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
