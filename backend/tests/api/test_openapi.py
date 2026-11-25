"""O contrato OpenAPI versionado para o front é o que a API gera (RN-ENT-01, RN-ENT-03)."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from observatorio.api.main import app

ATUALIZAR = "uv run pytest tests/api/test_openapi.py --atualizar-openapi"


class _Dumper(yaml.SafeDumper):
    """Texto de várias linhas em bloco (`|`), para o contrato ser lido e revisado como texto."""


def _texto(dumper: yaml.SafeDumper, valor: str) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", valor, style="|" if "\n" in valor else None)


_Dumper.add_representer(str, _texto)


def _contrato(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath.parent / "docs" / "api" / "openapi-producao.yaml"


def test_contrato_versionado_igual_ao_gerado(request: pytest.FixtureRequest) -> None:
    """RN-ENT-03: o arquivo que o front lê não pode divergir das rotas servidas."""
    gerado = app.openapi()
    caminho = _contrato(request)
    if request.config.getoption("--atualizar-openapi"):
        texto = yaml.dump(gerado, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=110)
        caminho.write_text(texto, encoding="utf-8", newline="\n")
    assert caminho.is_file(), f"Contrato ausente; gere com: {ATUALIZAR}"
    versionado = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    assert versionado == gerado, f"docs/api/openapi-producao.yaml desatualizado; gere com: {ATUALIZAR}"


def test_contrato_documenta_erros_dimensoes_e_csv() -> None:
    """RN-ENT-01, RN-ENT-03: o front vê as dimensões válidas, os erros e o CSV como text/csv."""
    rotas: dict[str, Any] = app.openapi()["paths"]
    json_ = rotas["/api/v1/dimensoes/{dimensao}"]["get"]
    csv_ = rotas["/api/v1/dimensoes/{dimensao}.csv"]["get"]
    for operacao in (json_, csv_):
        assert {"404", "503"} <= set(operacao["responses"])
        dimensao = next(p for p in operacao["parameters"] if p["name"] == "dimensao")
        assert dimensao["schema"]["enum"] == ["social", "economica", "ambiental", "institucional"]
    assert list(csv_["responses"]["200"]["content"]) == ["text/csv"]
    saude = rotas["/saude"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert saude == {"$ref": "#/components/schemas/Saude"}
