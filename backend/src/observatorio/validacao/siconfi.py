"""Conferência da despesa por função com o RREO e a MSC, e relatório do lote (RN-FNT-04, RN-VPU-06/07/12).

Decisão do mantenedor de 25/11/2026 (RN-FNT-04): a empenhada e a liquidada da DCA são conferidas com o RREO
Anexo 2 do 6º bimestre, e a paga com a MSC de dezembro, ao centavo (RN-VPU-12). A unidade é o município, o
exercício e o estágio: só é homologado o que coincide no total e em todas as linhas (funções, subfunções e
"Demais Subfunções"). O que não coincide, ou não tem referência, fica fora da publicação com o motivo, sem
reprovar o lote. O fechamento da DCA (soma das funções igual ao total) reprova o lote (RN-FNT-04).
"""

import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from observatorio.modelo.lote import Entrega, LinhaReferencia, LoteDespesa, Resultado
from observatorio.modelo.observacao import Observacao
from observatorio.modelo.territorios import MUNICIPIOS

ESTAGIOS = ("empenhada", "liquidada", "paga")
ZERO = Decimal(0)


def _normalizar(texto: str) -> str:
    """Sem acento, caixa, espaço nem pontuação, para casar nomes de publicações diferentes."""
    return "".join(c for c in unicodedata.normalize("NFKD", texto).lower() if c.isalnum())


class Grupo:
    """As linhas da DCA de um município, exercício e estágio, por categoria."""

    def __init__(self, observacoes: list[Observacao]) -> None:
        self.observacoes = observacoes
        self.valores: dict[str, Decimal] = {}
        self.nomes: dict[str, str] = {}
        for o in observacoes:
            assert o.categoria is not None and o.categoria_nome is not None and o.valor is not None
            self.valores[o.categoria] = Decimal(str(o.valor))
            self.nomes[o.categoria] = o.categoria_nome

    def funcoes(self) -> list[str]:
        return [c for c in self.valores if c.isdigit()]

    def subfuncoes(self, funcao: str) -> list[str]:
        return [c for c in self.valores if c.startswith(funcao + ".") and c[3:].isdigit()]


def fechamento(grupo: Grupo) -> str | None:
    """RN-FNT-04: a soma das funções fecha com "Despesas (Exceto Intraorçamentárias)"; senão, o erro."""
    total = grupo.valores.get("total")
    if total is None:
        return "sem a linha de total"
    soma = sum((grupo.valores[f] for f in grupo.funcoes()), ZERO)
    return None if soma == total else f"soma das funções {soma} diferente do total {total}"


def mapear_rreo(linhas: list[LinhaReferencia], grupo: Grupo) -> tuple[dict[str, Decimal], list[str]]:
    """Leva as linhas do RREO (sem código) às categorias da DCA do mesmo município e exercício.

    Função e subfunção são reconhecidas pelo nome, sem acento nem pontuação ("Infra-Estrutura" e
    "Infraestrutura" coincidem); "FUxx - Administração Geral" é a subfunção xx.122. O que o RREO lista
    e a DCA agrupa em "Demais Subfunções" soma no resíduo `FF.demais` da função.
    """
    por_nome_funcao = {_normalizar(grupo.nomes[f]): f for f in grupo.funcoes()}
    por_nome_sub = {f: {_normalizar(grupo.nomes[s]): s for s in grupo.subfuncoes(f)} for f in grupo.funcoes()}
    saida: dict[str, Decimal] = defaultdict(Decimal)
    problemas: list[str] = []
    atual: str | None = None
    for linha in linhas:
        conta = linha.conta.strip()
        chave = _normalizar(conta)
        if chave.startswith("despesasexcetointra"):
            saida["total"] += linha.valor
            continue
        if chave.startswith(("despesasintra", "totaliii")):
            continue
        if conta.startswith("FU") and conta[2:4].isdigit() and " - " in conta:
            atual = conta[2:4]
            resto = _normalizar(conta.split(" - ", 1)[1])
            destino = por_nome_sub.get(atual, {}).get(resto, f"{atual}.demais")
            saida[destino] += linha.valor
            continue
        if chave in por_nome_funcao:
            atual = por_nome_funcao[chave]
            if atual in saida:
                problemas.append(f"função repetida no RREO: {conta}")
            saida[atual] += linha.valor
            continue
        if atual is None:
            problemas.append(f"linha do RREO fora de função: {conta}")
            continue
        saida[por_nome_sub.get(atual, {}).get(chave, f"{atual}.demais")] += linha.valor
    return dict(saida), problemas


def referencia_msc(msc: dict[str, Decimal], grupo: Grupo) -> dict[str, Decimal]:
    """MSC por função e subfunção → as categorias da DCA; "Demais" é a função menos as listadas."""
    saida: dict[str, Decimal] = {}
    funcoes_msc = {c for c in msc if "." not in c}
    saida["total"] = sum((msc[f] for f in funcoes_msc), ZERO)
    for f in funcoes_msc:
        saida[f] = msc[f]
        listadas = ZERO
        for s in grupo.subfuncoes(f):
            if s in msc:
                saida[s] = msc[s]
                listadas += msc[s]
        saida[f"{f}.demais"] = msc[f] - listadas
    return saida


def comparar(grupo: Grupo, referencia: dict[str, Decimal]) -> list[str]:
    """RN-VPU-12: cada categoria da DCA igual à da referência, ao centavo; e nada sobrando na referência."""
    diferencas: list[str] = []
    for categoria, valor in grupo.valores.items():
        outro = referencia.get(categoria)
        if outro is None:
            diferencas.append(f"{categoria}: {valor} na DCA, ausente na referência")
        elif outro != valor:
            diferencas.append(f"{categoria}: {valor} na DCA, {outro} na referência")
    for categoria, valor in referencia.items():
        if categoria not in grupo.valores and valor != 0:
            diferencas.append(f"{categoria}: ausente na DCA, {valor} na referência")
    return diferencas


def resumo_entregas(entregas: Iterable[Entrega]) -> dict[str, list[str]]:
    """`município:ano` → entregas `entregável|período|status|data`, para comparar coletas (RN-TMP-04)."""
    saida: dict[str, list[str]] = defaultdict(list)
    for e in entregas:
        saida[f"{e.municipio_id}:{e.ano}"].append(f"{e.entregavel}|{e.periodo}|{e.status}|{e.data_status}")
    return {k: sorted(v) for k, v in sorted(saida.items())}


def entregas_alteradas(entregas: Iterable[Entrega], anterior: dict[str, object] | None) -> list[str]:
    """RN-TMP-04: município e exercício cuja entrega mudou desde a coleta anterior."""
    if not anterior or not isinstance(anterior.get("entregas"), dict):
        return []
    antigas = anterior["entregas"]
    assert isinstance(antigas, dict)
    atuais = resumo_entregas(entregas)
    return sorted(
        chave
        for chave in set(antigas) | set(atuais)
        if sorted(antigas.get(chave, [])) != sorted(atuais.get(chave, []))
    )


def validar(lote: LoteDespesa, anterior: dict[str, object] | None = None) -> Resultado:
    """RN-FNT-04, RN-VPU-07/12: só sai o município-exercício-estágio que coincide com a referência."""
    erros: list[str] = []
    grupos: dict[tuple[str, int, str], list[Observacao]] = defaultdict(list)
    for o in lote.observacoes:
        assert o.municipio_id is not None
        grupos[(o.municipio_id, o.ano, o.indicador.removeprefix("despesa_funcao_"))].append(o)
    rreo: dict[tuple[str, int, str], list[LinhaReferencia]] = defaultdict(list)
    for linha in lote.rreo:
        rreo[(linha.municipio_id, linha.ano, linha.estagio)].append(linha)
    aprovadas: list[Observacao] = []
    conferidos: list[str] = []
    fora: list[dict[str, object]] = []
    repetidas = 0
    for chave, observacoes in sorted(grupos.items()):
        codigo, ano, estagio = chave
        rotulo = f"{codigo}:{ano}:{estagio}"
        categorias = [o.categoria for o in observacoes]
        if len(categorias) != len(set(categorias)):
            repetidas += len(categorias) - len(set(categorias))
            erros.append(f"Linhas repetidas na DCA em {rotulo} (RN-VPU-11)")
            continue
        grupo = Grupo(observacoes)
        problema = fechamento(grupo)
        if problema:
            erros.append(f"Fechamento da DCA falhou em {rotulo}: {problema} (RN-FNT-04)")
            continue
        if estagio == "paga":
            msc = lote.msc.get((codigo, ano))
            if not msc:
                fora.append({"chave": rotulo, "motivo": "sem MSC de dezembro na API (sem referência)"})
                continue
            referencia, problemas = referencia_msc(msc, grupo), list[str]()
            nome_referencia = "MSC de dezembro"
        else:
            linhas = rreo.get(chave)
            if not linhas:
                fora.append(
                    {"chave": rotulo, "motivo": "sem RREO Anexo 2 do 6º bimestre na API (sem referência)"}
                )
                continue
            referencia, problemas = mapear_rreo(linhas, grupo)
            nome_referencia = "RREO Anexo 2"
        diferencas = problemas + comparar(grupo, referencia)
        if diferencas:
            fora.append(
                {
                    "chave": rotulo,
                    "motivo": f"diverge do {nome_referencia} em {len(diferencas)} linha(s)",
                    "diferencas": diferencas[:20],
                }
            )
            continue
        conferidos.append(rotulo)
        aprovadas.extend(o.model_copy(update={"estado_validacao": "validado"}) for o in observacoes)
    presentes = {(o.municipio_id, o.ano) for o in lote.observacoes}
    anos_com_dado = sorted({ano for _, ano in presentes})
    resumo: dict[str, dict[str, int]] = {}
    for estagio in ESTAGIOS:
        resumo[estagio] = {
            "com_dca": sum(1 for k in grupos if k[2] == estagio),
            "conferidos": sum(1 for c in conferidos if c.endswith(":" + estagio)),
            "sem_referencia": sum(
                1 for f in fora if str(f["chave"]).endswith(":" + estagio) and "sem " in str(f["motivo"])
            ),
            "divergentes": sum(
                1 for f in fora if str(f["chave"]).endswith(":" + estagio) and "diverge" in str(f["motivo"])
            ),
        }
    valores = [Decimal(str(o.valor)) for o in aprovadas if o.valor is not None]
    relatorio: dict[str, object] = {
        "situacao": "reprovado" if erros or not aprovadas else "aprovado",
        "indicadores": sorted({o.indicador for o in lote.observacoes}),
        "sha256_bruto": lote.sha256,
        "origem": lote.origem,
        "coletado_em": lote.coletado_em,
        "filtros": lote.filtros,
        "respostas": lote.respostas,
        "linhas_lidas": lote.linhas_lidas,
        "linhas_dca": len(lote.observacoes),
        "linhas_intraorcamentarias_fora": lote.intraorcamentarias,
        "duplicatas": repetidas,
        "anos": anos_com_dado,
        "municipios_presentes": sorted({c for c, _ in presentes if c}),
        "ausencias_municipais": [
            f"{c}:{a}"
            for a in lote.anos
            if a <= max(anos_com_dado, default=0)
            for c in MUNICIPIOS
            if (c, a) not in presentes
        ],
        "causa_ausencias": "DCA sem linhas na API; ausência não equivale a zero (RN-MOD-10)",
        "conferencia": resumo,
        "conferidos": conferidos,
        "fora_da_publicacao": fora,
        "entregas": resumo_entregas(lote.entregas),
        "entregas_alteradas": entregas_alteradas(lote.entregas, anterior),
        "faixa_valores": {
            "minimo": str(min(valores)) if valores else None,
            "maximo": str(max(valores)) if valores else None,
        },
        "erros": erros,
    }
    aprovado = not erros and bool(aprovadas)
    return Resultado(aprovado, tuple(aprovadas) if aprovado else (), tuple(erros), relatorio)
