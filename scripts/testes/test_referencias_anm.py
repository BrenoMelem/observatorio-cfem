"""Testes do extrator das tabelas oficiais da ANM (scripts/cfem/referencias_anm.py), com HTML sintético."""

import gzip
import hashlib
from decimal import Decimal

import pytest

from scripts.cfem.referencias_anm import extrair_municipal, extrair_nacional, gerar, valor_brl

MESES = "".join(f"<td>{v}</td>" for v in ["1.000,50", "", "2,00"] + [""] * 9)
MUNICIPAL = f"""<table><thead><td>Estado</td><td>Jan.</td></thead>
<tr class="labelResultado"><td nowrap> PARAUAPEBAS </td>{MESES}<td>1.002,50</td></tr>
<tr class="labelResultado"><td nowrap> ABAETETUBA </td>{MESES}<td>1.002,50</td></tr>
<tr class="labelResultadoAlternado"><td nowrap> CANAÃ DOS CARAJÁS </td>{"<td></td>" * 11}<td>5,00</td><td>5,00</td></tr>
</table>"""
NACIONAL = f"""<table><tr><td><a href="x">AC</a></td>{MESES}<td>1.002,50</td></tr>
<tfoot><tr><td> Total:</td>{MESES}<td> 1.002,50 </td></tr></tfoot></table>"""


def test_valor_brl_e_celula_vazia_e_lacuna() -> None:
    assert valor_brl("1.234.567,89") == Decimal("1234567.89")
    assert valor_brl("  ") is None


def test_extrai_so_os_municipios_da_ri_com_lacunas() -> None:
    valores = extrair_municipal(MUNICIPAL, 2025)
    assert set(valores) == {"1505536", "1502152"}  # Abaetetuba fica de fora
    assert valores["1505536"][:3] == [Decimal("1000.50"), None, Decimal("2.00")]
    assert valores["1502152"][11] == Decimal("5.00")


def test_total_que_nao_fecha_falha() -> None:
    with pytest.raises(ValueError, match="soma dos meses"):
        extrair_municipal(MUNICIPAL.replace("<td>1.002,50</td></tr>", "<td>9,99</td></tr>", 1), 2025)


def test_total_nacional_vem_do_rodape() -> None:
    assert extrair_nacional(NACIONAL, 2025) == Decimal("1002.50")
    with pytest.raises(ValueError, match="rodapé"):
        extrair_nacional(NACIONAL.replace("tfoot", "tbody"), 2025)


def test_gerar_registra_hash_do_html_e_omite_lacunas(tmp_path) -> None:
    (tmp_path / "anm-pa-2025.html.gz").write_bytes(gzip.compress(MUNICIPAL.encode()))
    (tmp_path / "anm-brasil-2025.html.gz").write_bytes(gzip.compress(NACIONAL.encode()))

    mensais, nacionais = gerar(tmp_path, [2025], "2026-11-25")

    assert [(r["municipio_id"], r["mes"], r["valor"]) for r in mensais] == [
        ("1502152", 12, "5.00"),
        ("1505536", 1, "1000.50"),
        ("1505536", 3, "2.00"),
    ]
    assert mensais[0]["sha256"] == hashlib.sha256(MUNICIPAL.encode()).hexdigest()
    assert nacionais == [
        {
            "ano": 2025,
            "valor": "1002.50",
            "documento": "ANM Extra: Arrecadação CFEM por Ano/Estado, Brasil, 2025",
            "url": "https://sistemas.anm.gov.br/arrecadacao/extra/relatorios/arrecadacao_cfem_ano.aspx?ano=2025",
            "consultado_em": "2026-11-25",
            "sha256": hashlib.sha256(NACIONAL.encode()).hexdigest(),
        }
    ]
