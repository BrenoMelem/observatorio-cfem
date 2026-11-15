"""Lê exclusivamente o pacote publicado, sem consultar fonte externa (RN-ENT-01)."""
import json
import os
from pathlib import Path

from pydantic import ValidationError

from app.dtos.publicacao import Observacao

RAIZ = Path(__file__).resolve().parents[3]
PUBLICADO = Path(os.getenv("OBS_PUBLICADO_DIR", RAIZ / "output" / "observatorio" / "publicado"))


class PublicacaoInvalida(Exception):
    pass


def populacao_publicada(pasta: Path | None = None) -> list[Observacao]:
    caminho = (pasta or PUBLICADO) / "populacao.json"
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
    except (ValueError, ValidationError) as erro:
        raise PublicacaoInvalida("Publicação de população inválida") from erro
