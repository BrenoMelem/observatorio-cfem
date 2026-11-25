"""CLI que atualiza as referências oficiais da ANM usadas pela validação da CFEM (RN-VPU-07, RN-CFE-12).

Uso (da raiz):
    python -m observatorio.referencias --pasta data/evidencias-anm \\
        --mensal data/referencia-cfem-mensal-anm.json --nacional data/referencia-cfem-nacional-anm.json

Captura, ano a ano, as tabelas da ANM Extra e compara com a referência versionada. Um ano cujos valores
não mudaram fica como está, com a captura e o SHA-256 antigos; só um ano com célula nova, valor
alterado ou célula removida ganha captura e referência novas. A mudança não é aplicada à produção aqui:
o workflow abre um PR para revisão humana (decisão do mantenedor de 25/11/2026). No ano corrente entram
só os meses já fechados, e o total nacional só existe para ano fechado (RN-CFE-06, RN-CFE-12).
"""

import argparse
import json
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from observatorio import config
from observatorio.fontes.referencia_anm import (
    Pagina,
    ReferenciaMensal,
    ReferenciaNacional,
    baixar,
    referencia_nacional,
    referencias_municipais,
    url_municipal,
    url_nacional,
)

PRIMEIRO_ANO = 2004  # 2003 não tem janeiro a abril no arquivo nacional (registro de 25/11/2026)


@dataclass
class Resumo:
    """O que mudou em relação à referência versionada; vazio quando nada mudou."""

    anos_atualizados: list[str] = field(default_factory=list)
    celulas_novas: list[str] = field(default_factory=list)
    valores_alterados: list[str] = field(default_factory=list)
    celulas_removidas: list[str] = field(default_factory=list)

    @property
    def mudou(self) -> bool:
        return bool(self.anos_atualizados)

    def markdown(self) -> str:
        linhas = [
            f"- Anos com captura nova: {', '.join(self.anos_atualizados) or 'nenhum'}",
            f"- Células novas: {len(self.celulas_novas)}",
            f"- Valores alterados: {len(self.valores_alterados)}",
            f"- Células removidas: {len(self.celulas_removidas)}",
        ]
        for titulo, itens in (
            ("Valores alterados (revisar com atenção)", self.valores_alterados),
            ("Células removidas", self.celulas_removidas),
        ):
            if itens:
                linhas += ["", f"### {titulo}", "", *(f"- {i}" for i in itens[:200])]
        return "\n".join(linhas) + "\n"


def _valores_mensais(referencias: Sequence[ReferenciaMensal]) -> dict[str, str]:
    return {f"{r['municipio_id']}:{r['ano']}:{r['mes']:02d}": r["valor"] for r in referencias}


def _valores_nacionais(referencias: Sequence[ReferenciaNacional]) -> dict[str, str]:
    return {f"Brasil:{r['ano']}": r["valor"] for r in referencias}


def _comparar(antes: dict[str, str], depois: dict[str, str], resumo: Resumo) -> bool:
    """Registra no resumo as diferenças de um ano; devolve se houve alguma."""
    if antes == depois:
        return False
    resumo.celulas_novas += sorted(depois.keys() - antes.keys())
    resumo.celulas_removidas += sorted(antes.keys() - depois.keys())
    resumo.valores_alterados += [
        f"{k}: {antes[k]} → {depois[k]}"
        for k in sorted(antes.keys() & depois.keys())
        if antes[k] != depois[k]
    ]
    return True


def atualizar(
    pasta: Path,
    mensais: list[ReferenciaMensal],
    nacionais: list[ReferenciaNacional],
    hoje: date,
    obter: Callable[[str], Pagina],
    primeiro_ano: int = PRIMEIRO_ANO,
) -> tuple[list[ReferenciaMensal], list[ReferenciaNacional], Resumo]:
    """RN-VPU-07: refaz as referências dos anos que mudaram; os demais ficam intactos."""
    resumo = Resumo()
    consultado_em = hoje.isoformat()
    novas_mensais = [r for r in mensais if not primeiro_ano <= r["ano"] <= hoje.year]
    novas_nacionais = [r for r in nacionais if not primeiro_ano <= r["ano"] <= hoje.year]
    for ano in range(primeiro_ano, hoje.year + 1):
        ate_mes = hoje.month - 1 if ano == hoje.year else 12
        atuais_m = [r for r in mensais if r["ano"] == ano]
        if ate_mes > 0:
            pagina = obter(url_municipal(ano))
            capturadas = referencias_municipais(pagina, ano, consultado_em, ate_mes)
            if _comparar(_valores_mensais(atuais_m), _valores_mensais(capturadas), resumo):
                (pasta / f"anm-pa-{ano}.html.gz").write_bytes(pagina.comprimido)
                resumo.anos_atualizados.append(f"PA {ano}")
                atuais_m = capturadas
        novas_mensais += atuais_m
        atuais_n = [r for r in nacionais if r["ano"] == ano]
        if ano < hoje.year:
            pagina = obter(url_nacional(ano))
            capturada = [referencia_nacional(pagina, ano, consultado_em)]
            if _comparar(_valores_nacionais(atuais_n), _valores_nacionais(capturada), resumo):
                (pasta / f"anm-brasil-{ano}.html.gz").write_bytes(pagina.comprimido)
                resumo.anos_atualizados.append(f"Brasil {ano}")
                atuais_n = capturada
        novas_nacionais += atuais_n
    novas_mensais.sort(key=lambda r: (r["ano"], r["municipio_id"], r["mes"]))
    novas_nacionais.sort(key=lambda r: r["ano"])
    return novas_mensais, novas_nacionais, resumo


def _escrever(caminho: Path, dados: Sequence[ReferenciaMensal] | Sequence[ReferenciaNacional]) -> None:
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--pasta", type=Path, required=True, help="Pasta das capturas .html.gz")
    parser.add_argument("--mensal", type=Path, required=True, help="Referência mensal por município (JSON)")
    parser.add_argument("--nacional", type=Path, required=True, help="Totais nacionais anuais (JSON)")
    parser.add_argument("--resumo", type=Path, help="Grava o resumo das mudanças em Markdown (corpo do PR)")
    parser.add_argument("--hoje", type=date.fromisoformat, default=date.today(), help="Data de referência")
    args = parser.parse_args()
    certificado = config.carregar().certificado_anm

    def obter(url: str) -> Pagina:
        time.sleep(1)  # uma requisição por vez: o servidor da ANM é público e lento
        return baixar(url, certificado)

    try:
        mensais = json.loads(args.mensal.read_text(encoding="utf-8"))
        nacionais = json.loads(args.nacional.read_text(encoding="utf-8"))
        args.pasta.mkdir(parents=True, exist_ok=True)
        novas_m, novas_n, resumo = atualizar(args.pasta, mensais, nacionais, args.hoje, obter)
    except (OSError, ValueError) as erro:
        print(json.dumps({"situacao": "falhou", "erro": str(erro)}, ensure_ascii=False))
        return 1
    if resumo.mudou:
        _escrever(args.mensal, novas_m)
        _escrever(args.nacional, novas_n)
    if args.resumo:
        args.resumo.write_text(resumo.markdown(), encoding="utf-8")
    print(
        json.dumps(
            {
                "situacao": "mudou" if resumo.mudou else "sem_mudanca",
                "anos_atualizados": resumo.anos_atualizados,
                "celulas_novas": len(resumo.celulas_novas),
                "valores_alterados": len(resumo.valores_alterados),
                "celulas_removidas": len(resumo.celulas_removidas),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
