"""Consulta por dimensão e status, preservando ausências como lacunas."""
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from observatorio.api.dtos.publicacao import Metadados, Observacao, RespostaDimensao, StatusIndicador
from observatorio.api.repositories.publicacao import (
    PublicacaoInvalida,
    manifesto_publicado,
    populacao_publicada,
)

DIMENSOES = {
    "social": ("populacao_estimada", "despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
    "economica": ("cfem_arrecadada", "preco_minerio_ferro", "preco_cobre", "despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
    "ambiental": ("despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
    "institucional": ("despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"),
}
MOTIVOS = {
    "cfem_arrecadada": "Lote da API CFEM sem homologação demonstrada para esta camada (RN-VPU-10).",
    "preco_minerio_ferro": "Séries do Pink Sheet sem publicação homologada nesta camada (RN-TMP-13, RN-VPU-07).",
    "preco_cobre": "Série do Pink Sheet sem publicação homologada nesta camada (RN-FNT-05, RN-VPU-07).",
}
LACUNAS = {
    "social": ["Censo, emprego, educação, saúde, pobreza, segurança, moradia e saneamento: sem publicação homologada nesta camada."],
    "economica": ["PIB, VAB, receitas, investimentos e distribuição recebida: sem publicação homologada nesta camada."],
    "ambiental": ["Uso do solo, emissões e saneamento domiciliar: sem publicação homologada nesta camada."],
    "institucional": ["Índices compostos, receita e gestão pública: sem publicação homologada nesta camada."],
}


@dataclass(frozen=True)
class Pacote:
    """O pacote publicado lido uma vez por requisição, para não misturar versões se ele for trocado no meio."""
    definicoes: dict[str, dict[str, object]]
    populacao: list[Observacao]
    versao: str


def ler_pacote(pasta: Path | None = None) -> Pacote:
    definicoes = manifesto_publicado(pasta)
    populacao = populacao_publicada(pasta)
    conteudo = {"manifesto": definicoes, "populacao": [o.model_dump() for o in populacao]}
    versao = hashlib.sha256(json.dumps(conteudo, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
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
    return Metadados(fonte=str(definicao["fonte"]), metodo=str(definicao["metodo"]),
                     limitacoes=str(definicao["limitacoes"]), edicao=max(edicoes, key=_chave_edicao, default=None))


def _status(id_: str, pacote: Pacote, motivo_padrao: str | None = None) -> StatusIndicador:
    originais = [o for o in pacote.populacao if o.indicador == id_]
    datas = [o.atualizado_em for o in originais if o.atualizado_em]
    try:
        atualizado_em = max(datas, key=_chave_data, default=None)
    except ValueError as erro:
        raise PublicacaoInvalida(f"Data de atualização inválida em {id_}") from erro
    motivo = None if originais else (motivo_padrao or MOTIVOS.get(
        id_, "Não há lote homologado publicado para este indicador."))
    return StatusIndicador(indicador=id_, situacao="publicado" if originais else "sem_dado_validado", motivo=motivo,
                           ano_referencia=max((o.ano for o in originais), default=None),
                           atualizado_em=atualizado_em, metadados=_metadados(id_, pacote))


def status_geral(pasta: Path | None = None) -> list[StatusIndicador]:
    """Status de todos os indicadores do manifesto (RN-ENT-04), inclusive os que ainda não têm dimensão na API."""
    pacote = ler_pacote(pasta)
    mapeados = {id_ for ids in DIMENSOES.values() for id_ in ids}
    return [_status(id_, pacote, None if id_ in mapeados else "Indicador do manifesto sem dimensão definida na API.")
            for id_ in pacote.definicoes]


def consultar(dimensao: str, municipio_id: str | None = None, ano_inicio: int | None = None,
             ano_fim: int | None = None, pasta: Path | None = None) -> RespostaDimensao:
    pacote = ler_pacote(pasta)
    permitidos = DIMENSOES[dimensao]
    faltantes = [id_ for id_ in permitidos if id_ not in pacote.definicoes]
    if faltantes:
        raise PublicacaoInvalida(f"Manifesto de indicadores sem: {', '.join(faltantes)}")
    todas = [o for o in pacote.populacao if o.indicador in permitidos]
    # O filtro só afeta observações; status informa a publicação inteira, mesmo sem pontos no recorte.
    linhas = [o for o in todas if (municipio_id is None or o.municipio_id == municipio_id)
              and (ano_inicio is None or o.ano >= ano_inicio) and (ano_fim is None or o.ano <= ano_fim)]
    return RespostaDimensao(filtros={"dimensao": dimensao, "municipio_id": municipio_id,
                            "ano_inicio": ano_inicio, "ano_fim": ano_fim}, versao_dados=pacote.versao,
                            notas=["Somente observações validadas da camada publicada; ausência não equivale a zero."],
                            dados=linhas, status=[_status(id_, pacote) for id_ in permitidos],
                            metadados={id_: _metadados(id_, pacote) for id_ in permitidos},
                            lacunas=LACUNAS[dimensao])
