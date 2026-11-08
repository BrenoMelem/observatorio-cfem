import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

from scripts.comum.municipios import MUNICIPIOS
from scripts.populacao.atualizar import ContratoSidraError, executar, extrair_sidra, ler_publicado
from scripts.servidor.servidor import criar_servidor
from scripts.testes.conftest import servidor_em_thread

REFERENCIA = Path(__file__).resolve().parents[2] / "data" / "referencia-populacao-2025.json"
referencia = json.loads(REFERENCIA.read_text(encoding="utf-8"))
AGORA = lambda: datetime(2026, 10, 30, 12, tzinfo=timezone.utc)  # noqa: E731


def resposta(codigo, valor=None):
    valor = referencia["valores"][codigo] if valor is None else valor
    return [{"id": 9324, "variavel": "População residente estimada", "unidade": "Pessoas", "resultados": [{
        "classificacoes": [], "series": [{"localidade": {"id": codigo, "nome": f"{MUNICIPIOS[codigo]} (PA)",
                                                         "nivel": {"id": "N6", "nome": "Município"}},
                                          "serie": {"2025": str(valor)}}]}]}]


def buscar_simulado(alterar=lambda p, c: p):
    def buscar(url):
        codigo = url.split("N6%5B")[1][:7]
        return 200, json.dumps(alterar(resposta(codigo), codigo))
    return buscar


@pytest.mark.parametrize("alterar", [
    lambda p: p[0].update(id=999),
    lambda p: p[0].update(unidade="Mil pessoas"),
    lambda p: p[0]["resultados"][0]["series"][0]["localidade"].update(id=1505536),
    lambda p: p[0]["resultados"][0].pop("series"),
])
def test_contrato_rejeita_mudancas(alterar):
    payload = resposta("1502152")
    alterar(payload)
    with pytest.raises(ContratoSidraError):
        extrair_sidra(payload, "1502152")


def test_publica_so_apos_conferir_e_falha_preserva_ultimo_lote(pasta_dados):
    relatorio = executar(pasta_dados, buscar_simulado(), REFERENCIA, agora_fn=AGORA)
    assert relatorio["situacao"] == "publicado" and len(relatorio["municipios_presentes"]) == 12
    anterior = ler_publicado(pasta_dados)
    assert len(anterior) == 12
    assert list(anterior[0]) == ["indicador", "municipio_id", "municipio_nome", "nivel_territorial", "ano", "mes",
                                 "valor", "unidade", "natureza_valor", "estado_validacao", "fonte", "edicao_fonte",
                                 "atualizado_em", "versao_tratamento"]

    def divergente(p, c):
        if c == "1502152":
            p[0]["resultados"][0]["series"][0]["serie"]["2025"] = "99999"
        return p

    with pytest.raises(Exception, match="Reconciliação falhou"):
        executar(pasta_dados, buscar_simulado(divergente), REFERENCIA, agora_fn=AGORA)
    assert ler_publicado(pasta_dados) == anterior

    def unidade(p, c):
        if c == "1502152":
            p[0]["unidade"] = "Mil pessoas"
        return p

    with pytest.raises(ContratoSidraError):
        executar(pasta_dados, buscar_simulado(unidade), REFERENCIA, agora_fn=AGORA)
    assert ler_publicado(pasta_dados) == anterior


def test_api_e_csv_leem_so_a_camada_publicada(pasta_dados):
    executar(pasta_dados, buscar_simulado(), REFERENCIA, agora_fn=AGORA)
    with servidor_em_thread(criar_servidor(pasta_dados)) as base:
        status = httpx.get(f"{base}/api/v1/status").json()
        assert status["ano_referencia"] == 2025 and status["atualizado_em"] == "2026-10-30T12:00:00.000Z"
        linhas = httpx.get(f"{base}/api/v1/populacao").json()
        assert len(linhas) == 12 and linhas[0]["natureza_valor"] == "informado"
        csv = httpx.get(f"{base}/api/v1/populacao.csv").text
        assert "municipio_id" in csv
        assert not any(x in csv for x in ("resultados", "classificacoes", "localidade"))
