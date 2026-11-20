"""Confere se a fonte de recursos 1708 (CFEM) da MSC orçamentária serve para medir a despesa paga com CFEM.

Script de teste/laboratório (não é o produto). Ajuda a responder RN-CFE-24. Faz três conferências,
por município e ano, sobre arquivos já baixados (nada de rede):

1. Mapeamento de estágios: soma o movimento (crédito menos débito) das contas de controle da execução
   da despesa da MSC (classe 6, PCASP) por estágio e compara com o "Total Geral da Despesa" da DCA,
   Anexo I-D, nas colunas empenhada, liquidada e paga. Mapeamento testado (hipótese, conferida aqui):
   empenhada = 6.2.2.1.3.01 a .07; liquidada = .03, .04 e .07; paga = .04.
2. Despesa por fonte: o mesmo, só nas linhas com fonte de recursos 1708 ou 2708.
3. Escala: compara a despesa paga com fonte 1708/2708 com a CFEM distribuída pela ANM ao município no
   mesmo ano (arquivo de distribuição arquivado, RN-TMP-18) e com a receita de CFEM que o próprio
   município declara na DCA, Anexo I-C (contas "Cota-parte da CFEM" de transferência da União e dos
   Estados, com os códigos de cada período, receitas brutas realizadas). O arquivo da ANM só traz a
   parcela de município produtor.

Entradas:
  - CSV da MSC gerado por `scripts.financas.msc_despesa_fonte` (fora do repositório);
  - CSV da DCA gerado por `scripts.financas.dca_anexos` (output/financas/dca_anexos.csv);
  - `distribuicao.csv.gz` de uma Release `anm-*`.

Uso:
    uv run python -m scripts.financas.conferir_fonte_cfem tmp/msc_ri_2022_2026.csv \
        output/financas/dca_anexos.csv tmp/anm-2026-11-19/distribuicao.csv.gz [--saida output/fonte-cfem.json]
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
from decimal import Decimal
from pathlib import Path

from scripts.comum.arquivos import escrever_json
from scripts.comum.municipios import MUNICIPIOS

ESTAGIOS = {
    "empenhada": ("622130100", "622130200", "622130300", "622130400", "622130500", "622130600", "622130700"),
    "liquidada": ("622130300", "622130400", "622130700"),
    "paga": ("622130400",),
}
COLUNA_DCA = {"empenhada": "Despesas Empenhadas", "liquidada": "Despesas Liquidadas", "paga": "Despesas Pagas"}
FONTES_CFEM = ("1708", "2708")
CONTAS_RECEITA_CFEM = ("RO1.7.1.2.51.0.0", "RO1.7.2.2.51.0.0", "RO1.7.1.8.02.2.0", "RO1.7.2.8.02.2.0", "RO1.7.2.1.22.20.00")


def estagios_msc(linhas: Iterable[dict[str, str]]) -> dict[tuple[str, int, str], dict[str, Decimal]]:
    """Soma (crédito − débito) por município, ano, recorte ('total' ou 'cfem') e estágio."""
    somas: dict[tuple[str, int, str], dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    for linha in linhas:
        valor = Decimal(linha["valor"]) * (1 if linha["natureza_conta"] == "C" else -1)
        chave_total = (linha["cod_ibge"], int(linha["ano"]), "total")
        recortes = [chave_total]
        if linha["fonte_recursos"] in FONTES_CFEM:
            recortes.append((linha["cod_ibge"], int(linha["ano"]), "cfem"))
        for estagio, contas in ESTAGIOS.items():
            if linha["conta_contabil"] in contas:
                for chave in recortes:
                    somas[chave][estagio] += valor
    return somas


def totais_dca(linhas: Iterable[dict[str, str]]) -> dict[tuple[str, int], dict[str, Decimal]]:
    """Total Geral da Despesa do Anexo I-D por município, ano e estágio."""
    totais: dict[tuple[str, int], dict[str, Decimal]] = defaultdict(dict)
    colunas = {v: k for k, v in COLUNA_DCA.items()}
    for linha in linhas:
        if linha["anexo"] == "I-D" and linha["cod_conta"] == "TotalDespesas" and linha["coluna"] in colunas:
            totais[(linha["cod_ibge"], int(linha["exercicio"]))][colunas[linha["coluna"]]] = Decimal(linha["valor"])
    return totais


def receita_cfem_dca(linhas: Iterable[dict[str, str]]) -> dict[tuple[str, int], Decimal]:
    """Receita bruta realizada da cota-parte da CFEM declarada na DCA (Anexo I-C), por município e ano."""
    somas: dict[tuple[str, int], Decimal] = defaultdict(Decimal)
    for linha in linhas:
        if (linha["anexo"] == "I-C" and linha["cod_conta"] in CONTAS_RECEITA_CFEM
                and linha["coluna"] in ("Receitas Brutas Realizadas", "Receitas Realizadas")):
            somas[(linha["cod_ibge"], int(linha["exercicio"]))] += Decimal(linha["valor"])
    return dict(somas)


def cfem_distribuida(linhas: Iterable[dict[str, str]]) -> dict[tuple[str, int], Decimal]:
    """CFEM distribuída pela ANM a cada um dos 12 municípios, por ano (todas as modalidades)."""
    somas: dict[tuple[str, int], Decimal] = defaultdict(Decimal)
    for linha in linhas:
        if linha["CodigoEnte"] in MUNICIPIOS and linha["Ente"] == "Município":
            somas[(linha["CodigoEnte"], int(linha["Ano"]))] += Decimal(linha["Valor"].replace(",", "."))
    return somas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("msc", type=Path)
    parser.add_argument("dca", type=Path)
    parser.add_argument("distribuicao", type=Path)
    parser.add_argument("--anos", default="2022-2025")
    parser.add_argument("--saida", type=Path, default=Path("output/fonte-cfem.json"))
    args = parser.parse_args(argv)
    inicio, fim = (int(a) for a in args.anos.split("-"))
    with args.msc.open(encoding="utf-8") as f:
        msc = estagios_msc(csv.DictReader(f))
    with args.dca.open(encoding="utf-8") as f:
        dca = totais_dca(csv.DictReader(f))
    with args.dca.open(encoding="utf-8") as f:
        receita = receita_cfem_dca(csv.DictReader(f))
    with gzip.open(args.distribuicao) as bruto:
        anm = cfem_distribuida(csv.DictReader(io.TextIOWrapper(bruto, encoding="latin-1")))
    linhas = []
    for codigo, nome in MUNICIPIOS.items():
        for ano in range(inicio, fim + 1):
            total = msc.get((codigo, ano, "total"), {})
            cfem = msc.get((codigo, ano, "cfem"), {})
            ref = dca.get((codigo, ano), {})
            linhas.append({
                "municipio": nome, "cod_ibge": codigo, "ano": ano,
                **{f"msc_{e}": str(total.get(e, Decimal(0))) for e in ESTAGIOS},
                **{f"dca_{e}": str(ref[e]) if e in ref else None for e in ESTAGIOS},
                **{f"cfem_{e}": str(cfem.get(e, Decimal(0))) for e in ESTAGIOS},
                "anm_distribuida": str(anm.get((codigo, ano), Decimal(0))),
                "dca_receita_cfem": str(receita[(codigo, ano)]) if (codigo, ano) in receita else None,
            })
    escrever_json(args.saida, {"checked_at_utc": datetime.now(UTC).isoformat(), "msc": str(args.msc),
                               "dca": str(args.dca), "distribuicao": str(args.distribuicao), "linhas": linhas})
    print(f"{'municipio':26} {'ano':4} {'paga MSC/DCA':>13} {'empenh MSC/DCA':>15} {'pago 1708 (mi)':>15} "
          f"{'ANM (mi)':>9} {'rec DCA (mi)':>12} {'DCA/ANM':>8} {'1708/rec':>8}")
    for r in linhas:
        def razao(a, b):
            return f"{Decimal(a) / Decimal(b):.4f}" if b and Decimal(b) else "-"
        print(f"{r['municipio']:26} {r['ano']:4} {razao(r['msc_paga'], r['dca_paga']):>13} "
              f"{razao(r['msc_empenhada'], r['dca_empenhada']):>15} {Decimal(r['cfem_paga']) / 1_000_000:>15.2f} "
              f"{Decimal(r['anm_distribuida']) / 1_000_000:>9.2f} "
              f"{(Decimal(r['dca_receita_cfem']) / 1_000_000 if r['dca_receita_cfem'] else Decimal(0)):>12.2f} "
              f"{razao(r['dca_receita_cfem'] or 0, r['anm_distribuida']):>8} {razao(r['cfem_paga'], r['dca_receita_cfem'] or 0):>8}")
    print(f"salvo em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
