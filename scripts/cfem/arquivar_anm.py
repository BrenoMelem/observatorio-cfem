"""Baixa os arquivos CFEM da ANM, compara com a última coleta arquivada e atualiza o manifesto.

Script de teste/laboratório (não é o produto). Serve para provar quando um arquivo da ANM mudou: guarda
tamanho, SHA-256, cabeçalhos HTTP, contagem de linhas e totais do recorte dos 12 municípios por ano. O
arquivo bruto vai para uma Release do GitHub pelo workflow `.github/workflows/arquivar-anm.yml`, não
para o Git. O manifesto só ganha uma entrada quando algum arquivo mudou.

Uso:
    uv run python -m scripts.cfem.arquivar_anm --pasta DESTINO [--anterior PASTA] [--manifesto ARQ.json]
        [--github-output ARQ]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from scripts.cfem.anm_arquivos import FONTES, decodificar, indices, interpretar, separar
from scripts.cfem.comparar_versoes_anm import comparar, texto_markdown
from scripts.comum.arquivos import agora, escrever_json, iso_utc

CERTIFICADO_INTERMEDIARIO = Path(__file__).parent / "certificados" / "sectigo-ov-r36.pem"
MANIFESTO_PADRAO = "registros/manifesto.json"
AGENTE = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/124.0 Safari/537.36")

Baixador = Callable[[str, Path], dict]


def baixar_http(url: str, destino: Path) -> dict:
    """Baixa em fluxo (os arquivos têm centenas de MB) e devolve os cabeçalhos HTTP relevantes."""
    import ssl

    import certifi
    import httpx

    contexto = ssl.create_default_context(cafile=certifi.where())
    contexto.load_verify_locations(CERTIFICADO_INTERMEDIARIO)  # a ANM não envia o intermediário
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        with httpx.stream("GET", url, headers={"User-Agent": AGENTE}, timeout=600, follow_redirects=True,
                          verify=contexto) as r:
            if r.status_code != 200:
                raise OSError(f"{url}: HTTP {r.status_code}")
            with open(destino, "wb") as f:
                f.writelines(r.iter_bytes(1 << 20))
            return {"last_modified": r.headers.get("last-modified"), "etag": r.headers.get("etag"), "content_type": r.headers.get("content-type"),
                    "content_length": r.headers.get("content-length")}
    except httpx.HTTPError as erro:
        raise OSError(f"{url}: {type(erro).__name__}: {erro}") from erro


def resumir(arquivo: Path, fonte: str) -> dict:
    sha, tamanho, linhas = hashlib.sha256(), 0, 0
    por_ano: dict[int, list] = defaultdict(lambda: [0, Decimal(0)])
    idx, cabecalho = {}, ""
    with open(arquivo, "rb") as f:
        for n, bruto in enumerate(f):
            sha.update(bruto)
            tamanho += len(bruto)
            if n == 0:
                cabecalho = decodificar(bruto).lstrip("﻿")
                idx = indices(separar(cabecalho, fonte), fonte)
                continue
            linhas += 1
            try:
                achado = interpretar(separar(decodificar(bruto), fonte), idx, fonte)
            except csv.Error:
                continue
            if achado:
                por_ano[achado[0]][0] += 1
                por_ano[achado[0]][1] += achado[2]
    return {
        "bytes": tamanho, "sha256": sha.hexdigest().upper(), "linhas": linhas, "cabecalho": cabecalho,
        "recorte_por_ano": {str(a): {"linhas": v[0], "valor": f"{v[1]:.2f}"} for a, v in sorted(por_ano.items())},
    }


def _ler_manifesto(caminho: Path) -> list[dict]:
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def arquivar(pasta: Path, manifesto: Path, anterior: Path | None = None, baixador: Baixador = baixar_http) -> dict:
    """Baixa, compara com a última entrada do manifesto e, se algo mudou, acrescenta uma entrada."""
    entradas = _ler_manifesto(manifesto)
    ultima = entradas[-1]["arquivos"] if entradas else {}
    instante = agora()
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos, mudou = {}, []
    for nome, config in FONTES.items():
        destino = pasta / f"{nome}.csv"
        cabecalhos = baixador(config["url"], destino)
        resumo = resumir(destino, nome)
        alterado = ultima.get(nome, {}).get("sha256") != resumo["sha256"]
        if alterado:
            mudou.append(nome)
        arquivos[nome] = {"url": config["url"], **cabecalhos, **resumo, "mudou": alterado}
    resultado = {"mudou": bool(mudou), "arquivos_alterados": mudou, "tag": f"anm-{instante:%Y-%m-%d-%H%M}"}
    if not mudou:
        return resultado
    diferencas = []
    for nome in mudou:
        antigo = (anterior / f"{nome}.csv") if anterior else None
        if antigo and antigo.exists():
            diferencas.append(texto_markdown(comparar(nome, antigo, pasta / f"{nome}.csv")))
        else:
            diferencas.append(f"### {nome}\n\nSem versão anterior arquivada para comparar (primeira coleta ou arquivo novo).\n")
    (pasta / "diferencas.md").write_text(
        f"# Diferenças da coleta de {instante:%d/%m/%Y}\n\n" + "\n".join(diferencas), encoding="utf-8")
    entradas.append({"coletado_em": iso_utc(instante), "release": resultado["tag"], "arquivos": arquivos})
    escrever_json(manifesto, entradas)
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pasta", required=True, help="onde guardar os arquivos baixados (fora do repositório)")
    parser.add_argument("--anterior", help="pasta com a versão anterior, para o relatório de diferenças")
    parser.add_argument("--manifesto", default=MANIFESTO_PADRAO)
    parser.add_argument("--github-output", help="arquivo $GITHUB_OUTPUT (grava mudou e tag)")
    args = parser.parse_args(argv)
    try:
        r = arquivar(Path(args.pasta), Path(args.manifesto), Path(args.anterior) if args.anterior else None)
    except (OSError, ValueError) as erro:
        print(erro, file=sys.stderr)
        return 1
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as f:
            f.write(f"mudou={'true' if r['mudou'] else 'false'}\ntag={r['tag']}\n")
    print("Mudou: " + (", ".join(r["arquivos_alterados"]) if r["mudou"] else "nenhum arquivo") + f". Tag: {r['tag']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
