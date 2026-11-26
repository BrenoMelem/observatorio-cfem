"""Sonda: compara a despesa paga por função e subfunção da DCA (Anexo I-E) com a MSC de dezembro.

Script de teste/laboratório (não é o produto). Responde à pendência da referência independente da
despesa paga (RN-FNT-04, RN-VPU-07), que o RREO Anexo 2 não traz. A MSC orçamentária (matriz `MSCC`,
mês 12, saldo final, classe 6) é outra declaração do município ao SICONFI; a conta 6.2.2.1.3.04
(crédito empenhado liquidado pago) é a despesa paga (mapeamento conferido em 19/11/2026, RN-CFE-24).
A sonda soma a conta por função e por função+subfunção, sem a modalidade 91 (intraorçamentária), e
compara com o estágio pago da DCA, ao centavo. As linhas "FUxx - Demais Subfunções" da DCA não têm
código de subfunção; elas são comparadas com o que sobra da função na MSC depois das subfunções
listadas. Usa a API pública do SICONFI, sem chave.

Uso:
    uv run python -m scripts.sondas.siconfi_msc_dca_paga [--anos 2018-2024] [--saida output/sonda-msc-dca.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx

from scripts.comum.municipios import MUNICIPIOS

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
CONTA_PAGA = "622130400"
FUNCAO = re.compile(r"^(\d{2}) - ")
SUBFUNCAO = re.compile(r"^(\d{2})\.(\d{3}) - ")
DEMAIS = re.compile(r"^FU(\d{2}) - Demais Subfun")


def _todas(cliente: httpx.Client, rota: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    deslocamento = 0
    while True:
        resposta = cliente.get(f"{API}/{rota}", params={**params, "offset": deslocamento, "limit": 5000},
                               timeout=240)
        resposta.raise_for_status()
        corpo = resposta.json()
        itens.extend(corpo["items"])
        deslocamento += len(corpo["items"])
        if not corpo["hasMore"]:
            return itens


def _dec(valor: Any) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"))


def paga_dca(dca: list[dict[str, Any]]) -> dict[str, Decimal]:
    """Chaves: 'FF' (função), 'FF.SSS' (subfunção) e 'FF.demais'."""
    saida: dict[str, Decimal] = {}
    for item in dca:
        if item["coluna"] != "Despesas Pagas":
            continue
        conta = str(item["conta"])
        if m := SUBFUNCAO.match(conta):
            saida[f"{m[1]}.{m[2]}"] = _dec(item["valor"])
        elif m := FUNCAO.match(conta):
            saida[m[1]] = _dec(item["valor"])
        elif m := DEMAIS.match(conta):
            saida[f"{m[1]}.demais"] = _dec(item["valor"])
    return saida


def paga_msc(msc: list[dict[str, Any]], chaves_dca: set[str]) -> dict[str, Decimal]:
    por_funcao: dict[str, Decimal] = defaultdict(Decimal)
    por_sub: dict[str, Decimal] = defaultdict(Decimal)
    for item in msc:
        if item["conta_contabil"] != CONTA_PAGA or str(item.get("natureza_despesa") or "")[2:4] == "91":
            continue
        sinal = 1 if item["natureza_conta"] == "C" else -1
        valor = Decimal(str(item["valor"])) * sinal
        por_funcao[item["funcao"]] += valor
        por_sub[f"{item['funcao']}.{item['subfuncao']}"] += valor
    saida: dict[str, Decimal] = {k: v.quantize(Decimal("0.01")) for k, v in por_funcao.items()}
    for funcao, total in por_funcao.items():
        listadas = Decimal(0)
        for chave, valor in por_sub.items():
            if chave.startswith(f"{funcao}.") and chave in chaves_dca:
                saida[chave] = valor.quantize(Decimal("0.01"))
                listadas += valor
        if f"{funcao}.demais" in chaves_dca:
            saida[f"{funcao}.demais"] = (total - listadas).quantize(Decimal("0.01"))
    return saida


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--anos", default="2018-2024")
    parser.add_argument("--saida", default="output/sonda-msc-dca.json")
    args = parser.parse_args(argv)
    inicio, fim = (int(a) for a in args.anos.split("-"))
    registros: list[dict[str, Any]] = []
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for ano in range(inicio, fim + 1):
            for codigo, nome in MUNICIPIOS.items():
                dca = paga_dca(_todas(cliente, "dca", {"an_exercicio": ano, "id_ente": codigo,
                                                       "no_anexo": "Anexo I-E" if ano == 2013 else "DCA-Anexo I-E"}))
                msc_bruta = _todas(cliente, "msc_orcamentaria", {
                    "id_ente": codigo, "an_referencia": ano, "me_referencia": 12, "co_tipo_matriz": "MSCC",
                    "classe_conta": 6, "id_tv": "ending_balance"})
                msc = paga_msc(msc_bruta, set(dca))
                diferentes = {k: [str(dca[k]), str(msc.get(k))] for k in dca if msc.get(k) != dca[k]}
                registros.append({"ano": ano, "municipio_id": codigo, "municipio": nome, "linhas_dca": len(dca),
                                  "linhas_msc": len(msc_bruta), "diferentes": diferentes})
                situacao = "sem dados" if not dca or not msc_bruta else (
                    "ok" if not diferentes else f"DIF em {len(diferentes)} de {len(dca)}")
                print(f"{ano} {nome:26} dca={len(dca):3} msc={len(msc_bruta):5} {situacao}")
    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.saida).write_text(json.dumps(registros, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saída:", args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
