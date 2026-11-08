"""Analisa as duplicatas da arrecadação da ANM para decisão humana (RN-VPU-11).

Script de teste/laboratório (não é o produto). Porte de analisar-duplicatas-cfem.mjs. Nunca exporta
identificadores pessoais: o relatório traz só município, ano, mês, números de linha e as datas de criação.

Uso:
    uv run python -m scripts.cfem.analisar_duplicatas [CSV] [RELATORIO.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.cfem.preparar import CABECALHO_ANM, ler_csv_anm
from scripts.comum.arquivos import escrever_json
from scripts.comum.municipios import MUNICIPIOS

DESTINO_PADRAO = "output/observatorio/qualidade/duplicatas-cfem.json"


def analisar_duplicatas(arquivo: str | Path, destino: str | Path = DESTINO_PADRAO) -> dict:
    vistos: dict[str, tuple[int, str]] = {}
    totais: dict[int, dict] = {}
    duplicatas: list[dict] = []
    cabecalho, linha = False, 0
    for cols in ler_csv_anm(arquivo):
        if not cabecalho:
            nomes = [c.lstrip("﻿") if i == 0 else c for i, c in enumerate(cols)]
            if tuple(nomes) != CABECALHO_ANM:
                raise ValueError("Cabeçalho ANM alterado")
            cabecalho = True
            continue
        linha += 1
        if len(cols) != 14:
            raise ValueError(f"Linha {linha}: quantidade de campos alterada")
        codigo = cols[8]
        try:
            ano, mes = int(cols[0]), int(cols[1])
        except ValueError:
            ano = mes = None
        if codigo not in MUNICIPIOS or (ano is not None and ano < 2003):
            continue
        if ano is None or not 1 <= mes <= 12:
            raise ValueError(f"Linha {linha}: período inválido")
        resumo = totais.setdefault(ano, {"linhas_recorte": 0, "duplicatas": 0})
        resumo["linhas_recorte"] += 1
        chave = json.dumps(cols)  # só em memória; preserva a igualdade dos 14 campos
        primeira = vistos.get(chave)
        if primeira:
            resumo["duplicatas"] += 1
            duplicatas.append({
                "municipio_id": codigo, "municipio_nome": MUNICIPIOS[codigo], "ano": ano, "mes": mes,
                "linha_original": primeira[0], "linha_duplicada": linha,
                "data_criacao_original": primeira[1], "data_criacao_duplicada": cols[13],
                "datas_criacao_iguais": primeira[1] == cols[13],
                "campos_identicos_incluindo_identificador": True,
            })
        else:
            vistos[chave] = (linha, cols[13])
    if not cabecalho:
        raise ValueError("CSV vazio")
    relatorio = {
        "finalidade": "Insumo para decisão do mantenedor; nenhuma duplicata foi removida e nenhum lote foi liberado.",
        "linhas_lidas": linha, "duplicatas": len(duplicatas),
        "por_ano": {str(a): totais[a] for a in sorted(totais)}, "linhas_duplicadas": duplicatas,
    }
    escrever_json(Path(destino), relatorio)
    return relatorio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("arquivo", nargs="?", default="tmp/CFEM_Arrecadacao.csv")
    parser.add_argument("destino", nargs="?", default=DESTINO_PADRAO)
    args = parser.parse_args(argv)
    arquivo, destino = args.arquivo, args.destino
    try:
        r = analisar_duplicatas(arquivo, destino)
    except (ValueError, OSError) as erro:
        print(erro, file=sys.stderr)
        return 1
    recorte = sum(x["linhas_recorte"] for x in r["por_ano"].values())
    print(f"CFEM arrecadada: {r['linhas_lidas']} linhas nacionais; {recorte} linhas no recorte; "
          f"{r['duplicatas']} duplicatas integrais. Relatório: {destino}. "
          "Tratamento pendente de decisão do mantenedor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
