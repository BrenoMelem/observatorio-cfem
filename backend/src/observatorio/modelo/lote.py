"""Contratos entre fonte e validação: RN-FON-13/14 e RN-VPU-06."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from observatorio.modelo.observacao import Observacao


@dataclass(frozen=True)
class Lote:
    observacoes: tuple[Observacao, ...]
    bruto: Path
    sha256: str
    coletado_em: str
    origem: str
    linhas_lidas: int
    linhas_recorte: int
    duplicatas: int
    registros_municipais: dict[str, int]
    registros_mensais: dict[str, int]
    totais_nacionais: dict[str, str]
    filtros: dict[str, object]


@dataclass(frozen=True)
class Resultado:
    """Saída de uma validação: o que pode ser publicado e o relatório do lote (RN-VPU-06)."""

    aprovado: bool
    observacoes: tuple[Observacao, ...]
    erros: tuple[str, ...]
    relatorio: dict[str, object]


@dataclass(frozen=True)
class LinhaReferencia:
    """Uma linha de uma publicação de referência do SICONFI, na ordem em que a API a devolve (RN-VPU-07)."""

    municipio_id: str
    ano: int
    estagio: str
    conta: str
    valor: Decimal


@dataclass(frozen=True)
class Entrega:
    """Uma entrega do extrato do SICONFI: o que o município declarou e quando (RN-TMP-04)."""

    municipio_id: str
    ano: int
    entregavel: str
    periodo: int | None
    instituicao: str
    status: str | None
    data_status: str


@dataclass(frozen=True)
class LoteDespesa:
    """Despesa por função da DCA com as referências do mesmo município e exercício (RN-FNT-04).

    `observacoes` traz todas as linhas da DCA, ainda sem conferência; `rreo` as linhas do RREO Anexo 2
    do 6º bimestre (empenhada e liquidada); `msc` a despesa paga da MSC de dezembro, somada por função
    e subfunção (chave `FF.SSS`).
    """

    observacoes: tuple[Observacao, ...]
    rreo: tuple[LinhaReferencia, ...]
    msc: dict[tuple[str, int], dict[str, Decimal]]
    entregas: tuple[Entrega, ...]
    anos: tuple[int, ...]
    bruto: Path
    sha256: str
    coletado_em: str
    origem: str
    respostas: int
    linhas_lidas: int
    intraorcamentarias: int
    filtros: dict[str, object]


@dataclass(frozen=True)
class LotePib:
    """PIB e VAB dos municípios lidos do SIDRA 5938, ainda `provisório` (RN-FNT-02).

    Sem referência externa (exceção de RN-VPU-07 de 27/11/2026): `periodos` traz a data de modificação de
    cada ano no SIDRA, que mostra se há edição nova (RN-TMP-02).
    """

    observacoes: tuple[Observacao, ...]
    periodos: dict[str, str]
    bruto: Path
    sha256: str
    coletado_em: str
    origem: str
    filtros: dict[str, object]


@dataclass(frozen=True)
class LotePinkSheet:
    """Preços de ferro e cobre da planilha mensal e a média anual da planilha anual da mesma edição.

    `observacoes` traz todos os pontos lidos, ainda `provisório`; `referencia` traz o valor anual
    publicado pelo World Bank, por (indicador, ano), para a conferência (RN-FNT-05, RN-VPU-07).
    """

    observacoes: tuple[Observacao, ...]
    referencia: dict[tuple[str, int], Decimal]
    bruto: Path
    sha256: str
    sha256_anual: str
    coletado_em: str
    origem: str
    origem_anual: str
    filtros: dict[str, object]
