"""RN-VPU-01/03, RN-ENT-01: pacote atômico e leitura consistente."""

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from test_fonte_cfem import arquivo_sintetico

from observatorio.fontes.cfem_arrecadacao import converter
from observatorio.validacao.cfem import Referencia, Resultado, validar


def lote_aprovado(pasta: Path) -> Resultado:
    lote = converter(arquivo_sintetico(pasta), pasta / "bruto")
    lote = replace(lote, registros_mensais={f"2025:{m}": 100 for m in range(1, 13)})
    ref = Referencia.model_validate(
        {
            "municipio_id": "1505536",
            "ano": 2025,
            "mes": 1,
            "valor": "0.01",
            "documento": "Fixture sintética, não é evidência real",
            "url": "https://sistemas.anm.gov.br/teste",
            "consultado_em": "2026-11-23",
            "sha256": "a" * 64,
        }
    )
    return validar(lote, [ref])


def test_publicacao_api_decimal_e_conservacao(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-VPU-03/12, RN-ENT-01: reprovação não muda os bytes publicados."""
    from observatorio.api.main import app
    from observatorio.publicacao.pacote import publicar

    pasta = tmp_path / "publicado"
    resultado = lote_aprovado(tmp_path)
    versao = publicar(resultado, pasta, manifesto)
    antes = (pasta / "pacote.json").read_bytes()
    with pytest.raises(ValueError):
        publicar(replace(resultado, aprovado=False), pasta, manifesto)
    assert (pasta / "pacote.json").read_bytes() == antes
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    cliente = TestClient(app)
    corpo = cliente.get("/api/v1/dimensoes/economica").json()
    assert corpo["versao_dados"] == versao
    assert corpo["dados"][0]["valor"] == "0.01"
    assert cliente.get("/saude").json()["estado"] == "pronto"
    assert cliente.get("/api/v1/dimensoes/economica.csv").status_code == 200


def test_corrupcao_nao_expoe_dados(tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RN-VPU-01: hash divergente invalida o pacote inteiro."""
    from observatorio.api.main import app
    from observatorio.publicacao.pacote import publicar

    pasta = tmp_path / "publicado"
    versao = publicar(lote_aprovado(tmp_path), pasta, manifesto)
    (pasta / "versoes" / versao / "cfem_arrecadada.parquet").write_bytes(b"corrompido")
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    assert TestClient(app).get("/api/v1/dimensoes/economica").status_code == 503


def test_falha_antes_da_troca_preserva_pacote(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-VPU-03: falha de rename não publica versão parcial."""
    from observatorio.publicacao.pacote import publicar

    pasta = tmp_path / "publicado"
    resultado = lote_aprovado(tmp_path)
    publicar(resultado, pasta, manifesto)
    antes = (pasta / "pacote.json").read_bytes()

    def falhar(self: Path, target: str | Path) -> Path:
        raise OSError("Falha simulada de disco")

    monkeypatch.setattr(Path, "replace", falhar)
    with pytest.raises(OSError):
        publicar(resultado, pasta, manifesto)
    assert (pasta / "pacote.json").read_bytes() == antes


def test_provisorio_so_no_ano_aberto_e_sem_total_anual(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-CFE-05/06: mês provisório do ano aberto é publicado e servido, mas não soma total anual."""
    from observatorio.api.main import app
    from observatorio.publicacao.pacote import publicar

    resultado = lote_aprovado(tmp_path)
    validado = resultado.observacoes[0]
    anterior = validado.model_copy(update={"ano": 2024})
    provisorio = validado.model_copy(update={"estado_validacao": "provisório"})
    pasta = tmp_path / "publicado"
    publicar(replace(resultado, observacoes=(anterior, provisorio)), pasta, manifesto)
    with pytest.raises(ValueError, match="ano aberto"):
        publicar(
            replace(
                resultado,
                observacoes=(anterior.model_copy(update={"estado_validacao": "provisório"}), provisorio),
            ),
            tmp_path / "outro",
            manifesto,
        )
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    cliente = TestClient(app)
    mensal = cliente.get("/api/v1/dimensoes/economica").json()["dados"]
    assert [(o["ano"], o["estado_validacao"]) for o in mensal] == [(2024, "validado"), (2025, "provisório")]
    anual = cliente.get("/api/v1/dimensoes/economica?periodicidade=anual").json()
    assert anual["dados"] == []
    assert any("2025" in nota for nota in anual["notas"])
