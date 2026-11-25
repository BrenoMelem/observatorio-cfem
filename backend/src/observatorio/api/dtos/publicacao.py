"""Contratos públicos da camada publicada (RN-MOD-03)."""

from typing import Literal

from pydantic import BaseModel

from observatorio.modelo.observacao import Observacao

__all__ = ["Metadados", "Observacao", "RespostaDimensao", "StatusIndicador"]


class Metadados(BaseModel):
    fonte: str
    edicao: str | None = None
    metodo: str
    limitacoes: str


class StatusIndicador(BaseModel):
    indicador: str
    situacao: Literal["publicado", "sem_dado_validado"]
    motivo: str | None = None
    ano_referencia: int | None = None
    atualizado_em: str | None = None
    metadados: Metadados


class RespostaDimensao(BaseModel):
    filtros: dict[str, str | int | None]
    versao_dados: str | None
    notas: list[str]
    dados: list[Observacao]
    status: list[StatusIndicador]
    metadados: dict[str, Metadados]
    lacunas: list[str]
