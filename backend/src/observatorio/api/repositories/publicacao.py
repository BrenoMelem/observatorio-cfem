"""Lê exclusivamente o pacote publicado, sem consultar fonte externa (RN-ENT-01)."""
import json
from pathlib import Path

from pydantic import ValidationError

from observatorio import config
from observatorio.api.dtos.publicacao import Observacao

MANIFESTO = "indicadores.json"
CAMPOS_MANIFESTO = ("fonte", "metodo", "limitacoes")


class PublicacaoInvalida(Exception):
    pass


def pasta_publicada() -> Path:
    return config.carregar().publicado_dir


def manifesto_publicado(pasta: Path | None = None) -> dict[str, dict[str, object]]:
    """Manifesto de indicadores (RN-MOD-25), lido de dentro do pacote publicado (ADR-014)."""
    caminho = (pasta or pasta_publicada()) / MANIFESTO
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise PublicacaoInvalida("Pacote publicado sem o manifesto de indicadores") from erro
    except OSError as erro:  # permissão, pasta no lugar do arquivo etc.
        raise PublicacaoInvalida("Manifesto de indicadores ilegível") from erro
    except ValueError as erro:
        raise PublicacaoInvalida("Manifesto de indicadores inválido") from erro
    if not isinstance(bruto, dict) or not all(
        isinstance(d, dict) and all(isinstance(d.get(c), str) for c in CAMPOS_MANIFESTO) for d in bruto.values()
    ):
        raise PublicacaoInvalida("Manifesto de indicadores inválido")
    return bruto


def populacao_publicada(pasta: Path | None = None) -> list[Observacao]:
    caminho = (pasta or pasta_publicada()) / "populacao.json"
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(bruto, list):
            raise PublicacaoInvalida("Publicação de população não é uma lista")
        linhas = [Observacao.model_validate(o) for o in bruto]
        if any(o.indicador != "populacao_estimada" or o.estado_validacao != "validado" for o in linhas):
            raise PublicacaoInvalida("Publicação de população contém indicador ou validação incompatível")
        chaves = [(o.municipio_id, o.ano, o.mes) for o in linhas]
        if len(chaves) != len(set(chaves)):
            raise PublicacaoInvalida("Publicação de população contém duplicatas")
        return linhas
    except FileNotFoundError:
        return []
    except OSError as erro:  # permissão, pasta no lugar do arquivo etc.
        raise PublicacaoInvalida("Publicação de população ilegível") from erro
    except (ValueError, ValidationError) as erro:
        raise PublicacaoInvalida("Publicação de população inválida") from erro
