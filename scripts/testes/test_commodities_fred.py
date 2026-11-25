import json
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest

from scripts.commodities.fred import ContratoFredError, executar_commodities, extrair_fred

CHAVE = "a" * 32
AGORA = lambda: datetime(2026, 10, 30, 12, tzinfo=UTC)


def meta(serie):
    return {"seriess": [{"id": serie, "frequency_short": "M", "units": "U.S. Dollars per Metric Ton",
                         "last_updated": "2026-10-30"}]}


def dados():
    return {"count": 3, "observations": [{"date": "2008-11-01", "value": "."}, {"date": "2008-12-01", "value": "70.0"},
                                         {"date": "2009-01-01", "value": "72.3"}]}


def buscar_ok(url):
    p = urlparse(url)
    serie = parse_qs(p.query)["series_id"][0]
    assert parse_qs(p.query)["api_key"] == [CHAVE]
    return 200, json.dumps(dados() if p.path.endswith("/observations") else meta(serie))


def test_preserva_meses_ausentes_e_publica_serie_global_provisoria(pasta_dados):
    r = executar_commodities(pasta_dados, CHAVE, buscar_ok, AGORA)
    assert r["situacao"] == "publicado_provisorio" and r["nulos"] == 1
    arquivo = pasta_dados / "publicado" / "commodities.json"
    linhas = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(linhas) == 5  # o ferro só entra a partir de dez/2008 (RN-TMP-13); o cobre, inteiro
    ferro = [l for l in linhas if l["indicador"] == "preco_minerio_ferro_spot"]
    cobre = [l for l in linhas if l["indicador"] == "preco_cobre"]
    assert [(l["ano"], l["mes"], l["valor"]) for l in ferro] == [(2008, 12, 70.0), (2009, 1, 72.3)]
    assert ferro[0]["municipio_id"] is None and ferro[0]["nivel_territorial"] == "global"
    assert cobre[0]["natureza_valor"] == "ausente" and cobre[1]["valor"] == 70.0
    repetida = {"count": 2, "observations": [dados()["observations"][0]] * 2}
    with pytest.raises(ContratoFredError):
        extrair_fred(meta("PIORECRUSDM"), repetida, "PIORECRUSDM", "2026-10-30")

    def cobre_vazio(url):
        p = urlparse(url)
        serie = parse_qs(p.query)["series_id"][0]
        if p.path.endswith("/observations"):
            return 200, json.dumps({"count": 0, "observations": []} if serie == "PCOPPUSDM" else dados())
        return 200, json.dumps(meta(serie))

    with pytest.raises(ContratoFredError):
        executar_commodities(pasta_dados, CHAVE, cobre_vazio, AGORA)
    assert json.loads(arquivo.read_text(encoding="utf-8")) == linhas  # falha preserva o lote

    def quebra(_):
        raise RuntimeError(f"Falha com chave {CHAVE}")

    with pytest.raises(RuntimeError) as erro:
        executar_commodities(pasta_dados, CHAVE, quebra, AGORA)
    assert CHAVE not in erro.value.relatorio["erro"]
