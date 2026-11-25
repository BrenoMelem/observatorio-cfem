"""Contrato do pacote imutável (ADR-014, RN-VPU-01/03)."""

import hashlib
import json

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ArquivoIndicador(BaseModel):
    model_config = ConfigDict(extra="forbid")
    arquivo: str = Field(pattern=r"^[a-z_]+\.parquet$")
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    ano_referencia: int
    atualizado_em: str


class DescricaoPacote(BaseModel):
    model_config = ConfigDict(extra="forbid")
    versao: str = Field(pattern=r"^[a-f0-9]{64}$")
    gerado_em: str
    arquivos: dict[str, str]
    indicadores: dict[str, ArquivoIndicador]

    @model_validator(mode="after")
    def conferir(self) -> "DescricaoPacote":
        """RN-VPU-01: nomes relativos seguros e hashes coerentes."""
        for nome, resumo in self.arquivos.items():
            if "/" in nome or "\\" in nome or nome in (".", "..") or not nome:
                raise ValueError("Nome de arquivo inválido no pacote")
            if len(resumo) != 64 or any(c not in "0123456789abcdef" for c in resumo):
                raise ValueError("Hash inválido no pacote")
        for indicador, item in self.indicadores.items():
            if item.arquivo != indicador + ".parquet" or self.arquivos.get(item.arquivo) != item.sha256:
                raise ValueError("Indicador inconsistente com arquivos do pacote")
        if not {"indicadores.json", "consumo_assistente.json"} <= self.arquivos.keys():
            raise ValueError("Pacote sem manifestos obrigatórios")
        if self.versao != calcular_versao(self.arquivos, self.indicadores):
            raise ValueError("Versão do pacote incoerente")
        return self


def calcular_versao(arquivos: dict[str, str], indicadores: dict[str, ArquivoIndicador]) -> str:
    conteudo = {"arquivos": arquivos, "indicadores": {k: v.model_dump() for k, v in indicadores.items()}}
    return hashlib.sha256(json.dumps(conteudo, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
