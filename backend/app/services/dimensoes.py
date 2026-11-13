"""Consulta por dimensão e status, preservando ausências como lacunas."""
import hashlib
import json
from pathlib import Path

from app.dtos.publicacao import Metadados, RespostaDimensao, StatusIndicador
from app.repositories.publicacao import populacao_publicada

RAIZ = Path(__file__).resolve().parents[3]
MANIFESTO = RAIZ / "data" / "indicadores.json"
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


def manifesto() -> dict:
    return json.loads(MANIFESTO.read_text(encoding="utf-8"))


def consultar(dimensao: str, municipio_id: str | None = None, ano_inicio: int | None = None,
             ano_fim: int | None = None, pasta: Path | None = None) -> RespostaDimensao:
    definicoes = manifesto()
    permitidos = DIMENSOES[dimensao]
    todas = populacao_publicada(pasta) if "populacao_estimada" in permitidos else []
    # O filtro só afeta observações; status informa a publicação inteira, mesmo sem pontos no recorte.
    linhas = [o for o in todas if (municipio_id is None or o.municipio_id == municipio_id)
              and (ano_inicio is None or o.ano >= ano_inicio) and (ano_fim is None or o.ano <= ano_fim)]
    metadados = {id_: Metadados(fonte=definicoes[id_]["fonte"], metodo=definicoes[id_]["metodo"],
                               limitacoes=definicoes[id_]["limitacoes"],
                               edicao=max((o.edicao_fonte for o in todas if o.indicador == id_ and o.edicao_fonte), default=None))
                 for id_ in permitidos}
    status = []
    for id_ in permitidos:
        originais = [o for o in todas if o.indicador == id_]
        status.append(StatusIndicador(indicador=id_, situacao="publicado" if originais else "sem_dado_validado",
                    motivo=None if originais else MOTIVOS.get(id_, "Não há lote homologado publicado para este indicador."),
                    ano_referencia=max((o.ano for o in originais), default=None),
                    atualizado_em=max((o.atualizado_em for o in originais if o.atualizado_em), default=None),
                    metadados=metadados[id_]))
    versao = hashlib.sha256(json.dumps([o.model_dump() for o in todas], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16] if todas else None
    return RespostaDimensao(filtros={"dimensao": dimensao, "municipio_id": municipio_id,
                            "ano_inicio": ano_inicio, "ano_fim": ano_fim}, versao_dados=versao,
                            notas=["Somente observações validadas da camada publicada; ausência não equivale a zero."],
                            dados=linhas, status=status, metadados=metadados, lacunas=LACUNAS[dimensao])
