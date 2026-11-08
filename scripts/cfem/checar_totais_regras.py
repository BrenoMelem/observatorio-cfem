"""Confere os totais de status das regras de negócio contra a linha `Total:` do README.

Script de teste/laboratório (não é o produto). Porte de checar-totais-regras.mjs. Rode antes de commitar
qualquer mudança de status em `docs/regras-de-negocio/`. Sai com código 1 se não conferir.

Uso:
    uv run python -m scripts.cfem.checar_totais_regras
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PASTA_REGRAS = Path(__file__).resolve().parents[2] / "docs" / "regras-de-negocio"
_STATUS = re.compile(r"^- \*\*Status:\*\* (DECIDIDA|PROPOSTA|EM ABERTO|OBSOLETA)\s*$", re.MULTILINE)
_TOTAL = re.compile(
    r"^Total:\s*(\d+) regras, sendo (\d+) DECIDIDAS, (\d+) PROPOSTAS(?:,| e) (\d+) EM ABERTO"
    r"(?: e (\d+) OBSOLETAS)?\.",
    re.MULTILINE,
)
_NOME = {"DECIDIDA": "DECIDIDAS", "PROPOSTA": "PROPOSTAS", "EM ABERTO": "EM ABERTO", "OBSOLETA": "OBSOLETAS"}


def checar_totais(pasta: str | Path = PASTA_REGRAS) -> dict:
    pasta = Path(pasta)
    contagem = {"DECIDIDAS": 0, "PROPOSTAS": 0, "EM ABERTO": 0, "OBSOLETAS": 0}
    for arquivo in sorted(pasta.glob("*.md")):
        if arquivo.name == "README.md":
            continue
        for achado in _STATUS.finditer(arquivo.read_text(encoding="utf-8")):
            contagem[_NOME[achado.group(1)]] += 1
    achado = _TOTAL.search((pasta / "README.md").read_text(encoding="utf-8"))
    if not achado:
        raise ValueError("Linha Total: ausente ou em formato inesperado")
    esperado = {"total": int(achado.group(1)), "DECIDIDAS": int(achado.group(2)),
                "PROPOSTAS": int(achado.group(3)), "EM ABERTO": int(achado.group(4)),
                "OBSOLETAS": int(achado.group(5) or 0)}
    obtido = {"total": sum(contagem.values()), **contagem}
    return {"esperado": esperado, "obtido": obtido, "confere": esperado == obtido}


def main() -> int:
    try:
        resultado = checar_totais()
    except ValueError as erro:
        print(erro, file=sys.stderr)
        return 1
    print(json.dumps(resultado, ensure_ascii=False))
    return 0 if resultado["confere"] else 1


if __name__ == "__main__":
    sys.exit(main())
