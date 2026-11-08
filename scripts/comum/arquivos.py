"""Leitura e escrita de arquivos JSON/CSV dos scripts de laboratório (escrita atômica, execução datada)."""

from __future__ import annotations

import json
import os
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

# Função que busca uma URL e devolve (status HTTP, corpo em texto). Os testes injetam uma simulada.
Buscar = Callable[[str], tuple[int, str]]

PASTA_PADRAO = os.environ.get("OBS_DATA_DIR", "output/observatorio")


def agora() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(instante: datetime) -> str:
    """Formato 2026-10-30T12:00:00.000Z."""
    instante = instante.astimezone(timezone.utc)
    return instante.strftime("%Y-%m-%dT%H:%M:%S.") + f"{instante.microsecond // 1000:03d}Z"


def id_execucao(instante_iso: str) -> str:
    sufixo = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return instante_iso.replace(":", "-").replace(".", "-") + "-" + sufixo


def buscar_http(url: str) -> tuple[int, str]:
    import httpx

    resposta = httpx.get(url, timeout=30, headers={"Accept": "application/json"}, follow_redirects=True)
    return resposta.status_code, resposta.text


def escrever_texto(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def escrever_json(caminho: Path, dados: Any, indent: int | None = 2) -> None:
    escrever_texto(caminho, json.dumps(dados, ensure_ascii=False, indent=indent) + "\n")


def escrever_json_atomico(destino: Path, dados: Any, sufixo_tmp: str) -> None:
    """Grava num arquivo temporário e troca, para o leitor nunca ver um arquivo pela metade."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_name(f"{destino.name}.{sufixo_tmp}.tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporario, destino)


def ler_json_ou_vazio(caminho: Path) -> list:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def _texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def csv_observacoes(linhas: Iterable[dict], campos: Iterable[str]) -> str:
    """CSV aberto (RN-ENT-03): UTF-8 com BOM, todos os valores entre aspas."""
    campos = list(campos)

    def aspas(valor: Any) -> str:
        return '"' + _texto(valor).replace('"', '""') + '"'

    corpo = [",".join(campos)] + [",".join(aspas(linha.get(c)) for c in campos) for linha in linhas]
    return "﻿" + "\n".join(corpo) + "\n"
