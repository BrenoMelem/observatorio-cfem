import json
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from scripts.commodities.fred import ContratoFredError, executar_commodities, extrair_fred

CHAVE = "a" * 32
AGORA = lambda: datetime(2026, 10, 30, 12, tzinfo=timezone.utc)  # noqa: E731


def meta(serie):
    return {"seriess": [{"id": serie, "frequency_short": "M", "units": "U.S. Dollars per Metric Ton",
                         "last_updated": "2026-10-30"}]}


def dados():
    return {"count": 3, "observations": [{"date": "1991-12-01", "value": "."}, {"date": "1992-01-01", "value": "14.31"},
                                         {"date": "1992-02-01", "value": "15.2"}]}


def buscar_ok(url):
    p = urlparse(url)
    serie = parse_qs(p.query)["series_id"][0]
    assert parse_qs(p.query)["api_key"] == [CHAVE]
    return 200, json.dumps(dados() if p.path.endswith("/observations") else meta(serie))


def test_preserva_meses_ausentes_e_publica_serie_global_provisoria(pasta_dados):
    r = executar_commodities(pasta_dados, CHAVE, buscar_ok, AGORA)
    assert r["situacao"] == "publicado_provisorio" and r["nulos"] == 2
    arquivo = pasta_dados / "publicado" / "commodities.json"
    linhas = json.loads(arquivo.read_text(encoding="utf-8"))
    assert len(linhas) == 6
    assert linhas[0]["municipio_id"] is None and linhas[0]["nivel_territorial"] == "global"
    assert linhas[0]["natureza_valor"] == "ausente" and linhas[1]["valor"] == 14.31
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
