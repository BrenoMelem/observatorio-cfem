"""Conta, para os 12 municípios, os meses com linha na arrecadação e na distribuição da CFEM, por ano.

Script de teste/laboratório (não é o produto). Ajuda a responder RN-CFE-23 (meses sem linha de
Bom Jesus do Tocantins): mostra se a falta de linha é um buraco do arquivo ou um padrão de
arrecadação esporádica, comparando a arrecadação (mês M) com a distribuição (repasse, em geral
no mês seguinte). Lê os arquivos `.csv.gz` arquivados nas Releases `anm-*` (RN-TMP-18), baixados
antes para uma pasta local; nenhum CPF/CNPJ é lido para a saída.

Uso:
    gh release download anm-AAAA-MM-DD-HHMM --pattern 'arrecadacao.csv.gz' --pattern 'distribuicao.csv.gz' --dir tmp/anm
    uv run python -m scripts.cfem.meses_por_municipio tmp/anm [--desde 2022] [--saida output/cfem-meses.json]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import sys
from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from scripts.comum.arquivos import escrever_json
from scripts.comum.municipios import MUNICIPIOS

ARQUIVOS = {"arrecadacao": ("arrecadacao.csv.gz", "CodigoMunicipio"),
            "distribuicao": ("distribuicao.csv.gz", "CodigoEnte")}


def meses_por_ano(linhas: Iterable[dict[str, str]], campo_codigo: str, desde: int) -> dict[str, dict[int, list[int]]]:
    """Para cada um dos 12 municípios, os meses (ordenados) com ao menos uma linha, por ano."""
    meses: dict[str, dict[int, set[int]]] = {c: defaultdict(set) for c in MUNICIPIOS}
    for linha in linhas:
        codigo = linha.get(campo_codigo, "")
        if codigo in meses and int(linha["Ano"]) >= desde:
            meses[codigo][int(linha["Ano"])].add(int(linha["Mês"]))
    return {c: {a: sorted(m) for a, m in sorted(anos.items())} for c, anos in meses.items()}


def _ler(caminho: Path) -> Iterable[dict[str, str]]:
    with gzip.open(caminho) as bruto:
        yield from csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pasta", type=Path, help="pasta com arrecadacao.csv.gz e distribuicao.csv.gz")
    parser.add_argument("--desde", type=int, default=2022)
    parser.add_argument("--saida", type=Path, default=Path("output/cfem-meses-por-municipio.json"))
    args = parser.parse_args(argv)
    resultado = {nome: meses_por_ano(_ler(args.pasta / arquivo), campo, args.desde)
                 for nome, (arquivo, campo) in ARQUIVOS.items()}
    escrever_json(args.saida, {"checked_at_utc": datetime.now(UTC).isoformat(), "pasta": str(args.pasta),
                               "desde": args.desde, "meses": resultado})
    anos = sorted({a for r in resultado.values() for m in r.values() for a in m})
    print(f"{'municipio':26} " + " ".join(f"{a}(arr/dist)" for a in anos))
    for codigo, nome in MUNICIPIOS.items():
        celulas = [f"{len(resultado['arrecadacao'][codigo].get(a, [])):>5}/{len(resultado['distribuicao'][codigo].get(a, [])):<5}"
                   for a in anos]
        print(f"{nome:26} " + " ".join(f"{c:>11}" for c in celulas))
    print(f"salvo em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
