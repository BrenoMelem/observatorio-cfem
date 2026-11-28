"""Fonte Pink Sheet do World Bank: preços globais de minério de ferro e cobre (RN-FNT-05, RN-TMP-13/14).

Acha na página do World Bank o endereço das planilhas mensal e anual (o endereço traz um código que muda a
cada edição), baixa as duas, guarda cada uma com o SHA-256 e a origem (RN-FON-13, RN-FON-14) e lê as colunas
pelo nome, conferindo a unidade (RN-VPU-04). O ferro sai em duas séries separadas: contrato anual em ¢/dmtu
de 1985 a 2005 e spot mensal em USD/dmt desde dezembro de 2008 (RN-TMP-13, RN-TMP-14); o cobre, mensal desde
2000. Séries globais, sem município (RN-MOD-19). Valor ausente fica ausente, nunca zero (RN-MOD-12).

Não confere, não aprova nem publica: isso é da validação.
"""

import hashlib
import io
import itertools
import json
import math
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from observatorio.modelo.lote import LotePinkSheet
from observatorio.modelo.observacao import Observacao

PAGINA = "https://www.worldbank.org/en/research/commodity-markets"
_LINK = r"https://thedocs\.worldbank\.org/[^\"'\s<>]*CMO-Historical-Data-{}\.xlsx"
ABA_MENSAL = "Monthly Prices"
ABA_ANUAL = "Annual Prices (Nominal)"
FERRO, COBRE = "Iron ore, cfr spot", "Copper"
UNIDADES_PLANILHA = {FERRO: "($/dmtu)", COBRE: "($/mt)"}
CONTRATO_ANOS = (1985, 2005)
SPOT_INICIO = (2008, 12)
COBRE_INICIO = (2000, 1)
IND_CONTRATO = "preco_minerio_ferro_contrato"
IND_SPOT = "preco_minerio_ferro_spot"
IND_COBRE = "preco_cobre"
UNIDADES = {IND_CONTRATO: "¢/dmtu", IND_SPOT: "USD/dmt", IND_COBRE: "USD/t"}
INDICADORES = tuple(UNIDADES)
VERSAO_TRATAMENTO = "1.0.0"

Buscar = Callable[[str], bytes]
Serie = dict[tuple[int, int], Decimal | None]


def buscar_http(url: str) -> bytes:
    """GET com User-Agent de navegador; três tentativas em erro de rede ou 5xx."""
    for tentativa in range(3):
        requisicao = Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        try:
            with urlopen(requisicao, timeout=120) as resposta:
                corpo: bytes = resposta.read()
                return corpo
        except HTTPError as erro:
            if erro.code < 500 or tentativa == 2:
                raise ValueError(f"World Bank respondeu HTTP {erro.code} em {url}") from erro
        except (URLError, TimeoutError) as erro:
            if tentativa == 2:
                raise ValueError(f"World Bank inacessível em {url}: {erro}") from erro
        time.sleep(5 * (tentativa + 1))
    raise AssertionError("inalcançável")


def achar_link(html: str, tipo: str) -> str:
    """O endereço da planilha `Monthly` ou `Annual`; falha se a página não traz exatamente um."""
    achados = sorted(set(re.findall(_LINK.format(tipo), html)))
    if len(achados) != 1:
        raise ValueError(f"Pink Sheet: {len(achados)} endereços da planilha {tipo} na página (RN-VPU-04)")
    return str(achados[0])


def _linhas(conteudo: bytes, aba: str) -> list[tuple[object, ...]]:
    from openpyxl import load_workbook  # só a coleta do Pink Sheet usa (extra `coleta`, ADR-013)

    try:
        livro = load_workbook(io.BytesIO(conteudo), read_only=True, data_only=True)
        return [tuple(linha) for linha in livro[aba].iter_rows(values_only=True)]
    except Exception as erro:
        raise ValueError(f"Pink Sheet: planilha ilegível ou sem a aba {aba!r} (RN-VPU-04)") from erro


def _preco(bruto: object, onde: str) -> Decimal | None:
    if isinstance(bruto, bool) or not isinstance(bruto, int | float):
        return None  # "…", "..", vazio: ausente, nunca zero (RN-MOD-12)
    if not math.isfinite(bruto) or bruto < 0:
        raise ValueError(f"Pink Sheet: preço inválido em {onde}")
    return Decimal(str(bruto))


def _cabecalho(linhas: list[tuple[object, ...]]) -> int:
    achado = next((k for k, r in enumerate(linhas[:15]) if FERRO in r and COBRE in r), None)
    if achado is None:
        raise ValueError("Pink Sheet: colunas de ferro e cobre não encontradas (RN-VPU-04)")
    return achado


def ler_mensal(conteudo: bytes) -> dict[str, Serie]:
    """Colunas de ferro e cobre da aba mensal, por (ano, mês), conferindo unidade, mês e duplicidade."""
    linhas = _linhas(conteudo, ABA_MENSAL)
    topo = _cabecalho(linhas)
    if topo + 1 >= len(linhas):
        raise ValueError("Pink Sheet: planilha mensal sem linha de unidades (RN-VPU-04)")
    saida: dict[str, Serie] = {}
    for nome, esperada in UNIDADES_PLANILHA.items():
        coluna = linhas[topo].index(nome)
        if str(linhas[topo + 1][coluna]).strip() != esperada:
            raise ValueError(f"Pink Sheet: {nome}: unidade inesperada {linhas[topo + 1][coluna]!r}")
        serie: Serie = {}
        for linha in linhas[topo + 2 :]:
            achado = re.fullmatch(r"(\d{4})M(\d{2})", linha[0]) if isinstance(linha[0], str) else None
            if not achado:
                continue
            ano, mes = int(achado[1]), int(achado[2])
            if not 1 <= mes <= 12 or (ano, mes) in serie:
                raise ValueError(f"Pink Sheet: {nome}: mês inválido ou duplicado ({linha[0]})")
            serie[(ano, mes)] = _preco(linha[coluna], f"{nome} {linha[0]}")
        saida[nome] = serie
    return saida


def ler_anual(conteudo: bytes) -> dict[str, dict[int, Decimal]]:
    """Valor anual de ferro e cobre da planilha anual, a referência da conferência (RN-VPU-07)."""
    linhas = _linhas(conteudo, ABA_ANUAL)
    topo = _cabecalho(linhas)
    saida: dict[str, dict[int, Decimal]] = {}
    for nome in UNIDADES_PLANILHA:
        coluna = linhas[topo].index(nome)
        anos: dict[int, Decimal] = {}
        for linha in linhas[topo + 2 :]:
            rotulo = linha[0]
            texto = (
                str(int(rotulo))
                if isinstance(rotulo, int | float) and not isinstance(rotulo, bool)
                else rotulo
            )
            if not isinstance(texto, str) or not re.fullmatch(r"\d{4}", texto):
                continue
            valor = _preco(linha[coluna], f"{nome} {texto} (anual)")
            if valor is not None:
                anos[int(texto)] = valor
        saida[nome] = anos
    return saida


def _mensal(serie: Serie, inicio: tuple[int, int], nome: str) -> list[tuple[int, int | None, Decimal | None]]:
    meses = sorted(p for p in serie if p >= inicio)
    if not meses or meses[0] != inicio:
        raise ValueError(f"Pink Sheet: {nome}: série não começa em {inicio[0]}-{inicio[1]:02d} (RN-VPU-04)")
    for (a1, m1), (a2, m2) in itertools.pairwise(meses):
        if a2 * 12 + m2 != a1 * 12 + m1 + 1:
            raise ValueError(f"Pink Sheet: {nome}: lacuna na sequência mensal")
    return [(a, m, serie[(a, m)]) for a, m in meses]


def _contrato(serie: Serie) -> list[tuple[int, int | None, Decimal | None]]:
    """RN-TMP-13: o contrato é anual; a planilha mensal o repete nos 12 meses, e qualquer variação falha."""
    saida: list[tuple[int, int | None, Decimal | None]] = []
    for ano in range(CONTRATO_ANOS[0], CONTRATO_ANOS[1] + 1):
        doze = {serie.get((ano, mes)) for mes in range(1, 13)}
        if len(doze) != 1 or None in doze:
            raise ValueError(f"Pink Sheet: ferro, contrato: {ano} não tem um valor único nos 12 meses")
        saida.append((ano, None, doze.pop()))
    return saida


def converter(mensal: bytes, instante: str, edicao: str) -> tuple[Observacao, ...]:
    """Observações de ferro (contrato e spot, separadas) e cobre, nos recortes de RN-TMP-13 e RN-TMP-14."""
    colunas = ler_mensal(mensal)
    series: dict[str, tuple[str, list[tuple[int, int | None, Decimal | None]]]] = {
        IND_CONTRATO: ("Iron ore, cfr spot (contrato anual)", _contrato(colunas[FERRO])),
        IND_SPOT: ("Iron ore, cfr spot (spot 62% Fe)", _mensal(colunas[FERRO], SPOT_INICIO, "ferro, spot")),
        IND_COBRE: ("Copper", _mensal(colunas[COBRE], COBRE_INICIO, "cobre")),
    }
    saida: list[Observacao] = []
    for indicador, (coluna, pontos) in series.items():
        if all(v is None for _, _, v in pontos):
            raise ValueError(f"Pink Sheet: {indicador}: série sem valores")
        for ano, mes, valor in pontos:
            saida.append(
                Observacao(
                    indicador=indicador,
                    municipio_id=None,
                    municipio_nome=None,
                    nivel_territorial="global",
                    ano=ano,
                    mes=mes,
                    valor=valor,
                    unidade=UNIDADES[indicador],
                    natureza_valor="ausente" if valor is None else "informado",
                    estado_validacao="provisório",
                    fonte=f"World Bank, Pink Sheet mensal, coluna {coluna}",
                    edicao_fonte=edicao,
                    atualizado_em=instante,
                    versao_tratamento=VERSAO_TRATAMENTO,
                )
            )
    return tuple(saida)


def coletar(pasta: Path, buscar: Buscar = buscar_http, agora: datetime | None = None) -> LotePinkSheet:
    """RN-FON-13/14: baixa as planilhas mensal e anual da edição vigente e guarda o bruto com a proveniência."""
    instante = (agora or datetime.now(UTC)).isoformat()
    html = buscar(PAGINA).decode("utf-8", errors="replace")
    url_mensal, url_anual = achar_link(html, "Monthly"), achar_link(html, "Annual")
    mensal, anual = buscar(url_mensal), buscar(url_anual)
    if not mensal or not anual:
        raise ValueError("Pink Sheet: planilha vazia")
    sha_mensal, sha_anual = hashlib.sha256(mensal).hexdigest(), hashlib.sha256(anual).hexdigest()
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "CMO-Historical-Data-Monthly.xlsx").write_bytes(mensal)
    (pasta / "CMO-Historical-Data-Annual.xlsx").write_bytes(anual)
    filtros: dict[str, object] = {
        "colunas": list(UNIDADES_PLANILHA),
        "contrato_anos": list(CONTRATO_ANOS),
        "spot_inicio": list(SPOT_INICIO),
        "cobre_inicio": list(COBRE_INICIO),
    }
    (pasta / "indice.json").write_text(
        json.dumps(
            {
                "pagina": PAGINA,
                "coletado_em": instante,
                "arquivos": {
                    "CMO-Historical-Data-Monthly.xlsx": {"url": url_mensal, "sha256": sha_mensal},
                    "CMO-Historical-Data-Annual.xlsx": {"url": url_anual, "sha256": sha_anual},
                },
                "filtros": filtros,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    observacoes = converter(mensal, instante, sha_mensal)
    anual_lido = ler_anual(anual)
    referencia = {
        (indicador, ano): valor
        for indicador, coluna in ((IND_CONTRATO, FERRO), (IND_SPOT, FERRO), (IND_COBRE, COBRE))
        for ano, valor in anual_lido[coluna].items()
    }
    return LotePinkSheet(
        observacoes=observacoes,
        referencia=referencia,
        bruto=pasta,
        sha256=sha_mensal,
        sha256_anual=sha_anual,
        coletado_em=instante,
        origem=url_mensal,
        origem_anual=url_anual,
        filtros=filtros,
    )
