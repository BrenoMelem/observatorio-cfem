"""Lista, ano a ano, o código de conta da DCA para receitas e despesas da dimensão econômica.

Script de teste/laboratório (não é o produto). Responde à extensão das séries antes de 2022
(RN-ENT-12: receita corrente, cota-parte do ICMS e investimento; RN-CFE-24: receita de CFEM
declarada): mostra em que anos o código da conta muda e se o conceito continua o mesmo. Lê o CSV
gerado por `scripts.financas.dca_anexos` (sem rede).

Uso:
    uv run python -m scripts.financas.codigos_dca output/financas/dca_anexos.csv [--municipio 1505536]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

# Conceito -> (anexo, padrão do nome da conta, colunas aceitas)
CONCEITOS = {
    "receita_corrente": ("I-C", r"^1\.0\.0\.0\.00\.0+\.0+ - Receitas Correntes$", ("Receitas Realizadas", "Receitas Brutas Realizadas")),
    "cota_parte_icms": ("I-C", r"Cota-Parte do ICMS$", ("Receitas Realizadas", "Receitas Brutas Realizadas")),
    "receita_cfem": ("I-C", r"Compensação Financeira (pela Exploração )?de Recursos Minerais", ("Receitas Realizadas", "Receitas Brutas Realizadas")),
    "investimento_pago": ("I-D", r"^4\.4\.00\.00\.00(\.00)? - Investimentos$", ("Despesas Pagas",)),
}


def codigos_por_ano(linhas: Iterable[dict[str, str]], municipio: str) -> dict[str, dict[int, list[tuple[str, float]]]]:
    """Para cada conceito, os (código, valor) encontrados em cada exercício do município."""
    saida: dict[str, dict[int, list[tuple[str, float]]]] = {c: defaultdict(list) for c in CONCEITOS}
    for linha in linhas:
        if linha["cod_ibge"] != municipio:
            continue
        for conceito, (anexo, padrao, colunas) in CONCEITOS.items():
            if linha["anexo"] == anexo and linha["coluna"] in colunas and re.search(padrao, linha["conta"].strip()):
                saida[conceito][int(linha["exercicio"])].append((linha["cod_conta"], float(linha["valor"])))
    return saida


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("dca", type=Path)
    parser.add_argument("--municipio", default="1505536")
    args = parser.parse_args(argv)
    with args.dca.open(encoding="utf-8") as f:
        resultado = codigos_por_ano(csv.DictReader(f), args.municipio)
    for conceito, anos in resultado.items():
        print(conceito)
        for ano in sorted(anos):
            print(f"  {ano}: " + "; ".join(f"{c} = R$ {v / 1e6:,.1f} mi" for c, v in anos[ano]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
