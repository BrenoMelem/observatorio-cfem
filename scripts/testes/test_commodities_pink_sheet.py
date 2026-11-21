import io
import json
from datetime import datetime, timezone

import pytest
from openpyxl import Workbook

from scripts.commodities.pink_sheet import (
    IND_CONTRATO, IND_COBRE, IND_SPOT, ContratoPinkSheetError, achar_link_mensal, executar_pink_sheet,
    extrair_pink_sheet,
)

AGORA = lambda: datetime(2026, 11, 21, 12, tzinfo=timezone.utc)  # noqa: E731
URL = "https://thedocs.worldbank.org/en/doc/abc123-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
HTML = f'<html><a href="{URL}">Monthly</a><a href="x/CMO-Historical-Data-Annual.xlsx">Anual</a></html>'
# Valores do contrato conferidos no Pink Sheet (RN-TMP-13/14): 2004 = 37,9 e 2005 = 65; spot dez/2008 = 70.
CONTRATO = {ano: 26.6 + (ano - 1985) * 0.1 for ano in range(1985, 2006)} | {2004: 37.9, 2005: 65.0}
PERIODOS = [f"{a}M{m:02d}" for a in range(1984, 2010) for m in range(1, 13)][: (2009 - 1984) * 12 + 2]


def ferro_padrao(periodo):
    ano, mes = int(periodo[:4]), int(periodo[5:])
    if ano in CONTRATO:
        return CONTRATO[ano]
    if ano < 1985:
        return 20.0
    if (ano, mes) < (2008, 12):
        return 60.0 + mes  # spot 63,5% Fe, varia mês a mês: fica fora
    return {(2008, 12): 70.0, (2009, 1): 72.0, (2009, 2): 75.0}.get((ano, mes), 80.0)


def planilha(ferro=None, cobre=None, unidade_ferro="($/dmtu)", nome_cobre="Copper", periodos=None):
    periodos = periodos or PERIODOS
    ferro = ferro or {p: ferro_padrao(p) for p in periodos}
    cobre = cobre or {p: (".." if p == "2000M02" else 1800.0 + i) for i, p in enumerate(periodos)}
    livro = Workbook()
    aba = livro.active
    aba.title = "Monthly Prices"
    aba.append(["World Bank Commodity Price Data"])
    aba.append([])
    aba.append([None, "Crude oil, average", "Iron ore, cfr spot", nome_cobre])
    aba.append([None, "($/bbl)", unidade_ferro, "($/mt)"])
    for p in periodos:
        aba.append([p, 1.6, ferro[p], cobre[p]])
    saida = io.BytesIO()
    livro.save(saida)
    return saida.getvalue()


def buscar_ok(conteudo):
    def buscar(url):
        return (200, HTML.encode()) if "commodity-markets" in url else (200, conteudo)
    return buscar


def test_separa_contrato_e_spot_e_corta_os_periodos():
    linhas = extrair_pink_sheet(planilha(), "2026-11-21T12:00:00Z", "ed1")
    contrato = [l for l in linhas if l["indicador"] == IND_CONTRATO]
    spot = [l for l in linhas if l["indicador"] == IND_SPOT]
    cobre = [l for l in linhas if l["indicador"] == IND_COBRE]
    # RN-TMP-13: contrato anual de 1985 a 2005, sem mês, em ¢/dmtu (RN-TMP-14)
    assert [l["ano"] for l in contrato] == list(range(1985, 2006))
    assert all(l["mes"] is None and l["unidade"] == "¢/dmtu" for l in contrato)
    assert {l["ano"]: l["valor"] for l in contrato}[2004] == 37.9
    assert {l["ano"]: l["valor"] for l in contrato}[2005] == 65.0
    # RN-TMP-13: spot mensal desde dez/2008, em $/dmt; 2006 a nov/2008 fora
    assert [(l["ano"], l["mes"], l["valor"]) for l in spot] == [(2008, 12, 70.0), (2009, 1, 72.0), (2009, 2, 75.0)]
    assert all(l["unidade"] == "USD/dmt" for l in spot)
    # cobre mensal desde 2000, com o ausente preservado
    assert (cobre[0]["ano"], cobre[0]["mes"]) == (2000, 1) and cobre[0]["unidade"] == "USD/t"
    assert cobre[1]["valor"] is None and cobre[1]["natureza_valor"] == "ausente"
    assert all(l["nivel_territorial"] == "global" and l["municipio_id"] is None for l in linhas)  # RN-MOD-19
    assert linhas[0]["estado_validacao"] == "provisório" and linhas[0]["edicao_fonte"] == "ed1"


def test_contrato_com_meses_diferentes_falha():
    ferro = {p: ferro_padrao(p) for p in PERIODOS} | {"1990M07": 99.9}
    with pytest.raises(ContratoPinkSheetError, match="1990"):
        extrair_pink_sheet(planilha(ferro=ferro), "x")


@pytest.mark.parametrize("conteudo", [
    planilha(nome_cobre="Cobre"),                                   # coluna renomeada
    planilha(unidade_ferro="($/dmt)"),                              # unidade mudou
    planilha(periodos=PERIODOS + ["2009M02"]),                     # mês duplicado
    planilha(periodos=PERIODOS[:-1] + ["2009M04"]),                 # lacuna na spot
    planilha(periodos=PERIODOS[: (2008 - 1984) * 12 + 11]),         # spot não chega a dez/2008
    planilha(ferro={p: (-1.0 if p == "2009M01" else ferro_padrao(p)) for p in PERIODOS}),  # preço inválido
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
    assert set(r["faixa_valores"]) == {IND_CONTRATO, IND_SPOT, IND_COBRE}
    assert list((pasta_dados / "bruto" / "pink-sheet").glob("*-CMO-Historical-Data-Monthly.xlsx"))
    linhas = json.loads((pasta_dados / "publicado" / "commodities.json").read_text(encoding="utf-8"))
    assert len(linhas) == 21 + 3 + (2009 - 2000) * 12 + 2


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
