"""Consulta por dimensão e status, preservando ausências como lacunas."""

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal

from observatorio.api.dtos.publicacao import Metadados, Observacao, RespostaDimensao, StatusIndicador
from observatorio.api.repositories.publicacao import (
    PublicacaoInvalida,
    indicadores_publicados,
    manifesto_publicado,
    populacao_publicada,
    resolver_pacote,
)

DIMENSOES = {
    "social": (
        "populacao_estimada",
        "despesa_funcao_empenhada",
        "despesa_funcao_liquidada",
        "despesa_funcao_paga",
    ),
    "economica": (
        "cfem_arrecadada",
        "preco_minerio_ferro_contrato",
        "preco_minerio_ferro_spot",
        "preco_cobre",
        "pib_municipal",
        "pib_impostos_liquidos",
        "vab_total",
        "vab_agropecuaria",
        "vab_industria",
        "vab_servicos",
        "vab_administracao_publica",
        "despesa_funcao_empenhada",
        "despesa_funcao_liquidada",
        "despesa_funcao_paga",
    ),
    "ambiental": ("despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
    "institucional": ("despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
}
MOTIVOS = {
    "cfem_arrecadada": "Lote da API CFEM sem homologação demonstrada para esta camada (RN-VPU-10).",
    "preco_minerio_ferro_contrato": "Série do Pink Sheet sem publicação homologada nesta camada (RN-TMP-13, RN-VPU-07).",
    "preco_minerio_ferro_spot": "Série do Pink Sheet sem publicação homologada nesta camada (RN-TMP-13, RN-VPU-07).",
    "preco_cobre": "Série do Pink Sheet sem publicação homologada nesta camada (RN-FNT-05, RN-VPU-07).",
    **{
        indicador: "PIB dos Municípios do SIDRA sem publicação homologada nesta camada (RN-FNT-02)."
        for indicador in (
            "pib_municipal",
            "pib_impostos_liquidos",
            "vab_total",
            "vab_agropecuaria",
            "vab_industria",
            "vab_servicos",
            "vab_administracao_publica",
        )
    },
}
LACUNAS = {
    "social": [
        "Censo, emprego, educação, saúde, pobreza, segurança, moradia e saneamento: sem publicação homologada nesta camada."
    ],
    "economica": ["Receitas, investimentos e distribuição recebida: sem publicação homologada nesta camada."],
    "ambiental": ["Uso do solo, emissões e saneamento domiciliar: sem publicação homologada nesta camada."],
    "institucional": ["Índices compostos, receita e gestão pública: sem publicação homologada nesta camada."],
}


@dataclass(frozen=True)
class Pacote:
    """O pacote publicado lido uma vez por requisição, para não misturar versões se ele for trocado no meio."""

    definicoes: dict[str, dict[str, object]]
    populacao: list[Observacao]
    versao: str
    consumo: dict[str, dict[str, object]] | None = None


def ler_pacote(pasta: Path | None = None) -> Pacote:
    pasta, descricao = resolver_pacote(pasta)
    definicoes = manifesto_publicado(pasta)
    populacao = populacao_publicada(pasta)
    if descricao:
        populacao.extend(indicadores_publicados(pasta, descricao))
        try:
            consumo = json.loads((pasta / "consumo_assistente.json").read_bytes())
            if not isinstance(consumo, dict) or any(
                not isinstance(v, dict)
                or type(v.get("habilitado")) is not bool
                or not isinstance(v.get("motivo"), str)
                for v in consumo.values()
            ):
                raise ValueError("Controle inválido")
        except (OSError, ValueError) as erro:
            raise PublicacaoInvalida("Controle do assistente inválido") from erro
        return Pacote(definicoes, populacao, descricao.versao, consumo)
    conteudo = {"manifesto": definicoes, "populacao": [o.model_dump() for o in populacao]}
    versao = hashlib.sha256(
        json.dumps(conteudo, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()[:16]
    return Pacote(definicoes, populacao, versao)


def _chave_edicao(edicao: str) -> tuple[int, int, str]:
    """Edições numéricas comparadas como número ("10" > "9"); as demais, como texto."""
    return (1, int(edicao), edicao) if edicao.isdigit() else (0, 0, edicao)


def _chave_data(texto: str) -> datetime:
    """Datas ISO 8601 comparadas como data, aceitando "Z" ou deslocamento ("+00:00")."""
    data = datetime.fromisoformat(texto)
    return data if data.tzinfo else data.replace(tzinfo=UTC)


def _metadados(id_: str, pacote: Pacote) -> Metadados:
    definicao = pacote.definicoes[id_]
    edicoes = [o.edicao_fonte for o in pacote.populacao if o.indicador == id_ and o.edicao_fonte]
    return Metadados(
        fonte=str(definicao["fonte"]),
        metodo=str(definicao["metodo"]),
        limitacoes=str(definicao["limitacoes"]),
        edicao=max(edicoes, key=_chave_edicao, default=None),
    )


def _status(id_: str, pacote: Pacote, motivo_padrao: str | None = None) -> StatusIndicador:
    originais = [o for o in pacote.populacao if o.indicador == id_]
    datas = [o.atualizado_em for o in originais if o.atualizado_em]
    try:
        atualizado_em = max(datas, key=_chave_data, default=None)
    except ValueError as erro:
        raise PublicacaoInvalida(f"Data de atualização inválida em {id_}") from erro
    motivo = (
        None
        if originais
        else (motivo_padrao or MOTIVOS.get(id_, "Não há lote homologado publicado para este indicador."))
    )
    return StatusIndicador(
        indicador=id_,
        situacao="publicado" if originais else "sem_dado_validado",
        motivo=motivo,
        ano_referencia=max((o.ano for o in originais), default=None),
        atualizado_em=atualizado_em,
        metadados=_metadados(id_, pacote),
    )


def status_geral(pasta: Path | None = None) -> list[StatusIndicador]:
    """Status de todos os indicadores do manifesto (RN-ENT-04), inclusive os que ainda não têm dimensão na API."""
    pacote = ler_pacote(pasta)
    mapeados = {id_ for ids in DIMENSOES.values() for id_ in ids}
    return [
        _status(
            id_, pacote, None if id_ in mapeados else "Indicador do manifesto sem dimensão definida na API."
        )
        for id_ in pacote.definicoes
    ]


def consultar(
    dimensao: str,
    municipio_id: str | None = None,
    ano_inicio: int | None = None,
    ano_fim: int | None = None,
    pasta: Path | None = None,
    periodicidade: Literal["mensal", "anual"] = "mensal",
    categoria: str | None = None,
) -> RespostaDimensao:
    pacote = ler_pacote(pasta)
    permitidos = DIMENSOES[dimensao]
    faltantes = [id_ for id_ in permitidos if id_ not in pacote.definicoes]
    if faltantes:
        raise PublicacaoInvalida(f"Manifesto de indicadores sem: {', '.join(faltantes)}")
    todas = [o for o in pacote.populacao if o.indicador in permitidos]
    # O filtro só afeta observações; status informa a publicação inteira, mesmo sem pontos no recorte.
    linhas = [
        o
        for o in todas
        # A série global (preço de commodity) não pertence a município: o filtro municipal não a esconde.
        if (municipio_id is None or o.nivel_territorial == "global" or o.municipio_id == municipio_id)
        and (ano_inicio is None or o.ano >= ano_inicio)
        and (ano_fim is None or o.ano <= ano_fim)
        and (categoria is None or o.categoria == categoria)
    ]
    notas = [
        (
            "Somente observações conferidas com a fonte oficial; no ano ainda aberto saem como provisórias "
            "(RN-CFE-06). Ausência não equivale a zero."
        )
    ]
    if any(o.indicador.startswith("despesa_funcao_") for o in todas):
        notas.append(
            "Despesa por função: só o município, exercício e estágio que coincidem ao centavo com o RREO "
            "(empenhada e liquidada) ou com a MSC (paga), declarações do próprio município (RN-FNT-04). "
            "Funções, subfunções e o total estão na mesma série: filtre por `categoria` antes de somar."
        )
    if periodicidade == "anual":
        linhas, avisos = agregar_anos(linhas)
        notas.extend(avisos)
    return RespostaDimensao(
        filtros={
            "dimensao": dimensao,
            "municipio_id": municipio_id,
            "ano_inicio": ano_inicio,
            "ano_fim": ano_fim,
            "periodicidade": periodicidade,
            "categoria": categoria,
        },
        versao_dados=pacote.versao,
        notas=notas,
        dados=linhas,
        status=[_status(id_, pacote) for id_ in permitidos],
        metadados={id_: _metadados(id_, pacote) for id_ in permitidos},
        lacunas=LACUNAS[dimensao],
    )


def agregar_anos(observacoes: list[Observacao]) -> tuple[list[Observacao], list[str]]:
    """RN-CFE-05/11: somente 12 meses validados, soma decimal calculada no servidor."""
    grupos: dict[tuple[str | None, int], list[Observacao]] = defaultdict(list)
    saida = [o for o in observacoes if o.indicador != "cfem_arrecadada"]
    notas = []
    for item in observacoes:
        if item.indicador == "cfem_arrecadada":
            grupos[(item.municipio_id, item.ano)].append(item)
    for (codigo, ano), meses in grupos.items():
        if (
            len(meses) != 12
            or {o.mes for o in meses} != set(range(1, 13))
            or any(o.valor is None or o.estado_validacao != "validado" for o in meses)
        ):
            notas.append(f"{codigo}/{ano}: ano incompleto, sem total anual homologado.")
            continue
        total = sum((Decimal(str(o.valor)) for o in meses), Decimal(0))
        saida.append(
            meses[0].model_copy(
                update={
                    "mes": None,
                    "valor": total,
                    "natureza_valor": "zero real" if total == 0 else "informado",
                }
            )
        )
    return saida, notas
