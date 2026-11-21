"""Testes de contrato e de lacunas da API publicada."""
import json

from fastapi.testclient import TestClient

from observatorio.api.main import app


def _cliente(tmp_path, monkeypatch, manifesto, linhas=None):
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path))
    (tmp_path / "indicadores.json").write_bytes(manifesto.read_bytes())  # o manifesto vai no pacote (ADR-014)
    if linhas is not None:
        (tmp_path / "populacao.json").write_text(json.dumps(linhas), encoding="utf-8")
    return TestClient(app)


def _observacao():
    return {"indicador": "populacao_estimada", "municipio_id": "1502152", "municipio_nome": "Canaã dos Carajás",
            "nivel_territorial": "município", "ano": 2025, "mes": None, "valor": 89524, "unidade": "pessoas",
            "natureza_valor": "informado", "estado_validacao": "validado", "fonte": "IBGE SIDRA",
            "edicao_fonte": "2025", "atualizado_em": "2026-10-30T12:00:00Z", "versao_tratamento": "1.0.0"}


def test_lacunas_explicitas_sem_publicacao(tmp_path, monkeypatch, manifesto):
    cliente = _cliente(tmp_path, monkeypatch, manifesto)
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
    assert all("Pink Sheet" in s["motivo"] for s in status if s["indicador"] in {"preco_minerio_ferro", "preco_cobre"})
    economia = cliente.get("/api/v1/dimensoes/economica").json()
    assert economia["metadados"]["preco_minerio_ferro"]["fonte"] == "World Bank Pink Sheet"
    assert "¢/dmtu" in economia["metadados"]["preco_minerio_ferro"]["metodo"]


def test_populacao_publicada_filtros_e_csv(tmp_path, monkeypatch, manifesto):
    cliente = _cliente(tmp_path, monkeypatch, manifesto, [_observacao()])
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


def test_publicacao_invalida_nao_e_exposta(tmp_path, monkeypatch, manifesto):
    invalida = _observacao() | {"estado_validacao": "provisório"}
    cliente = _cliente(tmp_path, monkeypatch, manifesto, [invalida])
    assert cliente.get("/api/v1/dimensoes/social").status_code == 503
    assert cliente.get("/api/v1/dimensoes/social.csv").status_code == 503


def test_valor_nao_finito_bloqueia_publicacao(tmp_path, monkeypatch, manifesto):
    for valor in (float("nan"), float("inf")):
        cliente = _cliente(tmp_path, monkeypatch, manifesto, [_observacao() | {"valor": valor}])
        assert cliente.get("/api/v1/dimensoes/social").status_code == 503


def test_filtros_invalidos(tmp_path, monkeypatch, manifesto):
    cliente = _cliente(tmp_path, monkeypatch, manifesto)
    assert cliente.get("/api/v1/dimensoes/inexistente").status_code == 404
    assert cliente.get("/api/v1/dimensoes/social", params={"municipio_id": "123"}).status_code == 422
    assert cliente.get("/api/v1/dimensoes/social", params={"ano_inicio": 2026, "ano_fim": 2025}).status_code == 422


def test_pacote_sem_manifesto_responde_503(tmp_path, monkeypatch):
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path))
    cliente = TestClient(app)
    assert cliente.get("/api/v1/dimensoes/social").status_code == 503
    assert cliente.get("/api/v1/indicadores/status").status_code == 503


def test_manifesto_incompleto_responde_503(tmp_path, monkeypatch, manifesto):
    """Code review de 21/11/2026: manifesto sem indicador ou sem `fonte` não pode virar erro 500."""
    cliente = _cliente(tmp_path, monkeypatch, manifesto)
    definicoes = json.loads(manifesto.read_text(encoding="utf-8"))
    sem_indicador = {k: v for k, v in definicoes.items() if k != "despesa_funcao_paga"}
    (tmp_path / "indicadores.json").write_text(json.dumps(sem_indicador), encoding="utf-8")
    resposta = cliente.get("/api/v1/dimensoes/social")
    assert resposta.status_code == 503 and "despesa_funcao_paga" in resposta.json()["detail"]
    sem_fonte = definicoes | {"populacao_estimada": {"nome": "x"}}
    (tmp_path / "indicadores.json").write_text(json.dumps(sem_fonte), encoding="utf-8")
    assert cliente.get("/api/v1/dimensoes/social").status_code == 503
    assert cliente.get("/api/v1/indicadores/status").status_code == 503


def test_pacote_ilegivel_responde_503(tmp_path, monkeypatch, manifesto):
    """Erro de leitura que não é arquivo ausente (aqui, uma pasta no lugar do arquivo) vira 503, não 500."""
    cliente = _cliente(tmp_path, monkeypatch, manifesto)
    (tmp_path / "populacao.json").mkdir()
    assert cliente.get("/api/v1/dimensoes/social").status_code == 503
    (tmp_path / "indicadores.json").unlink()
    (tmp_path / "indicadores.json").mkdir()
    assert cliente.get("/api/v1/dimensoes/economica").status_code == 503


def test_saude_confere_manifesto_e_populacao(tmp_path, monkeypatch, manifesto):
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path))
    cliente = TestClient(app)
    assert cliente.get("/saude").json()["estado"] == "publicacao_invalida"  # sem manifesto
    (tmp_path / "indicadores.json").write_bytes(manifesto.read_bytes())
    assert cliente.get("/saude").json()["estado"] == "sem_publicacao"
    (tmp_path / "populacao.json").write_text(json.dumps([_observacao()]), encoding="utf-8")
    assert cliente.get("/saude").json()["estado"] == "pronto"
    (tmp_path / "populacao.json").write_text(json.dumps([_observacao() | {"estado_validacao": "provisório"}]),
                                             encoding="utf-8")
    assert cliente.get("/saude").json()["estado"] == "publicacao_invalida"


def test_versao_dados_inclui_o_manifesto(tmp_path, monkeypatch, manifesto):
    """Code review de 21/11/2026: a versão muda quando o manifesto muda e existe em todas as dimensões."""
    cliente = _cliente(tmp_path, monkeypatch, manifesto, [_observacao()])
    antes = cliente.get("/api/v1/dimensoes/social").json()["versao_dados"]
    economica = cliente.get("/api/v1/dimensoes/economica").json()["versao_dados"]
    assert antes and economica == antes  # a versão é do pacote inteiro
    definicoes = json.loads(manifesto.read_text(encoding="utf-8"))
    definicoes["populacao_estimada"]["metodo"] += " Revisado."
    (tmp_path / "indicadores.json").write_text(json.dumps(definicoes), encoding="utf-8")
    assert cliente.get("/api/v1/dimensoes/social").json()["versao_dados"] != antes


def test_status_lista_todo_o_manifesto_e_compara_datas_e_edicoes(tmp_path, monkeypatch, manifesto):
    """RN-ENT-04: o painel de status mostra todos os indicadores do manifesto, com a última edição e data reais."""
    linhas = [_observacao() | {"ano": 2024, "edicao_fonte": "9", "atualizado_em": "2026-11-01T12:00:00+00:00"},
              _observacao() | {"edicao_fonte": "10", "atualizado_em": "2026-10-30T12:00:00Z"}]
    cliente = _cliente(tmp_path, monkeypatch, manifesto, linhas)
    definicoes = json.loads(manifesto.read_text(encoding="utf-8"))
    definicoes["indicador_novo"] = {"fonte": "x", "metodo": "y", "limitacoes": "z"}
    (tmp_path / "indicadores.json").write_text(json.dumps(definicoes), encoding="utf-8")
    status = {s["indicador"]: s for s in cliente.get("/api/v1/indicadores/status").json()}
    assert len(status) == 8 and "sem dimensão" in status["indicador_novo"]["motivo"]
    populacao = status["populacao_estimada"]
    assert populacao["metadados"]["edicao"] == "10"  # 10 > 9, não pela ordem do texto
    assert populacao["atualizado_em"] == "2026-11-01T12:00:00+00:00"  # comparado como data
