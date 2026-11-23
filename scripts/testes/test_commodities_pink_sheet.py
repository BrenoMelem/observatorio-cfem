import io
import json
from datetime import datetime, timezone

import pytest
from openpyxl import Workbook

from scripts.commodities.pink_sheet import (
    ContratoPinkSheetError, achar_link_mensal, anos_com_valor_repetido, executar_pink_sheet, extrair_pink_sheet,
)

AGORA = lambda: datetime(2026, 11, 10, 12, tzinfo=timezone.utc)  # noqa: E731
URL = "https://thedocs.worldbank.org/en/doc/abc123-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
HTML = f'<html><a href="{URL}">Monthly</a><a href="x/CMO-Historical-Data-Annual.xlsx">Anual</a></html>'


def planilha(ferro=None, cobre=None, unidade_ferro="($/dmtu)", nome_cobre="Copper", periodos=None):
    periodos = periodos or ["1990M01", "1990M02", "1990M03"]
    ferro = ferro or [34.8, 34.8, 34.8]
    cobre = cobre or [2000.0, "..", 2100.5]
    livro = Workbook()
    aba = livro.active
    aba.title = "Monthly Prices"
    aba.append(["World Bank Commodity Price Data"])
    aba.append([])
    aba.append([None, "Crude oil, average", "Iron ore, cfr spot", nome_cobre])
    aba.append([None, "($/bbl)", unidade_ferro, "($/mt)"])
    for p, f, c in zip(periodos, ferro, cobre):
        aba.append([p, 1.6, f, c])
    saida = io.BytesIO()
    livro.save(saida)
    return saida.getvalue()


def buscar_ok(conteudo):
    def buscar(url):
        return (200, HTML.encode()) if "commodity-markets" in url else (200, conteudo)
    return buscar


def test_extrai_ferro_e_cobre_preservando_ausente():
    linhas = extrair_pink_sheet(planilha(), "2026-11-10T12:00:00Z", "ed1")
    assert len(linhas) == 6
    ferro = [l for l in linhas if l["indicador"] == "preco_minerio_ferro"]
    cobre = [l for l in linhas if l["indicador"] == "preco_cobre"]
    assert ferro[0]["valor"] == 34.8 and ferro[0]["unidade"] == "USD/dmt" and ferro[0]["nivel_territorial"] == "global"
    assert cobre[1]["valor"] is None and cobre[1]["natureza_valor"] == "ausente"
    assert cobre[2]["valor"] == 2100.5 and cobre[0]["unidade"] == "USD/t"
    assert linhas[0]["estado_validacao"] == "provisório" and linhas[0]["edicao_fonte"] == "ed1"


def test_detecta_anos_com_valor_anual_repetido():
    meses = [f"1990M{m:02d}" for m in range(1, 13)]
    linhas = extrair_pink_sheet(planilha(ferro=[34.8] * 12, cobre=[1.0 + i for i in range(12)], periodos=meses), "x")
    assert anos_com_valor_repetido(linhas, "preco_minerio_ferro") == [1990]
    assert anos_com_valor_repetido(linhas, "preco_cobre") == []


@pytest.mark.parametrize("conteudo", [
    planilha(nome_cobre="Cobre"),                                   # coluna renomeada
    planilha(unidade_ferro="($/dmt)"),                              # unidade mudou
    planilha(periodos=["1990M01", "1990M01", "1990M03"]),           # mês duplicado
    planilha(periodos=["1990M01", "1990M02", "1990M04"]),           # lacuna
    planilha(ferro=[-1.0, 1.0, 1.0]),                               # preço inválido
    b"nao e xlsx",
])
def test_falha_quando_o_contrato_muda(conteudo):
    with pytest.raises(ContratoPinkSheetError):
        extrair_pink_sheet(conteudo, "x")


def test_acha_o_link_mensal_na_pagina():
    assert achar_link_mensal(HTML) == URL
    with pytest.raises(ContratoPinkSheetError):
        achar_link_mensal("<html>sem link</html>")


def test_executa_guarda_edicao_e_publica(pasta_dados):
    r = executar_pink_sheet(pasta_dados, buscar_ok(planilha()), AGORA)
    assert r["situacao"] == "publicado_provisorio" and r["nulos"] == 1 and r["arquivo_url"] == URL
    assert len(r["arquivo_sha256"]) == 64
    assert list((pasta_dados / "bruto" / "pink-sheet").glob("*-CMO-Historical-Data-Monthly.xlsx"))
    linhas = json.loads((pasta_dados / "publicado" / "commodities.json").read_text(encoding="utf-8"))
    assert len(linhas) == 6


def test_falha_preserva_o_lote_publicado(pasta_dados):
    executar_pink_sheet(pasta_dados, buscar_ok(planilha()), AGORA)
    arquivo = pasta_dados / "publicado" / "commodities.json"
    antes = arquivo.read_text(encoding="utf-8")
    with pytest.raises(ContratoPinkSheetError):
        executar_pink_sheet(pasta_dados, buscar_ok(planilha(unidade_ferro="($/t)")), AGORA)
    assert arquivo.read_text(encoding="utf-8") == antes

    def sem_link(url):
        return 200, b"<html></html>"

    with pytest.raises(ContratoPinkSheetError) as erro:
        executar_pink_sheet(pasta_dados, sem_link, AGORA)
    assert erro.value.relatorio["situacao"] == "bloqueado" and arquivo.read_text(encoding="utf-8") == antes

    def fora_do_ar(url):
        return 503, b""

    with pytest.raises(ContratoPinkSheetError):
        executar_pink_sheet(pasta_dados, fora_do_ar, AGORA)
