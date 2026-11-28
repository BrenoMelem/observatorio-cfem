"""Pink Sheet: leitura, conferência com a planilha anual e coleta (RN-FNT-05, RN-TMP-13/14, RN-VPU-07/12)."""

import io
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
from openpyxl import load_workbook

from observatorio import coleta
from observatorio.fontes import pink_sheet
from observatorio.fontes.pink_sheet import IND_COBRE, IND_CONTRATO, IND_SPOT
from observatorio.modelo.lote import LotePinkSheet, Resultado
from observatorio.validacao import pink_sheet as validacao

FIXTURES = Path(__file__).parent / "fixtures" / "pink_sheet"
MENSAL = (FIXTURES / "mensal-recorte.xlsx").read_bytes()
ANUAL = (FIXTURES / "anual-recorte.xlsx").read_bytes()
PAGINA = (
    '<a href="https://thedocs.worldbank.org/en/doc/x/related/CMO-Historical-Data-Monthly.xlsx">m</a>'
    '<a href="https://thedocs.worldbank.org/en/doc/x/related/CMO-Historical-Data-Annual.xlsx">a</a>'
)
COLUNAS_ESPERADAS = ["Iron ore, cfr spot", "Copper"]


def buscar_falso(url: str) -> bytes:
    if url == pink_sheet.PAGINA:
        return PAGINA.encode()
    return MENSAL if url.endswith("Monthly.xlsx") else ANUAL


def excluidos(resultado: Resultado) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], resultado.relatorio["excluidos"])


def lote(tmp_path: Path) -> LotePinkSheet:
    return pink_sheet.coletar(tmp_path / "bruto", buscar_falso)


def test_colunas_esperadas_e_unidades() -> None:
    """RN-VPU-04: as colunas pelo nome e as unidades da planilha."""
    assert list(pink_sheet.UNIDADES_PLANILHA) == COLUNAS_ESPERADAS
    assert set(pink_sheet.ler_mensal(MENSAL)) == set(COLUNAS_ESPERADAS)


def test_series_e_recortes(tmp_path: Path) -> None:
    """RN-TMP-13/14: ferro em duas séries; contrato 1985–2005; spot desde dez/2008; cobre desde 2000."""
    observacoes = lote(tmp_path).observacoes
    contrato = [o for o in observacoes if o.indicador == IND_CONTRATO]
    spot = [o for o in observacoes if o.indicador == IND_SPOT]
    cobre = [o for o in observacoes if o.indicador == IND_COBRE]
    assert [o.ano for o in contrato] == list(range(1985, 2006))
    assert all(o.mes is None and o.unidade == "¢/dmtu" for o in contrato)
    assert (spot[0].ano, spot[0].mes, spot[0].valor) == (2008, 12, Decimal("70.0"))
    assert (cobre[0].ano, cobre[0].mes) == (2000, 1)
    assert all(o.nivel_territorial == "global" and o.municipio_id is None for o in observacoes)
    assert {o.unidade for o in spot} == {"USD/dmt"} and {o.unidade for o in cobre} == {"USD/t"}


def test_layout_alterado_falha() -> None:
    """RN-VPU-04: unidade inesperada na planilha falha de forma explícita."""
    livro = load_workbook(io.BytesIO(MENSAL))
    for linha in livro["Monthly Prices"].iter_rows():
        for celula in linha:
            if celula.value == "($/mt)":
                celula.value = "($/kg)"
    saida = io.BytesIO()
    livro.save(saida)
    with pytest.raises(ValueError, match="unidade inesperada"):
        pink_sheet.ler_mensal(saida.getvalue())


def test_link_ausente_falha() -> None:
    """RN-VPU-04: página sem o endereço da planilha."""
    with pytest.raises(ValueError, match="0 endereços"):
        pink_sheet.achar_link("<html></html>", "Monthly")


def test_validacao_estados_e_exclusoes(tmp_path: Path) -> None:
    """RN-VPU-07, RN-TMP-12, exceção de RN-VPU-12: validado, provisório no ano corrente, 2008 fora."""
    resultado = validacao.validar(lote(tmp_path))
    assert resultado.aprovado, resultado.erros
    por_estado = {(o.indicador, o.ano): o.estado_validacao for o in resultado.observacoes}
    assert por_estado[(IND_COBRE, 2025)] == "validado"
    assert por_estado[(IND_COBRE, 2026)] == "provisório"
    assert por_estado[(IND_SPOT, 2025)] == "validado"
    assert por_estado[(IND_CONTRATO, 2005)] == "validado"
    assert (IND_SPOT, 2008) not in por_estado
    assert any(e["indicador"] == IND_SPOT and e["ano"] == 2008 for e in excluidos(resultado))


def test_divergencia_acima_da_tolerancia_exclui_o_ano(tmp_path: Path) -> None:
    """RN-VPU-12 (exceção de 27/11/2026): 1 USD/t ou mais de diferença bloqueia aquele ano."""
    base = lote(tmp_path)
    referencia = dict(base.referencia)
    referencia[(IND_COBRE, 2024)] += Decimal(2)
    resultado = validacao.validar(replace(base, referencia=referencia))
    assert resultado.aprovado
    assert all(not (o.indicador == IND_COBRE and o.ano == 2024) for o in resultado.observacoes)
    assert any(e["ano"] == 2024 and e["indicador"] == IND_COBRE for e in excluidos(resultado))


def test_diferenca_de_arredondamento_da_anual_passa(tmp_path: Path) -> None:
    """Exceção de RN-VPU-12: cobre 2002, média 1559,58 contra 1559 na anual, é aceito."""
    resultado = validacao.validar(lote(tmp_path))
    assert any(o.indicador == IND_COBRE and o.ano == 2002 for o in resultado.observacoes)


def configurar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("OBS_DATA_DIR", str(tmp_path / "dados"))
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path / "publicado"))
    monkeypatch.setenv("OBS_MANIFESTO", str(Path(__file__).parents[2] / "data" / "indicadores.json"))
    return tmp_path / "publicado"


def test_coleta_publica_e_so_se_mudou(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RN-VPU-03, RN-TMP-02: publica o pacote parcial; a mesma edição não republica."""
    publicado = configurar(tmp_path, monkeypatch)
    primeiro = coleta.executar_pinksheet(buscar=buscar_falso)
    assert primeiro["situacao"] == "aprovado"
    pacote = json.loads((publicado / "pacote.json").read_text())
    assert set(pacote["indicadores"]) == {IND_CONTRATO, IND_SPOT, IND_COBRE}
    assert "qualidade-pinksheet.json" in pacote["arquivos"]
    segundo = coleta.executar_pinksheet(somente_se_mudou=True, buscar=buscar_falso)
    assert segundo["situacao"] == "sem_mudanca"
    assert json.loads((publicado / "pacote.json").read_text())["versao"] == pacote["versao"]


def test_edicao_com_valor_corrigido_prevalece_e_vai_para_o_relatorio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Decisão de 27/11/2026: edição nova que corrige ano validado vale se passar na conferência."""
    configurar(tmp_path, monkeypatch)
    coleta.executar_pinksheet(buscar=buscar_falso)
    livro = load_workbook(io.BytesIO(MENSAL))
    livro_anual = load_workbook(io.BytesIO(ANUAL))
    for ws in (livro["Monthly Prices"],):
        for linha in ws.iter_rows():
            if linha[0].value and str(linha[0].value).startswith("2020M"):
                linha[2].value = float(str(linha[2].value)) + 12  # +12 USD/t em cada mês de 2020
    for linha in livro_anual["Annual Prices (Nominal)"].iter_rows():
        if linha[0].value is not None and str(linha[0].value).split(".")[0] == "2020":
            linha[2].value = float(str(linha[2].value)) + 12
    mensal, anual = io.BytesIO(), io.BytesIO()
    livro.save(mensal)
    livro_anual.save(anual)

    def buscar_novo(url: str) -> bytes:
        if url == pink_sheet.PAGINA:
            return PAGINA.encode()
        return mensal.getvalue() if url.endswith("Monthly.xlsx") else anual.getvalue()

    resumo = coleta.executar_pinksheet(buscar=buscar_novo)
    assert resumo["situacao"] == "aprovado"
    relatorio = json.loads(Path(str(resumo["relatorio"])).read_text())
    assert f"{IND_COBRE}:2020" in relatorio["anos_alterados"]


def test_reprovacao_preserva_o_pacote(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RN-VPU-03: layout novo reprova a coleta e os bytes publicados não mudam."""
    publicado = configurar(tmp_path, monkeypatch)
    coleta.executar_pinksheet(buscar=buscar_falso)
    antes = (publicado / "pacote.json").read_bytes()

    def sem_link(url: str) -> bytes:
        return b"<html></html>" if url == pink_sheet.PAGINA else MENSAL

    resumo = coleta.executar_pinksheet(buscar=sem_link)
    assert resumo["situacao"] == "reprovado"
    assert (publicado / "pacote.json").read_bytes() == antes
