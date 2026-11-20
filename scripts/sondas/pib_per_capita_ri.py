"""Sonda: calcula o PIB per capita da RI Carajás pelos dois jeitos e compara com o número da FAPESPA.

Script de teste/laboratório (não é o produto). Responde a RN-MOD-18 (razão regional): soma dos PIBs
÷ soma das populações dos 12 municípios × média dos 12 PIBs per capita. A FAPESPA publica
R$ 147.782 para a RI Carajás em 2021 (Relatório PIB dos Municípios Paraenses 2021); o jeito que
reproduzir esse número é o usado oficialmente. Dados do SIDRA: tabela 5938 (PIB dos Municípios,
variável 37, mil reais) e tabela 6579 (estimativa da população, variável 9324).

Uso:
    uv run python -m scripts.sondas.pib_per_capita_ri [--ano 2021]
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal

import httpx

from scripts.comum.municipios import MUNICIPIOS

SIDRA = "https://servicodados.ibge.gov.br/api/v3/agregados"
FAPESPA_2021 = Decimal(147782)


def per_capita_ri(pib_mil: dict[str, Decimal], populacao: dict[str, Decimal]) -> tuple[Decimal, Decimal]:
    """Devolve (soma sobre soma, média das razões), em reais por habitante."""
    soma = sum(pib_mil.values()) * 1000 / sum(populacao.values())
    media = sum(pib_mil[c] * 1000 / populacao[c] for c in pib_mil) / len(pib_mil)
    return soma, media


def _serie(cliente: httpx.Client, tabela: str, variavel: str, ano: int) -> dict[str, Decimal]:
    url = f"{SIDRA}/{tabela}/periodos/{ano}/variaveis/{variavel}"
    resposta = cliente.get(url, params={"localidades": f"N6[{','.join(MUNICIPIOS)}]"}, timeout=90)
    resposta.raise_for_status()
    return {s["localidade"]["id"]: Decimal(s["serie"][str(ano)]) for s in resposta.json()[0]["resultados"][0]["series"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ano", type=int, default=2021)
    args = parser.parse_args(argv)
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        pib = _serie(cliente, "5938", "37", args.ano)
        pop = _serie(cliente, "6579", "9324", args.ano)
    soma, media = per_capita_ri(pib, pop)
    print(f"{len(pib)} municípios com PIB e {len(pop)} com população em {args.ano}")
    print(f"soma sobre soma: R$ {soma:,.0f}")
    print(f"média das razões: R$ {media:,.0f}")
    if args.ano == 2021:
        print(f"FAPESPA 2021: R$ {FAPESPA_2021:,.0f} (diferença da soma sobre soma: {(soma / FAPESPA_2021 - 1) * 100:.3f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
