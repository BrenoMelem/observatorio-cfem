"""Busca explicações em três documentos permitidos, sem incorporar instruções do usuário."""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
ARQUIVOS = [RAIZ / "docs/regras-de-negocio/glossario.md",
            RAIZ / "docs/regras-de-negocio/modelo-de-dados.md",
            RAIZ / "docs/regras-de-negocio/entrega-dos-dados.md"]


def explicacao(indicador: str) -> str:
    manifesto = json.loads((RAIZ / "data/indicadores.json").read_text(encoding="utf-8"))
    item = manifesto[indicador]
    textos = [item["nome"], item["metodo"], item["limitacoes"]]
    termos = {t.lower() for t in re.findall(r"[\wÀ-ÿ]{5,}", item["nome"])}
    for caminho in ARQUIVOS:
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if linha.startswith(("| ", "- **Regra:**")) and any(t in linha.lower() for t in termos):
                textos.append(linha[:300])
                break
    return " ".join(textos)[:1200]

