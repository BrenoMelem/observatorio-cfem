"""Testes de contrato e de lacunas da API publicada."""
import json

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import publicacao


def _cliente(tmp_path, monkeypatch, linhas=None):
    monkeypatch.setattr(publicacao, "PUBLICADO", tmp_path)
    if linhas is not None:
        (tmp_path / "populacao.json").write_text(json.dumps(linhas), encoding="utf-8")
    return TestClient(app)


def _observacao():
    return {"indicador": "populacao_estimada", "municipio_id": "1502152", "municipio_nome": "Canaã dos Carajás",
            "nivel_territorial": "município", "ano": 2025, "mes": None, "valor": 89524, "unidade": "pessoas",
            "natureza_valor": "informado", "estado_validacao": "validado", "fonte": "IBGE SIDRA",
            "edicao_fonte": "2025", "atualizado_em": "2026-10-30T12:00:00Z", "versao_tratamento": "1.0.0"}


def test_lacunas_explicitas_sem_publicacao(tmp_path, monkeypatch):
    cliente = _cliente(tmp_path, monkeypatch)
    for dimensao in ("social", "economica", "ambiental", "institucional"):
        resposta = cliente.get(f"/api/v1/dimensoes/{dimensao}")
        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["dados"] == []
        assert corpo["lacunas"]
        assert all(s["situacao"] == "sem_dado_validado" and s["motivo"] for s in corpo["status"])
    status = cliente.get("/api/v1/indicadores/status").json()
    assert len(status) == 7
    assert all(s["situacao"] == "sem_dado_validado" for s in status)


def test_populacao_publicada_filtros_e_csv(tmp_path, monkeypatch):
    cliente = _cliente(tmp_path, monkeypatch, [_observacao()])
    resposta = cliente.get("/api/v1/dimensoes/social", params={"municipio_id": "1502152", "ano_inicio": 2025})
    assert resposta.status_code == 200
    assert resposta.json()["dados"][0]["valor"] == 89524
    assert resposta.json()["status"][0]["situacao"] == "publicado"
    vazio = cliente.get("/api/v1/dimensoes/social", params={"ano_inicio": 2026}).json()
    assert vazio["dados"] == []
    assert vazio["status"][0]["situacao"] == "publicado"
    csv = cliente.get("/api/v1/dimensoes/social.csv")
    assert csv.status_code == 200
    assert csv.text.startswith("\ufeffindicador;")
    assert "IBGE SIDRA" in csv.text and "Valor informado pelo SIDRA" in csv.text
    assert cliente.get("/api/v1/dimensoes/social.csv", params={"ano_inicio": 2026}).text.count("\n") == 1


def test_publicacao_invalida_nao_e_exposta(tmp_path, monkeypatch):
    invalida = _observacao() | {"estado_validacao": "provisório"}
    cliente = _cliente(tmp_path, monkeypatch, [invalida])
    assert cliente.get("/api/v1/dimensoes/social").status_code == 503
    assert cliente.get("/api/v1/dimensoes/social.csv").status_code == 503


def test_filtros_invalidos(tmp_path, monkeypatch):
    cliente = _cliente(tmp_path, monkeypatch)
    assert cliente.get("/api/v1/dimensoes/inexistente").status_code == 404
    assert cliente.get("/api/v1/dimensoes/social", params={"municipio_id": "123"}).status_code == 422
    assert cliente.get("/api/v1/dimensoes/social", params={"ano_inicio": 2026, "ano_fim": 2025}).status_code == 422
