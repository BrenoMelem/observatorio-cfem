"""Os três arquivos da ANM que o projeto arquiva e como ler o recorte dos 12 municípios.

Módulo de laboratório (não é o produto). Usado por `arquivar_anm.py` e `comparar_versoes_anm.py`.
"""

from __future__ import annotations

import csv
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

from scripts.comum.municipios import MUNICIPIOS

BASE = "https://dadosabertos.anm.gov.br/CFEM"

FONTES: dict[str, dict] = {
    "arrecadacao": {"url": f"{BASE}/CFEM_Arrecadacao.csv", "delimitador": ",", "ano": "Ano",
                    "valor": "ValorRecolhido", "local": "CodigoMunicipio", "modo": "codigo"},
    "distribuicao": {"url": f"{BASE}/CFEM_Distribuicao.csv", "delimitador": ",", "ano": "Ano",
                     "valor": "Valor", "local": "CodigoEnte", "modo": "codigo"},
    "autuacao": {"url": f"{BASE}/CFEM_Autuacao.csv", "delimitador": ";", "ano": "AnoPublicação",
                 "valor": "Valor", "local": "Município", "modo": "nome", "uf": "UF"},
}

ENCODING = "cp1252"


def _chave_nome(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


_POR_NOME = {_chave_nome(nome): nome for nome in MUNICIPIOS.values()}


def decodificar(linha: bytes) -> str:
    return linha.decode(ENCODING, errors="replace").rstrip("\r\n")


def separar(linha: str, fonte: str) -> list[str]:
    return next(csv.reader([linha], delimiter=FONTES[fonte]["delimitador"]))


def indices(cabecalho: list[str], fonte: str) -> dict[str, int]:
    config = FONTES[fonte]
    nomes = [c.lstrip("﻿") for c in cabecalho]
    chaves = ["ano", "valor", "local"] + (["uf"] if "uf" in config else [])
    return {k: nomes.index(config[k]) for k in chaves if config[k] in nomes}


def valor_decimal(texto: str) -> Decimal:
    try:
        return Decimal(texto.strip().replace(".", "").replace(",", ".") or "0")
    except InvalidOperation:
        return Decimal(0)


def interpretar(cols: list[str], idx: dict[str, int], fonte: str) -> tuple[int, str, Decimal] | None:
    """Devolve (ano, nome do município, valor) se a linha é do recorte dos 12 municípios; senão None."""
    config = FONTES[fonte]
    try:
        local = cols[idx["local"]].strip()
        ano = int(cols[idx["ano"]])
        valor = valor_decimal(cols[idx["valor"]])
        if config["modo"] == "codigo":
            nome = MUNICIPIOS.get(local)
        else:
            nome = _POR_NOME.get(_chave_nome(local))
            if "uf" in idx and cols[idx["uf"]].strip().upper() != "PA":
                nome = None
    except (KeyError, IndexError, ValueError):
        return None
    return (ano, nome, valor) if nome else None


def ler_cabecalho(arquivo: str | Path, fonte: str) -> list[str]:
    with open(arquivo, "rb") as f:
        return separar(decodificar(f.readline()), fonte)
