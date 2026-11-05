"""Collect the decisions recorded in docs/regras-de-negocio/ since a date.

Reads the rule files (not README, glossario, pendencias or fontes/) and lists, for the
period, (1) rules whose status is DECIDIDA and whose source cites a DECISÃO-MANTENEDOR
dated in the period, (2) rules with an "Evidência de DD/MM/AAAA" note in the period that
did not become a decision, and (3) the rules still EM ABERTO. It also reads the Total line
of the README now and in the first commit of the period's baseline, so the deck can show
the before and after. Only the standard library is used; nothing is written to disk.

Usage:
    python coletar_decisoes.py --desde 24/10/2026 [--ate 04/11/2026] [--formato md|json] [--raiz CAMINHO]
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
PASTA = RAIZ / "docs" / "regras-de-negocio"


def usar_raiz(caminho):
    """Read the rules from another checkout (for example, a worktree of another branch)."""
    global RAIZ, PASTA
    RAIZ = Path(caminho).resolve()
    PASTA = RAIZ / "docs" / "regras-de-negocio"
IGNORAR = {"README.md", "glossario.md", "pendencias.md"}
TEMAS = {
    "TER": "Território", "MOD": "Modelo de dados", "FON": "Consumo de fontes",
    "FNT": "Regras por fonte", "TMP": "Tempo e atualização", "VPU": "Validação e publicação",
    "ENT": "Entrega dos dados", "CFE": "Mineração e CFEM", "IND": "Indicadores",
    "PRI": "Privacidade e licenças",
}
DATA = r"(\d{2}/\d{2}/\d{4})"


def para_data(texto):
    return datetime.strptime(texto, "%d/%m/%Y").date()


def ler_regras():
    """Return one dict per rule, with its fields and the dates found in it."""
    regras = []
    for arq in sorted(PASTA.glob("*.md")):
        if arq.name in IGNORAR:
            continue
        bloco = None
        for linha in arq.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^### (RN-[A-Z]{3}-\d{2}): (.+)$", linha)
            if m:
                bloco = {"id": m.group(1), "titulo": m.group(2), "arquivo": arq.name, "campos": {}, "evidencias": []}
                regras.append(bloco)
                continue
            if linha.startswith("## ") or linha.startswith("# "):
                bloco = None
            if bloco is None:
                continue
            c = re.match(r"^- \*\*([^:*]+):\*\*\s*(.*)$", linha)
            if c:
                nome = c.group(1).strip()
                if nome.startswith("Evidência de"):
                    bloco["evidencias"].extend(re.findall(DATA, nome))
                else:
                    bloco["campos"][nome] = c.group(2).strip()
    for r in regras:
        f = r["campos"].get("Fonte", "")
        r["status"] = r["campos"].get("Status", "")
        r["datas_decisao"] = [para_data(d) for d in re.findall(r"DECISÃO-MANTENEDOR de " + DATA, f)]
        r["datas_evidencia"] = [para_data(d) for d in r["evidencias"]]
        outros = r["campos"].get("Exceções", "") + " " + f
        r["contraria_fonte"] = bool(re.search(r"contraria|não adotada|Versão não adotada", outros))
        r["tema"] = TEMAS.get(r["id"].split("-")[1], r["id"].split("-")[1])
    return regras


def total_readme(texto):
    m = re.search(r"Total: (\d+) regras, sendo (\d+) DECIDIDAS, (\d+) PROPOSTAS e (\d+) EM ABERTO", texto)
    return dict(zip(("regras", "decididas", "propostas", "em_aberto"), map(int, m.groups()))) if m else None


def totais_na_base(desde):
    """Totals in the last commit before `desde`; if there is none, in the first commit of the README."""
    caminho = "docs/regras-de-negocio/README.md"

    def git(*args):
        return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True).stdout.strip()

    sha = git("log", f"--before={desde.isoformat()}", "-1", "--format=%H", "--", caminho)
    rotulo = f"último commit antes de {desde.strftime('%d/%m/%Y')}"
    if not sha:
        sha = git("log", "--reverse", "--format=%H", "--", caminho).splitlines()[:1]
        sha = sha[0] if sha else ""
        rotulo = "primeira versão da documentação (não havia documento antes do período)"
    if not sha:
        return None, "sem histórico"
    return total_readme(git("show", f"{sha}:{caminho}")), rotulo


def em_aberto():
    """Rows of section 1 of pendencias.md (rules still EM ABERTO)."""
    texto = (PASTA / "pendencias.md").read_text(encoding="utf-8")
    secao = texto.split("## 1.")[1].split("## 2.")[0]
    itens = []
    for linha in secao.splitlines():
        m = re.match(r"^\| (RN-[A-Z]{3}-\d{2}) \| (.+?) \| \[", linha)
        if m:
            itens.append({"regra": m.group(1), "falta": m.group(2)})
    return itens


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--desde", required=True, help="data inicial, DD/MM/AAAA")
    ap.add_argument("--ate", help="data final, DD/MM/AAAA (padrão: hoje)")
    ap.add_argument("--formato", choices=["md", "json"], default="md")
    ap.add_argument("--raiz", help="outro checkout do repositório (por exemplo, um worktree de outra branch)")
    a = ap.parse_args()
    if a.raiz:
        usar_raiz(a.raiz)
    desde = para_data(a.desde)
    ate = para_data(a.ate) if a.ate else datetime.now().date()

    regras = ler_regras()
    decisoes, evidencias = [], []
    for r in regras:
        no_periodo = [d for d in r["datas_decisao"] if desde <= d <= ate]
        if r["status"] == "DECIDIDA" and no_periodo:
            decisoes.append({**r, "data": max(no_periodo)})
        else:
            ev = [d for d in r["datas_evidencia"] if desde <= d <= ate]
            if ev:
                evidencias.append({**r, "data": max(ev)})

    antes, rotulo = totais_na_base(desde)
    agora = total_readme((PASTA / "README.md").read_text(encoding="utf-8"))
    saida = {
        "periodo": [desde.isoformat(), ate.isoformat()],
        "totais_antes": antes, "base_do_antes": rotulo, "totais_agora": agora,
        "decisoes": [
            {"id": r["id"], "titulo": r["titulo"], "tema": r["tema"], "data": r["data"].isoformat(),
             "regra": r["campos"].get("Regra", ""), "motivo": r["campos"].get("Motivo", ""),
             "contraria_fonte_anterior": r["contraria_fonte"]} for r in sorted(decisoes, key=lambda r: (r["tema"], r["id"]))],
        "evidencias_sem_decisao": [
            {"id": r["id"], "titulo": r["titulo"], "status": r["status"], "data": r["data"].isoformat()} for r in sorted(evidencias, key=lambda r: r["id"])],
        "em_aberto": em_aberto(),
    }
    if a.formato == "json":
        json.dump(saida, sys.stdout, ensure_ascii=False, indent=2)
        return
    print(f"# Decisões de {desde.strftime('%d/%m/%Y')} a {ate.strftime('%d/%m/%Y')}\n")
    print(f"- Antes ({rotulo}): {antes}")
    print(f"- Agora: {agora}\n")
    print(f"## Decisões ({len(saida['decisoes'])})")
    tema = None
    for d in saida["decisoes"]:
        if d["tema"] != tema:
            tema = d["tema"]
            print(f"\n### {tema}")
        marca = " [contraria fonte anterior]" if d["contraria_fonte_anterior"] else ""
        print(f"- {d['id']} ({d['data']}){marca}: {d['titulo']}")
    print(f"\n## Evidências registradas sem decisão ({len(saida['evidencias_sem_decisao'])})")
    for e in saida["evidencias_sem_decisao"]:
        print(f"- {e['id']} ({e['status']}, {e['data']}): {e['titulo']}")
    print(f"\n## Em aberto ({len(saida['em_aberto'])})")
    for e in saida["em_aberto"]:
        print(f"- {e['regra']}: {e['falta'][:140]}")


if __name__ == "__main__":
    main()
