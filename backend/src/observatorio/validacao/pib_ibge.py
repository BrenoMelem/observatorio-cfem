"""Conferência interna do PIB municipal e relatório do lote (RN-FNT-02, RN-VPU-06; exceção de RN-VPU-07/12).

Decisão do mantenedor de 27/11/2026: o SIDRA é a única publicadora do dado, e o lote é homologado sem
referência externa (exceção de RN-VPU-07), condicionado às conferências internas. Em cada município e ano
com todos os componentes, as identidades contábeis têm de fechar dentro do arredondamento do SIDRA (exceção
de RN-VPU-12): meia unidade por valor envolvido, arredondada para baixo — até 2 mil reais em "soma dos quatro
setores = VAB total" e até 1 mil reais em "VAB total + impostos = PIB". Fora disso, as sete observações do
município e ano saem da publicação com o motivo no relatório, sem reprovar o lote.

Ano sem algum componente (2022 e 2023 na edição de dezembro de 2025) não é conferido nas identidades e é
publicado com as lacunas explícitas (RN-MOD-10). VAB negativo é publicado como o IBGE publica. A edição nova
prevalece; os anos cujos valores mudaram em relação ao parcial anterior vão para o relatório.
"""

import hashlib
import json
from collections import defaultdict
from decimal import Decimal

from observatorio.modelo.lote import LotePib, Resultado
from observatorio.modelo.observacao import Observacao

SETORES = ("vab_agropecuaria", "vab_industria", "vab_servicos", "vab_administracao_publica")
TOLERANCIA_SETORES = Decimal(2)  # cinco valores arredondados a mil reais: floor(5 × 0,5)
TOLERANCIA_PIB = Decimal(1)  # três valores: floor(3 × 0,5)


def _digest(observacoes: list[Observacao]) -> str:
    """Impressão digital dos valores de um ano, para detectar revisão de uma edição para outra."""
    pontos = sorted((o.municipio_id or "", str(o.valor), o.natureza_valor) for o in observacoes)
    return hashlib.sha256(json.dumps(pontos).encode()).hexdigest()[:16]


def resumo_edicao(lote: LotePib) -> dict[str, object]:
    """O que identifica a edição: as datas de modificação de cada ano e o SHA-256 da resposta (RN-TMP-02)."""
    return {"periodos": lote.periodos, "arquivo_sha256": lote.sha256}


def _identidades(grupo: dict[str, Observacao]) -> str:
    """Motivo da exclusão, ou texto vazio se fecha; município e ano sem algum componente não é conferido."""
    valores = {i: o.valor for i, o in grupo.items()}
    if any(not isinstance(v, Decimal) for v in valores.values()):
        return ""
    numeros = {i: v for i, v in valores.items() if isinstance(v, Decimal)}
    setores = sum((numeros[s] for s in SETORES), Decimal(0)) - numeros["vab_total"]
    if abs(setores) > TOLERANCIA_SETORES:
        return (
            f"soma dos setores difere do VAB total em {setores} mil reais (tolerância {TOLERANCIA_SETORES})"
        )
    pib = numeros["vab_total"] + numeros["pib_impostos_liquidos"] - numeros["pib_municipal"]
    if abs(pib) > TOLERANCIA_PIB:
        return f"VAB total + impostos difere do PIB em {pib} mil reais (tolerância {TOLERANCIA_PIB})"
    return ""


def validar(lote: LotePib, anterior: dict[str, object] | None = None) -> Resultado:
    """RN-VPU-06: relatório completo; só município e ano com as identidades fechadas são publicáveis."""
    grupos: dict[tuple[str, int], dict[str, Observacao]] = defaultdict(dict)
    for o in lote.observacoes:
        grupos[(o.municipio_id or "", o.ano)][o.indicador] = o
    publicaveis: list[Observacao] = []
    excluidos: list[dict[str, object]] = []
    conferidos = sem_componentes = 0
    for (municipio, ano), grupo in sorted(grupos.items()):
        motivo = _identidades(grupo)
        if motivo:
            excluidos.append({"municipio_id": municipio, "ano": ano, "motivo": motivo})
            continue
        if all(isinstance(o.valor, Decimal) for o in grupo.values()):
            conferidos += 1
        else:
            sem_componentes += 1
        publicaveis.extend(o.model_copy(update={"estado_validacao": "validado"}) for o in grupo.values())
    por_ano: dict[str, dict[int, list[Observacao]]] = defaultdict(lambda: defaultdict(list))
    for o in publicaveis:
        por_ano[o.indicador][o.ano].append(o)
    resumo_anos = {
        indicador: {str(ano): _digest(pontos) for ano, pontos in sorted(anos.items())}
        for indicador, anos in sorted(por_ano.items())
    }
    anteriores = anterior.get("resumo_anos") if anterior else None
    alterados = sorted(
        f"{indicador}:{ano}"
        for indicador, anos in resumo_anos.items()
        for ano, digest in anos.items()
        if isinstance(anteriores, dict)
        and isinstance(anteriores.get(indicador), dict)
        and anteriores[indicador].get(ano) not in (None, digest)
    )
    naturezas: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for o in publicaveis:
        naturezas[o.indicador][o.natureza_valor] += 1
    erros = (
        []
        if any(o.indicador == "pib_municipal" and o.valor is not None for o in publicaveis)
        else ["Nenhum PIB municipal publicável (RN-VPU-06)"]
    )
    relatorio: dict[str, object] = {
        "situacao": "reprovado" if erros else "aprovado",
        "fonte": "IBGE SIDRA, agregado 5938 (PIB dos Municípios)",
        "referencia_externa": None,
        "homologacao": "Fonte oficial única, sem referência externa; conferências internas (exceção de "
        "RN-VPU-07 de 27/11/2026)",
        "arquivo_url": lote.origem,
        "arquivo_sha256": lote.sha256,
        "periodos": lote.periodos,
        "coletado_em": lote.coletado_em,
        "filtros": lote.filtros,
        "linhas_lidas": len(lote.observacoes),
        "linhas_publicaveis": len(publicaveis),
        "conferencia": {
            "municipio_ano_com_identidades_fechadas": conferidos,
            "municipio_ano_sem_todos_os_componentes": sem_componentes,
            "municipio_ano_excluidos": len(excluidos),
        },
        "naturezas": {i: dict(sorted(n.items())) for i, n in sorted(naturezas.items())},
        "negativos": sorted(
            f"{o.indicador}:{o.municipio_id}:{o.ano}"
            for o in publicaveis
            if isinstance(o.valor, Decimal) and o.valor < 0
        ),
        "excluidos": excluidos,
        "anos_alterados": alterados,
        "resumo_anos": resumo_anos,
        "tolerancia": {"setores_vab": str(TOLERANCIA_SETORES), "vab_impostos_pib": str(TOLERANCIA_PIB)},
        "erros": erros,
    }
    return Resultado(
        aprovado=not erros,
        observacoes=tuple(publicaveis),
        erros=tuple(erros),
        relatorio=relatorio,
    )
