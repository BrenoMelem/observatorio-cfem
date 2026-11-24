"""RN-CFE-05/11 e RN-ENT-05: agregação e exportação da demonstração."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from test_publicacao_cfem import lote_aprovado

from observatorio.api.main import app
from observatorio.publicacao.pacote import publicar


def test_ano_so_com_doze_meses(tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RN-CFE-05/11: cálculo no servidor; não soma série incompleta."""
    resultado = lote_aprovado(tmp_path)
    pasta = tmp_path / "publicado"
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    publicar(resultado, pasta, manifesto)
    cliente = TestClient(app)
    incompleto = cliente.get("/api/v1/dimensoes/economica?periodicidade=anual").json()
    assert incompleto["dados"] == []
    assert any("incompleto" in n for n in incompleto["notas"])
    meses = tuple(
        resultado.observacoes[0].model_copy(update={"mes": m, "valor": Decimal("0.01")}) for m in range(1, 13)
    )
    publicar(replace(resultado, observacoes=meses), pasta, manifesto)
    corpo = cliente.get("/api/v1/dimensoes/economica?periodicidade=anual").json()
    assert corpo["dados"][0]["valor"] == "0.12"
    assert corpo["dados"][0]["mes"] is None
    assert cliente.get("/api/v1/dimensoes/economica?periodicidade=outra").status_code == 422
