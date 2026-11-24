"""Observação comum (RN-MOD-03/12); dinheiro decimal (RN-CFE-11)."""

import math
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class Observacao(BaseModel):
    model_config = ConfigDict(extra="forbid")
    indicador: str
    municipio_id: str | None
    municipio_nome: str | None
    nivel_territorial: Literal["município", "RI"]
    ano: int
    mes: int | None
    valor: Decimal | float | None
    unidade: str
    natureza_valor: Literal["informado", "zero real", "ausente", "não divulgado", "não aplicável"]
    estado_validacao: Literal["validado", "provisório"]
    fonte: str
    edicao_fonte: str | None
    atualizado_em: str | None
    versao_tratamento: str

    @model_validator(mode="after")
    def conferir_valor(self) -> "Observacao":
        if self.indicador == "cfem_arrecadada" and self.valor is not None:
            self.valor = Decimal(str(self.valor))
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
        return self
