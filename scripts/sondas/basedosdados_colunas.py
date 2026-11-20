"""Sonda: lista as colunas de tabelas da Base dos Dados pelo catálogo público (GraphQL, sem credencial).

Script de teste/laboratório (não é o produto). Não lê nenhuma linha de dado, só nomes de colunas.
Usado em 19/11/2026 para comparar o Novo CAGED (`caged.microdados_movimentacao`) com a RAIS
(`rais.microdados_vinculos`) na decisão de RN-MOD-16 (fluxo e estoque).

Uso:
    uv run python -m scripts.sondas.basedosdados_colunas microdados_movimentacao microdados_vinculos
"""

from __future__ import annotations

import argparse
import sys

import httpx

API = "https://backend.basedosdados.org/graphql"
CONSULTA = """query($slug: String) { allTable(slug: $slug) { edges { node {
  slug dataset { slug } columns { edges { node { name } } } } } } }"""


def colunas(resposta: dict) -> list[tuple[str, str, list[str]]]:
    """Extrai (dataset, tabela, colunas) da resposta do GraphQL."""
    saida = []
    for aresta in resposta["data"]["allTable"]["edges"]:
        no = aresta["node"]
        saida.append((no["dataset"]["slug"], no["slug"], [c["node"]["name"] for c in no["columns"]["edges"]]))
    return saida


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("tabelas", nargs="+", help="slug da tabela (por exemplo microdados_movimentacao)")
    args = parser.parse_args(argv)
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for tabela in args.tabelas:
            resposta = cliente.post(API, json={"query": CONSULTA, "variables": {"slug": tabela}}, timeout=60)
            resposta.raise_for_status()
            for dataset, slug, nomes in colunas(resposta.json()):
                print(f"{dataset}.{slug}: {len(nomes)} colunas")
                print("  " + ", ".join(nomes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
