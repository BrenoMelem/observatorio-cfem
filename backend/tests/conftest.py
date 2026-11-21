from pathlib import Path

import pytest


@pytest.fixture
def manifesto(request: pytest.FixtureRequest) -> Path:
    """O manifesto de indicadores do repositório (`data/indicadores.json`), achado pela raiz do pytest (`backend/`)."""
    caminho = request.config.rootpath.parent / "data" / "indicadores.json"
    assert caminho.is_file(), caminho
    return caminho
