"""RN-VPU-04/07, RN-CFE-06/07/12: tabelas oficiais da ANM Extra, com recorte de páginas reais."""

import gzip
import hashlib
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from observatorio.fontes.referencia_anm import (
    Pagina,
    ReferenciaMensal,
    ReferenciaNacional,
    extrair_municipal,
    extrair_nacional,
    referencias_municipais,
)
from observatorio.referencias import atualizar

FIXTURES = Path(__file__).parent / "fixtures"
PA = (FIXTURES / "anm-extra-pa-2025.html").read_text(encoding="utf-8")
BRASIL = (FIXTURES / "anm-extra-brasil-2025.html").read_text(encoding="utf-8")


def _pagina(html: str) -> Pagina:
    corpo = html.encode()
    return Pagina(html, hashlib.sha256(corpo).hexdigest(), gzip.compress(corpo))


def test_amostra_real_municipal_e_nacional() -> None:
    """RN-VPU-04: o layout real tem nome, 12 meses e total; só os municípios da RI entram."""
    valores = extrair_municipal(PA, 2025)
    assert set(valores) == {"1502152", "1505536"}  # Abaetetuba está na amostra e fica de fora
    assert valores["1505536"][0] == Decimal("120784171.37")
    assert sum(v for v in valores["1502152"] if v is not None) == Decimal("1248202989.59")
    assert extrair_nacional(BRASIL, 2025) == Decimal("7910068296.76")


def test_layout_alterado_falha() -> None:
    """RN-VPU-04: página sem a tabela esperada falha de forma explícita, sem referência vazia."""
    with pytest.raises(ValueError, match="nenhum município"):
        extrair_municipal("<table><tr><td>x</td></tr></table>", 2025)
    with pytest.raises(ValueError, match="rodapé"):
        extrair_nacional(BRASIL.replace("tfoot", "tbody"), 2025)
    with pytest.raises(ValueError, match="soma dos meses"):
        extrair_municipal(PA.replace("120.784.171,37", "120.784.171,38"), 2025)


def test_ano_corrente_so_com_meses_fechados() -> None:
    """RN-CFE-06: no ano corrente, só os meses anteriores ao mês da captura viram referência."""
    referencias = referencias_municipais(_pagina(PA), 2026, "2026-07-05", ate_mes=6)
    assert referencias and max(r["mes"] for r in referencias) == 6


def _obter(url: str) -> Pagina:
    return _pagina(BRASIL if "cfem_ano" in url else PA)


def test_atualizar_so_regrava_o_ano_que_mudou(tmp_path: Path) -> None:
    """RN-VPU-07: sem mudança, nada é regravado; valor alterado aparece no resumo para revisão."""
    hoje = date(2026, 3, 10)
    mensais, nacionais, resumo = atualizar(tmp_path, [], [], hoje, _obter, primeiro_ano=2025)
    assert resumo.mudou and resumo.anos_atualizados == ["PA 2025", "Brasil 2025", "PA 2026"]
    assert {r["mes"] for r in mensais if r["ano"] == 2026} == {1, 2}  # março ainda não fechou
    assert [r["ano"] for r in nacionais] == [2025]  # sem total nacional do ano corrente
    for arquivo in tmp_path.iterdir():
        arquivo.unlink()

    mesmas_m, mesmas_n, sem_mudanca = atualizar(
        tmp_path, mensais, nacionais, date(2026, 3, 20), _obter, primeiro_ano=2025
    )
    assert not sem_mudanca.mudou and not list(tmp_path.iterdir())
    assert mesmas_m == mensais and mesmas_n == nacionais  # data e hash antigos preservados

    alterada: list[ReferenciaMensal] = [
        {**r, "valor": "1.00"} if (r["ano"], r["municipio_id"], r["mes"]) == (2025, "1505536", 1) else r
        for r in mensais
    ]
    sem_dezembro: list[ReferenciaNacional] = []
    _, _, revisao = atualizar(tmp_path, alterada, sem_dezembro, hoje, _obter, primeiro_ano=2025)
    assert revisao.valores_alterados == ["1505536:2025:01: 1.00 → 120784171.37"]
    assert revisao.celulas_novas == ["Brasil:2025"]
    assert sorted(p.name for p in tmp_path.iterdir()) == ["anm-brasil-2025.html.gz", "anm-pa-2025.html.gz"]
    assert "Valores alterados (revisar com atenção)" in revisao.markdown()
