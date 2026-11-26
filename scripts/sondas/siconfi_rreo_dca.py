"""Sonda: compara a despesa por função da DCA (Anexo I-E) com o RREO Anexo 2 do 6º bimestre.

Script de teste/laboratório (não é o produto). Responde à pendência da referência independente da
despesa por função (RN-FNT-04, RN-VPU-07): o RREO é outro demonstrativo que o município entrega ao
SICONFI e que traz a despesa empenhada e a liquidada até o bimestre por função e subfunção. A sonda
compara, por município e exercício, o total "exceto intraorçamentárias" e o conjunto dos valores das
linhas (funções, subfunções e "Demais Subfunções"), ao centavo. O RREO não tem a coluna de despesa
paga; para ela, a sonda só informa que não há comparação. Usa a API pública do SICONFI, sem chave.

Uso:
    uv run python -m scripts.sondas.siconfi_rreo_dca [--anos 2015-2024] [--saida output/sonda-rreo-dca.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx

from scripts.comum.municipios import MUNICIPIOS

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
# Coluna da DCA -> prefixo da coluna do RREO Anexo 2 (6º bimestre, acumulado no ano).
PARES = {
    "Despesas Empenhadas": "DESPESAS EMPENHADAS AT",
    "Despesas Liquidadas": "DESPESAS LIQUIDADAS AT",
    "Inscrição de Restos a Pagar Não Processados": "INSCRITAS EM RESTOS A PAGAR N",
}


def _centavos(valor: Any) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"))


def _todas(cliente: httpx.Client, rota: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    deslocamento = 0
    while True:
        resposta = cliente.get(f"{API}/{rota}", params={**params, "offset": deslocamento, "limit": 5000},
                               timeout=120)
        resposta.raise_for_status()
        corpo = resposta.json()
        itens.extend(corpo["items"])
        deslocamento += len(corpo["items"])
        if not corpo["hasMore"]:
            return itens


def _e_total(conta: str) -> bool:
    texto = conta.upper().replace("-", "").replace(" ", "")
    return texto.startswith(("DESPESAS(EXCETOINTRA", "DESPESASEXCETOINTRA"))


def comparar(dca: list[dict[str, Any]], rreo: list[dict[str, Any]]) -> dict[str, Any]:
    """Compara, por estágio, o total e o conjunto de valores das linhas da DCA e do RREO."""
    resultado: dict[str, Any] = {}
    for coluna_dca, prefixo in PARES.items():
        linhas_dca = [i for i in dca if i["coluna"] == coluna_dca]
        linhas_rreo = [i for i in rreo if str(i["coluna"]).upper().startswith(prefixo)
                       and "TOTAL (III)" not in str(i["conta"]).upper()
                       and "INTRA" not in str(i.get("rotulo", "")).upper().replace("EXCETO INTRA", "")]
        if not linhas_dca and not linhas_rreo:
            continue
        total_dca = [_centavos(i["valor"]) for i in linhas_dca if _e_total(i["conta"])]
        total_rreo = [_centavos(i["valor"]) for i in linhas_rreo if _e_total(i["conta"])]
        valores_dca = Counter(_centavos(i["valor"]) for i in linhas_dca if not _e_total(i["conta"]))
        valores_rreo = Counter(_centavos(i["valor"]) for i in linhas_rreo if not _e_total(i["conta"]))
        so_dca = valores_dca - valores_rreo
        so_rreo = valores_rreo - valores_dca
        resultado[coluna_dca] = {
            "total_dca": str(total_dca[0]) if total_dca else None,
            "total_rreo": str(total_rreo[0]) if total_rreo else None,
            "linhas_dca": sum(valores_dca.values()),
            "linhas_rreo": sum(valores_rreo.values()),
            "valores_so_na_dca": sorted(str(v) for v in so_dca.elements())[:10],
            "valores_so_no_rreo": sorted(str(v) for v in so_rreo.elements())[:10],
            "coincide": bool(total_dca) and total_dca == total_rreo and not so_dca and not so_rreo,
        }
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--anos", default="2015-2024")
    parser.add_argument("--saida", default="output/sonda-rreo-dca.json")
    args = parser.parse_args(argv)
    inicio, fim = (int(a) for a in args.anos.split("-"))
    registros: list[dict[str, Any]] = []
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for ano in range(inicio, fim + 1):
            for codigo, nome in MUNICIPIOS.items():
                anexo_dca = "Anexo I-E" if ano == 2013 else "DCA-Anexo I-E"
                dca = _todas(cliente, "dca", {"an_exercicio": ano, "id_ente": codigo, "no_anexo": anexo_dca})
                rreo = _todas(cliente, "rreo", {"an_exercicio": ano, "nr_periodo": 6,
                                                "co_tipo_demonstrativo": "RREO",
                                                "no_anexo": "RREO-Anexo 02", "id_ente": codigo})
                comparacao = comparar(dca, rreo)
                registro = {"ano": ano, "municipio_id": codigo, "municipio": nome,
                            "linhas_dca": len(dca), "linhas_rreo": len(rreo), "estagios": comparacao}
                registros.append(registro)
                marcas = " ".join(f"{k.split()[1][:4]}={'ok' if v['coincide'] else 'DIF'}"
                                  for k, v in comparacao.items())
                print(f"{ano} {nome:26} dca={len(dca):4} rreo={len(rreo):4} {marcas}")
    Path(args.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.saida).write_text(json.dumps(registros, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saída:", args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
