"""Montagem do pacote a partir dos parciais de cada fonte (RN-VPU-01/03, ADR-011)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from test_publicacao_cfem import lote_aprovado
from test_siconfi import coletar

from observatorio.api.main import app
from observatorio.fontes import siconfi
from observatorio.modelo.pacote import DescricaoPacote
from observatorio.publicacao.montagem import montar
from observatorio.publicacao.pacote import publicar
from observatorio.validacao import siconfi as validacao


def _parciais(tmp_path: Path, manifesto: Path) -> tuple[Path, Path]:
    cfem, despesa = tmp_path / "cfem", tmp_path / "siconfi"
    publicar(lote_aprovado(tmp_path), cfem, manifesto)
    publicar(validacao.validar(coletar(tmp_path)), despesa, manifesto, qualidade="qualidade-siconfi.json")
    return cfem, despesa


def test_montar_junta_as_fontes_e_a_api_serve(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-VPU-03: o pacote montado tem os indicadores das duas fontes e os dois relatórios."""
    cfem, despesa = _parciais(tmp_path, manifesto)
    pasta = tmp_path / "publicado"
    versao = montar([cfem, despesa], pasta, manifesto)
    descricao = DescricaoPacote.model_validate_json((pasta / "pacote.json").read_bytes())
    assert descricao.versao == versao
    assert set(descricao.indicadores) == {"cfem_arrecadada", *siconfi.INDICADORES.values()}
    assert {"qualidade-cfem.json", "qualidade-siconfi.json"} <= descricao.arquivos.keys()
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    dados = TestClient(app).get("/api/v1/dimensoes/economica").json()["dados"]
    assert {d["indicador"] for d in dados} >= {"cfem_arrecadada", "despesa_funcao_paga"}


def test_montar_com_parcial_corrompido_conserva_o_pacote_anterior(tmp_path: Path, manifesto: Path) -> None:
    """RN-VPU-03: hash divergente num parcial não troca o ponteiro."""
    cfem, despesa = _parciais(tmp_path, manifesto)
    pasta = tmp_path / "publicado"
    anterior = montar([cfem], pasta, manifesto)
    descricao = DescricaoPacote.model_validate_json((despesa / "pacote.json").read_bytes())
    (despesa / "versoes" / descricao.versao / "despesa_funcao_paga.parquet").write_bytes(b"x")
    with pytest.raises(ValueError, match="corrompido"):
        montar([cfem, despesa], pasta, manifesto)
    atual = DescricaoPacote.model_validate_json((pasta / "pacote.json").read_bytes())
    assert atual.versao == anterior


def test_montar_recusa_indicador_repetido_e_lista_vazia(tmp_path: Path, manifesto: Path) -> None:
    """RN-VPU-01: o mesmo indicador em dois parciais, ou nenhum parcial, reprova."""
    cfem, _ = _parciais(tmp_path, manifesto)
    with pytest.raises(ValueError, match="mais de um"):
        montar([cfem, cfem], tmp_path / "p", manifesto)
    with pytest.raises(ValueError, match="Nenhum"):
        montar([], tmp_path / "p2", manifesto)
