"""DTOs do assistente; contexto compatível com assistente.js do site."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Tema(BaseModel):
    id: str = Field(max_length=60)
    titulo: str = Field(max_length=120)


class Grafico(BaseModel):
    i: int = Field(ge=0, le=100)
    titulo: str = Field(max_length=160)
    tipo: str = Field(max_length=40)
    real: bool


class Contexto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pagina: Literal["social", "economica", "ambiental", "institucional"]
    dimensao: str = Field(max_length=80)
    tema: Tema
    periodo: tuple[int, int]
    comparacoes: list[str] = Field(max_length=12)
    graficos: list[Grafico] = Field(max_length=60)


class Pergunta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pergunta: str = Field(min_length=3, max_length=500)
    contexto: Contexto
    historico: list[str] = Field(default_factory=list, max_length=5)


class Citacao(BaseModel):
    indicador: str
    fonte: str
    periodo: str
    edicao: str | None


class Acao(BaseModel):
    tipo: Literal["restaurar", "definirPeriodo", "definirSeries", "escolherTema", "destacar", "irPara"]
    de: int | None = None
    ate: int | None = None
    tema: str | None = None
    i: int | None = None
    nomes: list[str] | None = None
    pagina: Literal["social", "economica", "ambiental", "institucional"] | None = None


class Resposta(BaseModel):
    resposta: str
    citacoes: list[Citacao]
    limitacoes: list[str]
    acoes: list[Acao]
