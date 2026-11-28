"""Fonte PIB dos Municípios do IBGE pelo SIDRA, agregado 5938 (RN-FNT-02, RN-FNT-19, RN-TMP-16).

Lê a lista de anos do agregado (com a data de modificação de cada um) e, num só pedido, o PIB, os impostos
líquidos e o valor adicionado bruto (total e por setor) dos 12 municípios da RI Carajás, de 2010 ao último ano
publicado. Guarda as duas respostas com o SHA-256 e a URL (RN-FON-13, RN-FON-14). Confere o nome e a unidade
de cada variável (RN-VPU-04) e se a resposta identifica exatamente os municípios pedidos (RN-FNT-19, RN-TER-07).

Valores em mil reais inteiros, como o SIDRA publica (decisão do mantenedor de 27/11/2026). VAB negativo é
publicado como o IBGE publica. Os sinais do SIDRA não viram zero (RN-MOD-10, RN-MOD-12): `...` é ausente,
`..` não se aplica e `X` não divulgado; `-` é zero absoluto.

Não confere, não aprova nem publica: isso é da validação.
"""

import hashlib
import json
import re
import time
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from observatorio.modelo.lote import LotePib
from observatorio.modelo.observacao import Observacao
from observatorio.modelo.territorios import MUNICIPIOS

SIDRA = "https://servicodados.ibge.gov.br/api/v3/agregados/5938"
URL_PERIODOS = f"{SIDRA}/periodos"
ANO_INICIO = 2010  # RN-TMP-16
UNIDADE_SIDRA = "Mil Reais"
UNIDADE = "BRL mil nominal"
VERSAO_TRATAMENTO = "1.0.0"

# Variável do SIDRA → (indicador do manifesto, nome da variável como o SIDRA o publica).
VARIAVEIS: dict[str, tuple[str, str]] = {
    "37": ("pib_municipal", "Produto Interno Bruto a preços correntes"),
    "543": ("pib_impostos_liquidos", "Impostos, líquidos de subsídios, sobre produtos a preços correntes"),
    "498": ("vab_total", "Valor adicionado bruto a preços correntes total"),
    "513": ("vab_agropecuaria", "Valor adicionado bruto a preços correntes da agropecuária"),
    "517": ("vab_industria", "Valor adicionado bruto a preços correntes da indústria"),
    "6575": (
        "vab_servicos",
        (
            "Valor adicionado bruto a preços correntes dos serviços, exclusive administração, defesa, educação e "
            "saúde públicas e seguridade social"
        ),
    ),
    "525": (
        "vab_administracao_publica",
        (
            "Valor adicionado bruto a preços correntes da administração, defesa, educação e saúde públicas e "
            "seguridade social"
        ),
    ),
}
INDICADORES = tuple(indicador for indicador, _ in VARIAVEIS.values())

Natureza = Literal["informado", "zero real", "ausente", "não divulgado", "não aplicável"]
SINAIS: dict[str, Natureza] = {
    "-": "zero real",
    "...": "ausente",
    "..": "não aplicável",
    "X": "não divulgado",
}

Buscar = Callable[[str], bytes]


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
                raise ValueError(f"SIDRA respondeu HTTP {erro.code} em {url}") from erro
        except (URLError, TimeoutError) as erro:
            if tentativa == 2:
                raise ValueError(f"SIDRA inacessível em {url}: {erro}") from erro
        time.sleep(5 * (tentativa + 1))
    raise AssertionError("inalcançável")


def _json(corpo: bytes, onde: str) -> object:
    try:
        return json.loads(corpo)
    except ValueError as erro:
        raise ValueError(f"PIB: resposta do SIDRA ilegível em {onde} (RN-VPU-04)") from erro


def ler_periodos(corpo: bytes) -> dict[int, str]:
    """Ano → data de modificação, para os anos a partir de 2010 (RN-TMP-16); falha em layout novo."""
    dados = _json(corpo, "periodos")
    if not isinstance(dados, list):
        raise ValueError("PIB: lista de períodos inesperada (RN-VPU-04)")  # noqa: TRY004
    saida: dict[int, str] = {}
    for item in dados:
        if not isinstance(item, dict) or not re.fullmatch(r"\d{4}", str(item.get("id"))):
            raise ValueError("PIB: período sem ano de quatro dígitos (RN-VPU-04)")
        ano = int(str(item["id"]))
        if ano >= ANO_INICIO:
            saida[ano] = str(item.get("modificacao", ""))
    if not saida:
        raise ValueError(f"PIB: nenhum ano a partir de {ANO_INICIO} no agregado 5938")
    return saida


def url_dados(anos: list[int]) -> str:
    """O pedido único com os 12 municípios, os anos e as sete variáveis (RN-FNT-19)."""
    periodos = "|".join(str(a) for a in anos)
    variaveis = "|".join(VARIAVEIS)
    localidades = quote(f"N6[{','.join(MUNICIPIOS)}]", safe="")
    return f"{SIDRA}/periodos/{quote(periodos, safe='')}/variaveis/{quote(variaveis, safe='')}?localidades={localidades}"


def _sem_acento(texto: str) -> str:
    """RN-TER-07: compara nomes sem acento e sem diferença de caixa."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold().strip()


def _valor(bruto: object, onde: str) -> tuple[Decimal | None, Natureza]:
    texto = str(bruto).strip()
    if texto in SINAIS:
        natureza = SINAIS[texto]
        return (Decimal(0), natureza) if natureza == "zero real" else (None, natureza)
    if not re.fullmatch(r"-?\d+", texto):
        raise ValueError(f"PIB: valor inesperado {texto!r} em {onde} (RN-VPU-04)")
    valor = Decimal(texto)
    # "0" no SIDRA é arredondamento a zero de um valor pequeno; o modelo só tem "zero real" para valor zero.
    return valor, ("zero real" if valor == 0 else "informado")


def converter(corpo: bytes, anos: list[int], instante: str, edicao: str) -> tuple[Observacao, ...]:
    """Uma observação por variável, município e ano; layout, unidade e municípios conferidos."""
    dados = _json(corpo, "dados")
    if not isinstance(dados, list):
        raise ValueError("PIB: resposta de dados inesperada (RN-VPU-04)")  # noqa: TRY004
    por_id = {str(v.get("id")): v for v in dados if isinstance(v, dict)}
    if len(por_id) != len(dados) or set(por_id) != set(VARIAVEIS):
        raise ValueError(
            f"PIB: variáveis {sorted(por_id)} diferentes das esperadas {sorted(VARIAVEIS)} (RN-VPU-04)"
        )
    esperados = {str(a) for a in anos}
    saida: list[Observacao] = []
    for id_variavel, (indicador, nome) in VARIAVEIS.items():
        variavel = por_id[id_variavel]
        if variavel.get("variavel") != nome:
            raise ValueError(f"PIB: variável {id_variavel} com nome inesperado {variavel.get('variavel')!r}")
        if variavel.get("unidade") != UNIDADE_SIDRA:
            raise ValueError(
                f"PIB: variável {id_variavel} com unidade inesperada {variavel.get('unidade')!r}"
            )
        resultados = variavel.get("resultados")
        if not isinstance(resultados, list) or len(resultados) != 1 or resultados[0].get("classificacoes"):
            raise ValueError(f"PIB: variável {id_variavel} com resultados inesperados (RN-VPU-04)")
        series = resultados[0].get("series")
        if not isinstance(series, list):
            raise ValueError(f"PIB: variável {id_variavel} sem séries (RN-VPU-04)")  # noqa: TRY004
        vistos: set[str] = set()
        for serie in series:
            localidade = serie.get("localidade", {})
            codigo = str(localidade.get("id"))
            if codigo not in MUNICIPIOS or codigo in vistos:
                raise ValueError(f"PIB: município {codigo} não pedido ou repetido na resposta (RN-FNT-19)")
            vistos.add(codigo)
            nome_devolvido = re.sub(r"\s*\(PA\)$", "", str(localidade.get("nome", "")))
            if _sem_acento(nome_devolvido) != _sem_acento(MUNICIPIOS[codigo]):
                raise ValueError(f"PIB: {codigo} devolvido como {nome_devolvido!r} (RN-FNT-19, RN-TER-07)")
            valores = serie.get("serie")
            if not isinstance(valores, dict) or set(valores) != esperados:
                raise ValueError(f"PIB: {codigo}, variável {id_variavel}: anos diferentes dos pedidos")
            for ano in anos:
                valor, natureza = _valor(valores[str(ano)], f"{codigo} {ano} variável {id_variavel}")
                saida.append(
                    Observacao(
                        indicador=indicador,
                        municipio_id=codigo,
                        municipio_nome=MUNICIPIOS[codigo],
                        nivel_territorial="município",
                        ano=ano,
                        mes=None,
                        valor=valor,
                        unidade=UNIDADE,
                        natureza_valor=natureza,
                        estado_validacao="provisório",
                        fonte=f"IBGE SIDRA, agregado 5938, variável {id_variavel}",
                        edicao_fonte=edicao,
                        atualizado_em=instante,
                        versao_tratamento=VERSAO_TRATAMENTO,
                    )
                )
        if vistos != set(MUNICIPIOS):
            faltam = sorted(set(MUNICIPIOS) - vistos)
            raise ValueError(f"PIB: variável {id_variavel} sem os municípios {faltam} (RN-FNT-19)")
    return tuple(saida)


def coletar(pasta: Path, buscar: Buscar = buscar_http, agora: datetime | None = None) -> LotePib:
    """RN-FON-13/14: baixa os períodos e os dados do agregado 5938 e guarda o bruto com a proveniência."""
    instante = (agora or datetime.now(UTC)).isoformat()
    corpo_periodos = buscar(URL_PERIODOS)
    periodos = ler_periodos(corpo_periodos)
    anos = sorted(periodos)
    origem = url_dados(anos)
    corpo = buscar(origem)
    if not corpo:
        raise ValueError("PIB: resposta vazia do SIDRA")
    sha_periodos, sha = hashlib.sha256(corpo_periodos).hexdigest(), hashlib.sha256(corpo).hexdigest()
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "periodos.json").write_bytes(corpo_periodos)
    (pasta / "sidra-5938.json").write_bytes(corpo)
    filtros: dict[str, object] = {
        "agregado": "5938",
        "variaveis": list(VARIAVEIS),
        "municipios": list(MUNICIPIOS),
        "anos": anos,
    }
    (pasta / "indice.json").write_text(
        json.dumps(
            {
                "coletado_em": instante,
                "arquivos": {
                    "periodos.json": {"url": URL_PERIODOS, "sha256": sha_periodos},
                    "sidra-5938.json": {"url": origem, "sha256": sha},
                },
                "filtros": filtros,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return LotePib(
        observacoes=converter(corpo, anos, instante, sha),
        periodos={str(ano): data for ano, data in periodos.items()},
        bruto=pasta,
        sha256=sha,
        coletado_em=instante,
        origem=origem,
        filtros=filtros,
    )
