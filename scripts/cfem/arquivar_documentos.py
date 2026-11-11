"""Arquiva documentos avulsos (PDF) da ANM, um por URL de `scripts/cfem/documentos.json`, e registra cada versão.

Serve a documentos que a ANM pode retirar ou substituir sem aviso (por exemplo, o PDF mensal usado na
reconciliação). Cada versão nova (SHA-256 diferente da última do manifesto) vira um arquivo na Release do
dia; o manifesto `registros/manifesto-documentos.json` guarda o histórico. Um documento que falha no
download não impede os demais: o erro fica registrado e a contagem sai em `erros`.

Uso:
    uv run python -m scripts.cfem.arquivar_documentos --pasta DESTINO [--lista documentos.json]
        [--manifesto ARQ.json] [--github-output ARQ]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from scripts.cfem.arquivar_anm import Baixador, baixar_http
from scripts.comum.arquivos import agora, escrever_json, iso_utc

LISTA_PADRAO = "scripts/cfem/documentos.json"
MANIFESTO_PADRAO = "registros/manifesto-documentos.json"


def _sha256(arquivo: Path) -> str:
    resumo = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for pedaco in iter(lambda: f.read(1 << 20), b""):
            resumo.update(pedaco)
    return resumo.hexdigest().upper()


def arquivar_documentos(pasta: Path, lista: Path, manifesto: Path, baixador: Baixador = baixar_http) -> dict:
    documentos = json.loads(lista.read_text(encoding="utf-8"))
    historico = json.loads(manifesto.read_text(encoding="utf-8")) if manifesto.exists() else {}
    instante = agora()
    tag = f"doc-{instante:%Y-%m-%d}"
    pasta.mkdir(parents=True, exist_ok=True)
    novos, erros = [], []
    for doc in documentos:
        nome, url = doc["nome"], doc["url"]
        sufixo = Path(urlparse(url).path).suffix or ".bin"
        sha_curto = ""
        destino = pasta / f"{nome}{sufixo}"
        try:
            cabecalhos = baixador(url, destino)
        except OSError as erro:
            erros.append({"nome": nome, "erro": str(erro)})
            destino.unlink(missing_ok=True)
            continue
        sha = _sha256(destino)
        versoes = historico.setdefault(nome, {"url": url, "descricao": doc.get("descricao", ""), "versoes": []})
        if versoes["versoes"] and versoes["versoes"][-1]["sha256"] == sha:
            destino.unlink()
            continue
        sha_curto = sha[:8]
        final = pasta / f"{nome}-{sha_curto}{sufixo}"
        destino.rename(final)
        versoes["versoes"].append({
            "coletado_em": iso_utc(instante), "release": tag, "arquivo": final.name, "sha256": sha,
            "bytes": final.stat().st_size, "content_type": cabecalhos.get("content_type"),
            "last_modified": cabecalhos.get("last_modified"), "etag": cabecalhos.get("etag"),
        })
        novos.append(final.name)
    if novos:
        escrever_json(manifesto, historico)
    return {"mudou": bool(novos), "novos": novos, "erros": erros, "tag": tag}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pasta", required=True)
    parser.add_argument("--lista", default=LISTA_PADRAO)
    parser.add_argument("--manifesto", default=MANIFESTO_PADRAO)
    parser.add_argument("--github-output")
    args = parser.parse_args(argv)
    try:
        r = arquivar_documentos(Path(args.pasta), Path(args.lista), Path(args.manifesto))
    except (OSError, ValueError, KeyError) as erro:
        print(erro, file=sys.stderr)
        return 1
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as f:
            f.write(f"mudou={'true' if r['mudou'] else 'false'}\ntag={r['tag']}\nerros={len(r['erros'])}\n")
    for e in r["erros"]:
        print(f"ERRO em {e['nome']}: {e['erro']}", file=sys.stderr)
    print(f"Novos: {', '.join(r['novos']) or 'nenhum'}. Erros: {len(r['erros'])}. Tag: {r['tag']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
