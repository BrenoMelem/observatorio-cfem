"""Lê o CSV de arrecadação da ANM (`CFEM_Arrecadacao.csv`) e gera a CFEM arrecadada mensal e anual provisória.

Script de teste/laboratório (não é o produto). Porte do protótipo em Node (cfem.mjs).
Valores somados em precisão decimal por município, ano e mês e arredondados ao centavo só no fim
(RN-CFE-11). Lote com colunas alteradas, valor inválido ou nulo ou linhas duplicadas é bloqueado
(RN-VPU-04, RN-VPU-11). Nenhum CPF/CNPJ é gravado na saída.

Uso:
    uv run python -m scripts.cfem.preparar CAMINHO/CFEM_Arrecadacao.csv

Variável de ambiente: OBS_DATA_DIR (padrão output/observatorio).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterator

from scripts.comum.arquivos import PASTA_PADRAO, escrever_json
from scripts.comum.municipios import MUNICIPIOS

CABECALHO_ANM = (
    "Ano", "Mês", "Processo", "AnoDoProcesso", "Tipo_PF_PJ", "CPF_CNPJ", "Substância", "UF",
    "CodigoMunicipio", "Município", "QuantidadeComercializada", "UnidadeDeMedida", "ValorRecolhido",
    "DataCriacao",
)
_VALOR = re.compile(r"-?\d+(?:\.\d{3})*(?:,\d{1,4})?")


class ContratoAnmError(Exception):
    """O arquivo da ANM mudou de forma ou tem dado inválido."""


def ler_csv_anm(arquivo: str | Path) -> Iterator[list[str]]:
    """Lê o CSV da ANM (latin-1/windows-1252, vírgula, aspas). Erro de aspas vira ContratoAnmError."""
    with open(arquivo, encoding="cp1252", errors="replace", newline="") as f:
        leitor = csv.reader(f, strict=True)
        try:
            for linha in leitor:
                yield linha if linha else [""]
        except csv.Error as erro:
            raise ContratoAnmError(f"CSV inválido: {erro}") from erro


def centesimos(bruto: str) -> int:
    """'1.234,5678' -> 12345678 (décimos de milésimo de real, inteiro exato)."""
    if not _VALOR.fullmatch(bruto):
        raise ContratoAnmError(f"ValorRecolhido inválido: {bruto}")
    negativo = bruto.startswith("-")
    inteiro, _, fracao = bruto.lstrip("-").replace(".", "").partition(",")
    unidades = int(inteiro) * 10000 + int(fracao.ljust(4, "0") or "0")
    return -unidades if negativo else unidades


def _para_centavos(unidades: int) -> int:
    """Arredonda para centavo, metade para longe do zero."""
    sinal = -1 if unidades < 0 else 1
    return sinal * ((abs(unidades) + 50) // 100)


def _inteiro(texto: str) -> int | None:
    try:
        return int(texto.strip())
    except ValueError:
        return None


def _obs(codigo: str, ano: int, mes: int | None, centavos: int | None) -> dict:
    return {
        "indicador": "cfem_arrecadada", "municipio_id": codigo, "municipio_nome": MUNICIPIOS[codigo],
        "nivel_territorial": "município", "ano": ano, "mes": mes,
        "valor": None if centavos is None else centavos / 100, "unidade": "BRL nominal",
        "natureza_valor": "ausente" if centavos is None else "zero real" if centavos == 0 else "informado",
        "estado_validacao": "provisório", "fonte": "ANM, CFEM_Arrecadacao.csv", "edicao_fonte": str(ano),
        "atualizado_em": None, "versao_tratamento": "1.0.0",
    }


def analisar_cfem(arquivo: str | Path) -> tuple[dict, list[dict], list[dict]]:
    cabecalho: list[str] | None = None
    indices: dict[str, int] = {}
    linhas = nulos = duplicatas = 0
    hash_recorte = hashlib.sha256()
    meses_nacionais: dict[int, set[int]] = defaultdict(set)
    somas: dict[tuple[str, int, int], int] = defaultdict(int)
    vistos: set[str] = set()
    municipios: set[str] = set()
    anos: set[int] = set()
    grupos_duplicados: dict[str, int] = defaultdict(int)

    for cols in ler_csv_anm(arquivo):
        if cabecalho is None:
            cabecalho = [c.lstrip("﻿") if i == 0 else c for i, c in enumerate(cols)]
            if tuple(cabecalho) != CABECALHO_ANM:
                raise ContratoAnmError(f"Colunas ANM alteradas: {json.dumps(cabecalho, ensure_ascii=False)}")
            indices = {nome: i for i, nome in enumerate(cabecalho)}
            continue
        linhas += 1
        if len(cols) != len(cabecalho):
            raise ContratoAnmError(f"Linha {linhas}: {len(cols)} colunas; esperado {len(cabecalho)}")
        ano, mes = _inteiro(cols[indices["Ano"]]), _inteiro(cols[indices["Mês"]])
        if ano is None or mes is None or not 1 <= mes <= 12:
            raise ContratoAnmError(f"Linha {linhas}: ano/mês inválidos")
        if ano >= 2003:
            meses_nacionais[ano].add(mes)
        codigo = cols[indices["CodigoMunicipio"]]
        if codigo not in MUNICIPIOS or ano < 2003:
            continue
        if not cols[indices["ValorRecolhido"]]:
            raise ContratoAnmError(f"Linha {linhas}: valor nulo")
        impressao = "\x1f".join(cols)
        if impressao in vistos:
            duplicatas += 1
            grupos_duplicados[f"{codigo}:{ano}:{mes}"] += 1
        else:
            vistos.add(impressao)
        somas[(codigo, ano, mes)] += centesimos(cols[indices["ValorRecolhido"]])
        municipios.add(codigo)
        anos.add(ano)
        hash_recorte.update(impressao.encode())
    if cabecalho is None:
        raise ContratoAnmError("CSV vazio")

    mensais: list[dict] = []
    anuais: list[dict] = []
    for ano in sorted(meses_nacionais):
        meses = sorted(meses_nacionais[ano])
        for mes in meses:
            for codigo in MUNICIPIOS:
                soma = somas.get((codigo, ano, mes))
                mensais.append(_obs(codigo, ano, mes, None if soma is None else _para_centavos(soma)))
        if len(meses) == 12:
            for codigo in MUNICIPIOS:
                por_mes = [somas.get((codigo, ano, m)) for m in range(1, 13)]
                if any(v is None for v in por_mes):
                    continue
                anuais.append(_obs(codigo, ano, None, _para_centavos(sum(por_mes))))

    valores = [o["valor"] for o in mensais if o["valor"] is not None]
    municipios_sem_linha = {
        str(ano): [c for c in MUNICIPIOS if all((c, ano, m) not in somas for m in meses_nacionais[ano])]
        for ano in sorted(meses_nacionais)
    }
    meses_ausentes = {
        f"{c}:{ano}": faltam
        for ano in sorted(meses_nacionais) for c in MUNICIPIOS
        if (faltam := [m for m in sorted(meses_nacionais[ano]) if (c, ano, m) not in somas])
    }
    relatorio = {
        "situacao": "bloqueado", "linhas_lidas": linhas, "municipios_presentes": sorted(municipios),
        "anos": sorted(anos), "nulos": nulos, "duplicatas": duplicatas,
        "duplicatas_por_municipio_ano_mes": dict(sorted(grupos_duplicados.items())),
        "faixa_valores_mensais": {"minimo": min(valores), "maximo": max(valores)} if valores else None,
        "meses_nacionais": {str(a): sorted(m) for a, m in sorted(meses_nacionais.items())},
        "municipios_sem_linha_por_ano": municipios_sem_linha,
        "meses_ausentes_por_municipio_ano": meses_ausentes,
        "linhas_no_recorte": len(vistos), "hash_recorte_sha256": hash_recorte.hexdigest(),
        "divergencia_fonte_primaria": "não reconciliada; publicação bloqueada",
    }
    if duplicatas:
        erro = ContratoAnmError(f"{duplicatas} linhas inteiras duplicadas no recorte; lote bloqueado")
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise erro
    return relatorio, mensais, anuais


def preparar_cfem(arquivo: str | Path, pasta_dados: str | Path = PASTA_PADRAO) -> dict:
    pasta = Path(pasta_dados) / "tratado" / "cfem"
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        relatorio, mensais, anuais = analisar_cfem(arquivo)
    except ContratoAnmError as erro:
        if hasattr(erro, "relatorio"):
            escrever_json(pasta / "relatorio.json", erro.relatorio)
        raise
    escrever_json(pasta / "arrecadacao-mensal-provisoria.json", mensais, indent=None)
    escrever_json(pasta / "arrecadacao-anual-provisoria.json", anuais, indent=None)
    escrever_json(pasta / "relatorio.json", relatorio)
    return relatorio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("arquivo", help="caminho do CFEM_Arrecadacao.csv")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(preparar_cfem(args.arquivo), ensure_ascii=False))
    except ContratoAnmError as erro:
        print(f"{type(erro).__name__}: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
