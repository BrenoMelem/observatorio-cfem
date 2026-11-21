"""Teste de fumaça: o pacote instala, os subpacotes do ADR-013 existem e a configuração lê o ambiente."""

import importlib
from pathlib import Path

import pytest

from observatorio import config


@pytest.mark.parametrize("nome", ["modelo", "fontes", "validacao", "publicacao", "api", "api.main"])
def test_subpacotes_importam(nome: str) -> None:
    importlib.import_module(f"observatorio.{nome}")


def test_configuracao_le_o_ambiente(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OBS_PUBLICADO_DIR", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    padrao = config.carregar()
    assert padrao.publicado_dir == Path("output/observatorio/publicado") and padrao.database_url is None
    monkeypatch.setenv("OBS_PUBLICADO_DIR", "/dados/publicado")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@db/obs")
    lido = config.carregar()
    assert lido.publicado_dir == Path("/dados/publicado") and lido.database_url == "postgresql://u@db/obs"
