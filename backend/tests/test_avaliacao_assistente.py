"""Conjunto de avaliação com respostas independentes do IBGE para os 12 municípios."""
import json
from pathlib import Path

from fastapi.testclient import TestClient
from scripts.populacao.atualizar import MUNICIPIOS

from app.main import app
from app.repositories import publicacao

RAIZ = Path(__file__).resolve().parents[2]
CONTEXTO = {"pagina": "social", "dimensao": "Social", "tema": {"id": "populacao", "titulo": "População"},
            "periodo": [2025, 2026], "comparacoes": [], "graficos": []}


def test_perguntas_verificadas_dos_doze_municipios(tmp_path, monkeypatch):
    linhas = []
    gabarito = []
    for ano in (2025, 2026):
        referencia = json.loads((RAIZ / f"data/referencia-populacao-{ano}.json").read_text(encoding="utf-8"))
        for codigo, valor in referencia["valores"].items():
            linhas.append({"indicador": "populacao_estimada", "municipio_id": codigo,
                          "municipio_nome": MUNICIPIOS[codigo], "nivel_territorial": "município", "ano": ano,
                          "mes": None, "valor": valor, "unidade": "pessoas", "natureza_valor": "informado",
                          "estado_validacao": "validado", "fonte": "IBGE SIDRA", "edicao_fonte": str(ano),
                          "atualizado_em": "2026-10-30T12:00:00Z", "versao_tratamento": "1.0.0"})
            gabarito.append((MUNICIPIOS[codigo], ano, valor))
    (tmp_path / "populacao.json").write_text(json.dumps(linhas, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(publicacao, "PUBLICADO", tmp_path)
    monkeypatch.setenv("OBS_LLM_MODO", "mock")
    monkeypatch.setenv("OBS_ASSISTENTE_LIMITE_MINUTO", "100")
    cliente = TestClient(app)
    for nome, ano, valor in gabarito:
        resposta = cliente.post("/api/v1/assistente", json={"pergunta": f"Qual a população de {nome} em {ano}?",
                                                        "contexto": CONTEXTO})
        assert resposta.status_code == 200
        dados = resposta.json()
        assert f"{valor:,}".replace(",", ".") in dados["resposta"]
        assert dados["citacoes"][0]["periodo"] == str(ano)

