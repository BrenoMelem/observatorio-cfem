"""Conferência dos preços do Pink Sheet com a planilha anual e relatório do lote (RN-FNT-05, RN-VPU-06/07).

Decisão do mantenedor de 27/11/2026 (exceção de RN-VPU-12): a referência é a planilha anual da mesma edição,
e a diferença aceita é menor que 1 unidade da última casa que ela publica (cobre 1 USD/t; ferro 0,1 USD/dmt
e 0,1 ¢/dmtu). Ano fechado e conferido sai `validado`; o ano corrente, ainda incompleto, sai `provisório`
(RN-TMP-12) e não é conferido. O que não pode ser publicado (ano incompleto fora do ano corrente, sem
referência ou divergente) fica fora com o motivo, sem reprovar o lote; reprova o lote o indicador que
ficar sem nenhuma observação. Uma edição nova que corrija um ano já publicado prevalece se passar na
conferência, e a mudança vai para o relatório (`anos_alterados`).
"""

import hashlib
import json
from collections import defaultdict
from decimal import Decimal

from observatorio.fontes.pink_sheet import IND_COBRE, IND_CONTRATO, IND_SPOT, INDICADORES
from observatorio.modelo.lote import LotePinkSheet, Resultado
from observatorio.modelo.observacao import Observacao

TOLERANCIA = {IND_CONTRATO: Decimal("0.1"), IND_SPOT: Decimal("0.1"), IND_COBRE: Decimal(1)}
MESES_DO_ANO = 12


def _digest(observacoes: list[Observacao]) -> str:
    """Impressão digital dos valores de um ano, para detectar correção de uma edição para outra."""
    pontos = sorted((o.mes or 0, str(o.valor)) for o in observacoes)
    return hashlib.sha256(json.dumps(pontos).encode()).hexdigest()[:16]


def validar(lote: LotePinkSheet, anterior: dict[str, object] | None = None) -> Resultado:
    """RN-VPU-06: relatório completo; só o que foi conferido (ou o ano corrente) é publicável."""
    por_ano: dict[str, dict[int, list[Observacao]]] = {i: defaultdict(list) for i in INDICADORES}
    for o in lote.observacoes:
        por_ano[o.indicador][o.ano].append(o)
    publicaveis: list[Observacao] = []
    excluidos: list[dict[str, object]] = []
    conferencia: dict[str, dict[str, int]] = {}
    resumo_anos: dict[str, dict[str, str]] = {}
    erros: list[str] = []
    for indicador in INDICADORES:
        anos = por_ano[indicador]
        ultimo = max(anos, default=0)
        contagem = {"validados": 0, "provisorios": 0, "excluidos": 0}
        for ano in sorted(anos):
            pontos = anos[ano]
            reais = [o for o in pontos if o.valor is not None]
            esperado = 1 if indicador == IND_CONTRATO else MESES_DO_ANO
            if len(reais) == esperado:
                valores = [Decimal(str(o.valor)) for o in reais]
                valor = sum(valores, Decimal(0)) / len(valores)
                ref = lote.referencia.get((indicador, ano))
                if ref is None:
                    motivo = "sem referência na planilha anual (RN-VPU-07)"
                elif abs(valor - ref) >= TOLERANCIA[indicador]:
                    motivo = f"média {valor:.3f} difere da planilha anual {ref} (tolerância {TOLERANCIA[indicador]})"
                else:
                    motivo = ""
                if motivo:
                    excluidos.append({"indicador": indicador, "ano": ano, "motivo": motivo})
                    contagem["excluidos"] += 1
                    continue
                publicaveis.extend(o.model_copy(update={"estado_validacao": "validado"}) for o in pontos)
                contagem["validados"] += 1
            elif ano == ultimo:
                publicaveis.extend(pontos)  # RN-TMP-12: ano corrente incompleto, provisório e sem média anual
                contagem["provisorios"] += 1
            else:
                excluidos.append(
                    {
                        "indicador": indicador,
                        "ano": ano,
                        "motivo": f"ano incompleto ({len(reais)} de {esperado}) fora do ano corrente (RN-TMP-12)",
                    }
                )
                contagem["excluidos"] += 1
                continue
            resumo_anos.setdefault(indicador, {})[str(ano)] = _digest(pontos)
        conferencia[indicador] = contagem
        if contagem["validados"] + contagem["provisorios"] == 0:
            erros.append(f"{indicador}: nenhum ano publicável (RN-VPU-06)")
    anteriores = anterior.get("resumo_anos") if anterior else None
    alterados = (
        sorted(
            f"{indicador}:{ano}"
            for indicador, anos in resumo_anos.items()
            for ano, digest in anos.items()
            if isinstance(anteriores, dict)
            and isinstance(anteriores.get(indicador), dict)
            and anteriores[indicador].get(ano) not in (None, digest)
        )
        if isinstance(anteriores, dict)
        else []
    )
    relatorio: dict[str, object] = {
        "situacao": "reprovado" if erros else "aprovado",
        "fonte": "World Bank, Pink Sheet",
        "arquivo_url": lote.origem,
        "arquivo_sha256": lote.sha256,
        "referencia_url": lote.origem_anual,
        "referencia_sha256": lote.sha256_anual,
        "coletado_em": lote.coletado_em,
        "filtros": lote.filtros,
        "linhas_lidas": len(lote.observacoes),
        "linhas_publicaveis": len(publicaveis),
        "conferencia": conferencia,
        "excluidos": excluidos,
        "anos_alterados": alterados,
        "resumo_anos": resumo_anos,
        "tolerancia": {i: str(t) for i, t in TOLERANCIA.items()},
        "erros": erros,
    }
    return Resultado(
        aprovado=not erros,
        observacoes=tuple(publicaveis),
        erros=tuple(erros),
        relatorio=relatorio,
    )
