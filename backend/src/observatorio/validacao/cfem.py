"""Homologação por recorte mensal e relatório auditável (RN-VPU-01 a 12)."""

from datetime import date
from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from observatorio.modelo.lote import Lote, Resultado
from observatorio.modelo.observacao import Observacao
from observatorio.modelo.territorios import MUNICIPIOS

__all__ = ["Referencia", "ReferenciaNacional", "Resultado", "validar"]


class Referencia(BaseModel):
    """Valor transcrito de publicação independente; proveniência revisável (RN-VPU-07)."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    municipio_id: str = Field(pattern=r"^\d{7}$")
    ano: int = Field(ge=2003, le=2100)
    mes: int = Field(ge=1, le=12)
    valor: Decimal = Field(allow_inf_nan=False, decimal_places=2)
    documento: str = Field(min_length=1)
    url: str = Field(pattern=r"^https://(?:sistemas\.anm\.gov\.br|www\.gov\.br/anm)/")
    consultado_em: date
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    tipo: Literal["publicacao_oficial_independente"] = "publicacao_oficial_independente"


class ReferenciaNacional(BaseModel):
    """Total anual publicado pela ANM para o controle RN-CFE-12."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    ano: int = Field(ge=2003, le=2100)
    valor: Decimal = Field(gt=0, allow_inf_nan=False, decimal_places=2)
    documento: str = Field(min_length=1)
    url: str = Field(pattern=r"^https://sistemas\.anm\.gov\.br/")
    consultado_em: date
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


def validar(
    lote: Lote,
    referencias: list[Referencia],
    anterior: dict[str, object] | None = None,
    referencias_nacionais: list[ReferenciaNacional] | None = None,
) -> Resultado:
    """RN-VPU-07/12: nenhum valor é validado sem comparação exata da mesma chave.

    Recortes não cobertos pela referência ficam fora da publicação. Uma divergência
    no recorte solicitado reprova o lote inteiro (RN-VPU-01).

    RN-CFE-06 (decisão do mantenedor de 25/11/2026 sobre a aplicação): no último ano do arquivo,
    os meses posteriores ao último mês com registro ainda não aconteceram e não contam como
    ausentes. Um mês conferido desse ano sai "provisório" se o ano não tem os 12 meses com volume
    suficiente; um mês abaixo do critério de volume fica fora da publicação, sem reprovar o lote.
    """
    erros: list[str] = []
    comparacoes: list[dict[str, object]] = []
    aprovadas: list[Observacao] = []
    por_chave = {(o.municipio_id, o.ano, o.mes): o for o in lote.observacoes}
    if len(por_chave) != len(lote.observacoes):
        erros.append("Observações agregadas duplicadas")
    if not referencias:
        erros.append("Sem publicação oficial independente para reconciliar (RN-VPU-07)")
    chaves_referencia: set[tuple[str, int, int]] = set()
    controle_nacional: list[dict[str, object]] = []
    anos = sorted({o.ano for o in lote.observacoes})
    ultimo_ano = max(anos, default=0)
    meses_ausentes = {
        str(ano): [m for m in range(1, 13) if not lote.registros_mensais.get(f"{ano}:{m}")] for ano in anos
    }
    if ultimo_ano:
        presentes = [m for m in range(1, 13) if lote.registros_mensais.get(f"{ultimo_ano}:{m}")]
        ultimo_mes = max(presentes, default=0)
        meses_ausentes[str(ultimo_ano)] = [m for m in meses_ausentes[str(ultimo_ano)] if m < ultimo_mes]
    historico = [
        n for periodo, n in lote.registros_mensais.items() if int(periodo.split(":")[0]) < ultimo_ano
    ]
    limite_volume = median(historico) * 0.5 if historico else 0

    def volume_suficiente(ano: int, mes: int) -> bool:
        """RN-CFE-06, exceção de 08/11/2026: no último ano, mês completo tem ao menos 50% da mediana."""
        volume = lote.registros_mensais.get(f"{ano}:{mes}", 0)
        return ano != ultimo_ano or (volume > 0 and volume >= limite_volume)

    ano_aberto = bool(ultimo_ano) and not all(volume_suficiente(ultimo_ano, m) for m in range(1, 13))
    aguardando_volume: list[str] = []
    for referencia in referencias:
        chave = (referencia.municipio_id, referencia.ano, referencia.mes)
        if chave in chaves_referencia:
            erros.append(f"Referência duplicada: {chave}")
            continue
        chaves_referencia.add(chave)
        item = por_chave.get(chave)
        if referencia.municipio_id not in MUNICIPIOS or item is None or item.valor is None:
            erros.append(f"Referência sem observação correspondente: {chave}")
            continue
        diferenca = Decimal(str(item.valor)) - referencia.valor
        comparacoes.append(
            {
                "municipio_id": chave[0],
                "ano": chave[1],
                "mes": chave[2],
                "calculado": str(item.valor),
                "referencia": str(referencia.valor),
                "diferenca": str(diferenca),
                "documento": referencia.model_dump(mode="json"),
            }
        )
        if diferenca != 0:
            erros.append(f"Reconciliação divergente em {chave}: {diferenca} BRL")
        elif meses_ausentes.get(str(item.ano)):
            erros.append(f"Ano {item.ano} com mês nacional ausente: somente provisório, fora da demo")
        elif not volume_suficiente(item.ano, referencia.mes):
            aguardando_volume.append(f"{chave[0]}:{chave[1]}:{chave[2]}")
        else:
            estado = "provisório" if ano_aberto and item.ano == ultimo_ano else "validado"
            aprovadas.append(item.model_copy(update={"estado_validacao": estado}))
    if referencias_nacionais is not None:
        por_ano: dict[int, ReferenciaNacional] = {}
        for referencia_nacional in referencias_nacionais:
            if referencia_nacional.ano in por_ano:
                erros.append(f"Referência nacional duplicada: {referencia_nacional.ano} (RN-CFE-12)")
                continue
            por_ano[referencia_nacional.ano] = referencia_nacional
        for ano in sorted({r.ano for r in referencias if r.ano < date.today().year}):
            total_oficial = por_ano.get(ano)
            calculado = lote.totais_nacionais.get(str(ano))
            if total_oficial is None or calculado is None:
                erros.append(f"Sem total nacional para {ano} (RN-CFE-12)")
                continue
            diferenca = Decimal(calculado) - total_oficial.valor
            percentual = abs(diferenca) / total_oficial.valor
            controle_nacional.append(
                {
                    "ano": ano,
                    "calculado": calculado,
                    "referencia": str(total_oficial.valor),
                    "diferenca": str(diferenca),
                    "percentual": str(percentual),
                    "documento": total_oficial.model_dump(mode="json"),
                }
            )
            if percentual > Decimal("0.01"):
                erros.append(f"Total nacional diverge mais de 1% em {ano} (RN-CFE-12)")
    if anterior:
        for campo in ("totais_nacionais", "registros_municipais"):
            antigos = anterior.get(campo, {})
            novos = lote.totais_nacionais if campo == "totais_nacionais" else lote.registros_municipais
            if isinstance(antigos, dict):
                for periodo, valor in antigos.items():
                    ano = int(str(periodo).split(":")[-1])
                    limite = Decimal(".98") if campo == "totais_nacionais" else Decimal(1)
                    if (
                        ano < date.today().year
                        and Decimal(str(novos.get(str(periodo), 0))) < Decimal(str(valor)) * limite
                    ):
                        erros.append(f"Série encolheu em {campo}/{periodo} (RN-VPU-02)")
    valores = [o.valor for o in lote.observacoes if o.valor is not None]
    relatorio: dict[str, object] = {
        "situacao": "reprovado" if erros or not aprovadas else "aprovado",
        "sha256_bruto": lote.sha256,
        "origem": lote.origem,
        "coletado_em": lote.coletado_em,
        "filtros": lote.filtros,
        "linhas_lidas": lote.linhas_lidas,
        "linhas_recorte": lote.linhas_recorte,
        "duplicatas": lote.duplicatas,
        "municipios_presentes": sorted({o.municipio_id for o in lote.observacoes if o.municipio_id}),
        "anos": anos,
        "nulos": sum(o.valor is None for o in lote.observacoes),
        "faixa_valores": {
            "minimo": str(min(valores)) if valores else None,
            "maximo": str(max(valores)) if valores else None,
        },
        "meses_nacionais_ausentes": meses_ausentes,
        "ausencias_municipais": [
            f"{c}:{a}:{m}"
            for a in anos
            for m in range(1, 13)
            for c in MUNICIPIOS
            if (c, a, m) not in por_chave
        ],
        "causa_ausencias": "não confirmada; ausência não equivale a zero",
        "totais_nacionais": lote.totais_nacionais,
        "registros_municipais": lote.registros_municipais,
        "reconciliacao": comparacoes,
        "controle_nacional": controle_nacional,
        "erros": erros,
        "observacoes_sem_referencia": len(por_chave.keys() - chaves_referencia),
        "ano_aberto": ultimo_ano if ano_aberto else None,
        "provisorias": sum(o.estado_validacao == "provisório" for o in aprovadas),
        "aguardando_volume": aguardando_volume,
    }
    aprovado = not erros and bool(aprovadas)
    return Resultado(aprovado, tuple(aprovadas) if aprovado else (), tuple(erros), relatorio)
