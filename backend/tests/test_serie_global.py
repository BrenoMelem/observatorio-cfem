"""RN-MOD-03 (exceção de 21/11/2026) e RN-MOD-19: série global, sem município, publicada e lida."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from observatorio.modelo.lote import Resultado
from observatorio.modelo.observacao import Observacao


def preco(mes: int, valor: float, **extra: object) -> Observacao:
    base: dict[str, object] = {
        "indicador": "preco_cobre",
        "municipio_id": None,
        "municipio_nome": None,
        "nivel_territorial": "global",
        "ano": 2025,
        "mes": mes,
        "valor": valor,
        "unidade": "USD/t",
        "natureza_valor": "informado",
        "estado_validacao": "provisório",
        "fonte": "World Bank, Pink Sheet (teste sintético)",
        "edicao_fonte": "teste",
        "atualizado_em": "2026-11-27T00:00:00+00:00",
        "versao_tratamento": "1",
    }
    return Observacao.model_validate({**base, **extra})


def test_serie_global_sem_municipio() -> None:
    """RN-MOD-19: preço internacional não é atribuído a município."""
    assert preco(1, 9000.0).nivel_territorial == "global"
    with pytest.raises(ValueError, match="global"):
        preco(1, 9000.0, municipio_id="1505536", municipio_nome="Parauapebas")


def test_serie_global_publicada_e_lida_com_filtro_municipal(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-MOD-19, RN-VPU-03: o pacote guarda a série global e o filtro municipal não a esconde."""
    from observatorio.api.main import app
    from observatorio.publicacao.pacote import publicar

    pasta = tmp_path / "publicado"
    observacoes = (preco(1, 9000.0), preco(2, 9100.5))
    resultado = Resultado(aprovado=True, observacoes=observacoes, erros=(), relatorio={"lote": "teste"})
    publicar(resultado, pasta, manifesto, qualidade="qualidade-pinksheet.json")
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    cliente = TestClient(app)
    corpo = cliente.get("/api/v1/dimensoes/economica", params={"municipio_id": "1505536"}).json()
    dados = [o for o in corpo["dados"] if o["indicador"] == "preco_cobre"]
    assert [(o["mes"], o["nivel_territorial"], o["municipio_id"]) for o in dados] == [
        (1, "global", None),
        (2, "global", None),
    ]
    assert cliente.get("/saude").json()["estado"] == "pronto"
