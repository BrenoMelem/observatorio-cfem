"""Configuração do produto: o único módulo que lê variáveis de ambiente (ADR-017).

Nenhum outro módulo lê `os.environ` nem calcula caminho a partir da posição do próprio arquivo.
Os caminhos relativos valem a partir da pasta de onde o processo é iniciado (a raiz do repositório,
nos comandos do `backend/README.md`); no Docker, as variáveis vêm do `docker-compose.yml`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PUBLICADO_PADRAO = Path("output/observatorio/publicado")


@dataclass(frozen=True)
class Configuracao:
    publicado_dir: Path
    """Pasta do pacote publicado: observações e manifesto de indicadores (ADR-013, ADR-014)."""
    database_url: str | None
    """Conexão com o PostgreSQL dos dados de usuários (ADR-016); nenhum código a usa ainda."""
    dados_dir: Path = Path("output/observatorio")
    manifesto: Path = Path("data/indicadores.json")
    cors_origens: tuple[str, ...] = ()
    certificado_anm: Path | None = None


def carregar() -> Configuracao:
    """Lê a configuração a cada chamada, para que testes e processos possam trocar o ambiente."""
    return Configuracao(
        publicado_dir=Path(os.environ.get("OBS_PUBLICADO_DIR") or PUBLICADO_PADRAO),
        database_url=os.environ.get("DATABASE_URL") or None,
        dados_dir=Path(os.environ.get("OBS_DATA_DIR") or "output/observatorio"),
        manifesto=Path(os.environ.get("OBS_MANIFESTO") or "data/indicadores.json"),
        cors_origens=tuple(o.strip() for o in os.environ.get("OBS_CORS_ORIGENS", "").split(",") if o.strip()),
        certificado_anm=Path(os.environ["OBS_ANM_CA"]) if os.environ.get("OBS_ANM_CA") else None,
    )
