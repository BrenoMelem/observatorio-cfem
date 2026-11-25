from pathlib import Path

import pytest


@pytest.fixture
def manifesto(request: pytest.FixtureRequest) -> Path:
    """O manifesto de indicadores do repositório (`data/indicadores.json`), achado pela raiz do pytest (`backend/`)."""
    caminho = request.config.rootpath.parent / "data" / "indicadores.json"
    assert caminho.is_file(), caminho
    return caminho


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--atualizar-openapi",
        action="store_true",
        help="Regrava docs/api/openapi-producao.yaml a partir da API em vez de só comparar.",
    )
