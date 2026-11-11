"""Compara duas versões do mesmo arquivo da ANM: linhas que sumiram, apareceram e o efeito no recorte.

Script de teste/laboratório (não é o produto). A comparação é por linha inteira: uma linha alterada conta
como uma removida e uma adicionada. O relatório traz só contagens e somas por ano e município; nunca grava
linhas brutas nem CPF/CNPJ.

Uso:
    uv run python -m scripts.cfem.comparar_versoes_anm FONTE ANTIGO.csv NOVO.csv [RELATORIO.json]
FONTE: arrecadacao, distribuicao ou autuacao.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from scripts.cfem.anm_arquivos import FONTES, decodificar, indices, interpretar, ler_cabecalho, separar
from scripts.comum.arquivos import escrever_json


def _linhas(arquivo: Path):
    with open(arquivo, "rb") as f:
        f.readline()  # cabeçalho
        yield from f


def _agregar(linhas: list[bytes], fonte: str, idx: dict[str, int]) -> dict:
    por_ano: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"linhas": 0, "valor": Decimal(0)}))
    for bruto in linhas:
        try:
            achado = interpretar(separar(decodificar(bruto), fonte), idx, fonte)
        except csv.Error:  # linha que não é CSV válido sozinha (ex.: quebra de linha dentro de aspas)
            continue
        if achado:
            ano, nome, valor = achado
            resumo = por_ano[str(ano)][nome]
            resumo["linhas"] += 1
            resumo["valor"] += valor
    return {a: {m: {"linhas": r["linhas"], "valor": f"{r['valor']:.2f}"} for m, r in sorted(ms.items())}
            for a, ms in sorted(por_ano.items())}


def comparar(fonte: str, antigo: str | Path, novo: str | Path) -> dict:
    antigo, novo = Path(antigo), Path(novo)
    cab_antigo, cab_novo = ler_cabecalho(antigo, fonte), ler_cabecalho(novo, fonte)
    restante: Counter[int] = Counter()
    total_antigo = 0
    for linha in _linhas(antigo):
        restante[hash(linha)] += 1
        total_antigo += 1
    adicionadas, total_novo = [], 0
    for linha in _linhas(novo):
        total_novo += 1
        h = hash(linha)
        if restante[h] > 0:
            restante[h] -= 1
        else:
            adicionadas.append(linha)
    removidas = []
    for linha in _linhas(antigo):
        h = hash(linha)
        if restante[h] > 0:
            restante[h] -= 1
            removidas.append(linha)
    idx = indices(cab_novo, fonte)
    return {
        "fonte": fonte, "linhas_antigo": total_antigo, "linhas_novo": total_novo,
        "adicionadas": len(adicionadas), "removidas": len(removidas),
        "cabecalho_alterado": cab_antigo != cab_novo,
        "recorte_adicionadas": _agregar(adicionadas, fonte, idx),
        "recorte_removidas": _agregar(removidas, fonte, idx),
    }


def texto_markdown(relatorio: dict) -> str:
    r = relatorio
    saida = [f"### {r['fonte']}", "",
             f"- Linhas: {r['linhas_antigo']} → {r['linhas_novo']} (adicionadas {r['adicionadas']}, removidas {r['removidas']})."]
    if r["cabecalho_alterado"]:
        saida.append("- **O cabeçalho (colunas) mudou.**")
    for rotulo, chave in (("Adicionadas", "recorte_adicionadas"), ("Removidas", "recorte_removidas")):
        if r[chave]:
            saida += ["", f"{rotulo} no recorte dos 12 municípios:", "", "| Ano | Município | Linhas | Valor (R$) |", "| --- | --- | ---: | ---: |"]
            saida += [f"| {a} | {m} | {v['linhas']} | {v['valor']} |" for a, ms in r[chave].items() for m, v in ms.items()]
    return "\n".join(saida) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("fonte", choices=sorted(FONTES))
    parser.add_argument("antigo")
    parser.add_argument("novo")
    parser.add_argument("relatorio", nargs="?")
    args = parser.parse_args(argv)
    r = comparar(args.fonte, args.antigo, args.novo)
    if args.relatorio:
        escrever_json(Path(args.relatorio), r)
    print(texto_markdown(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
