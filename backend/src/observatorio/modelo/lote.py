"""Contratos entre fonte e validação: RN-FON-13/14 e RN-VPU-06."""

from dataclasses import dataclass
from pathlib import Path

from observatorio.modelo.observacao import Observacao


@dataclass(frozen=True)
class Lote:
    observacoes: tuple[Observacao, ...]
    bruto: Path
    sha256: str
    coletado_em: str
    origem: str
    linhas_lidas: int
    linhas_recorte: int
    duplicatas: int
    registros_municipais: dict[str, int]
    registros_mensais: dict[str, int]
    totais_nacionais: dict[str, str]
    filtros: dict[str, object]
