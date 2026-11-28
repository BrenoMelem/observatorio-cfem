"""Observação comum (RN-MOD-03/12, RN-MOD-19); dinheiro decimal (RN-CFE-11); categoria opcional (RN-MOD-03)."""

import math
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Observacao(BaseModel):
    """Uma observação no esquema comum (RN-MOD-03): um valor de um indicador num território e período."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "indicador": "cfem_arrecadada",
                    "municipio_id": "1505536",
                    "municipio_nome": "Parauapebas",
                    "nivel_territorial": "município",
                    "ano": 2025,
                    "mes": 1,
                    "valor": "120784171.37",
                    "unidade": "BRL nominal",
                    "natureza_valor": "informado",
                    "estado_validacao": "validado",
                    "fonte": "ANM, CFEM_Arrecadacao.csv",
                    "edicao_fonte": "54b112bef22b4bfc8e9d0cf02b3119d93a5969b948c7b1b0e02c65c9a7c3ca7f",
                    "atualizado_em": "2026-11-25T11:44:04.724818+00:00",
                    "versao_tratamento": "1.0.0",
                }
            ]
        },
    )
    indicador: str = Field(description="Identificador do indicador no manifesto (RN-MOD-25).")
    municipio_id: str | None = Field(
        description="Código IBGE de 7 dígitos; nulo nos níveis RI e global (RN-TER, RN-MOD-19)."
    )
    municipio_nome: str | None = Field(description="Nome do município; nulo nos níveis RI e global.")
    nivel_territorial: Literal["município", "RI", "global"] = Field(
        description=(
            "Município, a Região de Integração ou `global`: série internacional sem recorte territorial, "
            "como o preço de commodity (RN-MOD-03, exceção de 21/11/2026; RN-MOD-19)."
        )
    )
    ano: int = Field(description="Ano de referência do valor.")
    mes: int | None = Field(description="Mês de 1 a 12; nulo em séries anuais e nos totais anuais.")
    valor: Decimal | float | None = Field(
        description=(
            'Valor do indicador. Dinheiro sai como texto decimal (por exemplo, "120784171.37") para não '
            "perder centavos (RN-CFE-11). Nulo quando a natureza não é `informado` nem `zero real`."
        )
    )
    unidade: str = Field(description="Unidade do valor, por exemplo `BRL nominal` ou `pessoas`.")
    natureza_valor: Literal["informado", "zero real", "ausente", "não divulgado", "não aplicável"] = Field(
        description="Distingue zero real de ausência; ausência nunca vira zero (RN-MOD-12)."
    )
    estado_validacao: Literal["validado", "provisório"] = Field(
        description=(
            "`validado` em ano fechado; `provisório` nos meses conferidos do ano ainda aberto, que ainda não "
            "somam total anual (RN-CFE-06, RN-VPU-10)."
        )
    )
    fonte: str = Field(description="Fonte do dado.")
    edicao_fonte: str | None = Field(
        description="Edição da fonte; na CFEM, o SHA-256 do arquivo bruto lido (RN-FON-13)."
    )
    atualizado_em: str | None = Field(description="Data ISO 8601 da coleta.")
    versao_tratamento: str = Field(description="Versão do tratamento que gerou a observação.")
    categoria: str | None = Field(
        default=None,
        description=(
            "Código da categoria dentro do indicador, quando houver (RN-MOD-03, exceção de 25/11/2026): na "
            "despesa por função, `12` (função), `12.361` (subfunção), `12.demais` (Demais Subfunções) ou "
            "`total`. Nulo nos indicadores sem categoria."
        ),
        examples=["12.361"],
    )
    categoria_nome: str | None = Field(
        default=None,
        description="Nome da categoria como a fonte o publica, por exemplo `Ensino Fundamental`.",
        examples=["Ensino Fundamental"],
    )

    @model_validator(mode="after")
    def conferir_valor(self) -> "Observacao":
        if self.unidade.startswith("BRL") and self.valor is not None:
            self.valor = Decimal(str(self.valor))  # RN-CFE-11: dinheiro nunca em float
        if self.valor is not None and not math.isfinite(self.valor):
            raise ValueError("Valor deve ser finito")
        if self.natureza_valor == "informado" and (self.valor is None or self.valor == 0):
            raise ValueError("Valor informado deve ser diferente de zero")
        if self.natureza_valor == "zero real" and self.valor != 0:
            raise ValueError("Zero real exige valor zero")
        if self.natureza_valor in {"ausente", "não divulgado", "não aplicável"} and self.valor is not None:
            raise ValueError("Valor indisponível deve ser nulo")
        if self.mes is not None and not 1 <= self.mes <= 12:
            raise ValueError("Mês inválido")
        if self.nivel_territorial == "global" and (self.municipio_id or self.municipio_nome):
            raise ValueError("Série global não leva município (RN-MOD-19)")
        if (self.categoria is None) != (self.categoria_nome is None):
            raise ValueError("Categoria e nome da categoria vêm juntos")
        return self
