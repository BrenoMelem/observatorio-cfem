"""Contratos públicos da camada publicada (RN-MOD-03), descritos no OpenAPI para o front."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from observatorio.modelo.observacao import Observacao

__all__ = ["Erro", "Metadados", "Observacao", "RespostaDimensao", "Saude", "StatusIndicador"]


class Metadados(BaseModel):
    """Proveniência de um indicador, tirada do manifesto publicado (RN-MOD-25, RN-VPU-09)."""

    fonte: str = Field(description="Fonte do dado, como consta no manifesto de indicadores.")
    edicao: str | None = Field(
        default=None,
        description="Edição mais recente da fonte entre as observações publicadas; nula sem publicação.",
    )
    metodo: str = Field(description="Como o valor foi calculado a partir da fonte.")
    limitacoes: str = Field(description="O que o valor não diz e cuidados de leitura.")


class StatusIndicador(BaseModel):
    """Situação de publicação de um indicador (RN-ENT-04)."""

    indicador: str = Field(
        description="Identificador do indicador no manifesto.", examples=["cfem_arrecadada"]
    )
    situacao: Literal["publicado", "sem_dado_validado"] = Field(
        description="`publicado` quando há observação validada no pacote; `sem_dado_validado` caso contrário."
    )
    motivo: str | None = Field(
        default=None, description="Por que o indicador não tem publicação; nulo quando publicado."
    )
    ano_referencia: int | None = Field(default=None, description="Ano mais recente publicado.")
    atualizado_em: str | None = Field(
        default=None, description="Data ISO 8601 da coleta mais recente publicada."
    )
    metadados: Metadados


class RespostaDimensao(BaseModel):
    """Envelope híbrido da Fase 1: filtros, observações, status, metadados e lacunas (ADR-010, RN-MOD-03)."""

    filtros: dict[str, str | int | None] = Field(description="Os filtros aplicados, ecoados na resposta.")
    versao_dados: str | None = Field(
        description="Versão do pacote publicado lido (hash). Igual em todas as rotas enquanto o pacote não muda."
    )
    notas: list[str] = Field(description="Avisos de leitura, inclusive anos omitidos na periodicidade anual.")
    dados: list[Observacao] = Field(
        description="Observações validadas no recorte. Lista vazia não significa valor zero (RN-CFE-07)."
    )
    status: list[StatusIndicador] = Field(description="Situação de cada indicador da dimensão.")
    metadados: dict[str, Metadados] = Field(description="Proveniência de cada indicador da dimensão.")
    lacunas: list[str] = Field(description="Temas da dimensão que ainda não têm publicação homologada.")


class Saude(BaseModel):
    """Estado do pacote publicado lido pela API (RN-ENT-01)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"estado": "pronto"}, {"estado": "publicacao_invalida", "motivo": "…"}]
        }
    )

    estado: Literal["pronto", "sem_publicacao", "publicacao_invalida"] = Field(
        description=(
            "`pronto`: manifesto e ao menos uma observação publicada válidos. "
            "`sem_publicacao`: manifesto válido, sem observação. "
            "`publicacao_invalida`: pacote ilegível ou com hash divergente; ver `motivo`."
        )
    )
    motivo: str | None = Field(default=None, description="Presente só em `publicacao_invalida`.")


class Erro(BaseModel):
    """Corpo dos erros 404 e 503."""

    detail: str = Field(description="Mensagem do erro.", examples=["Dimensão desconhecida"])
