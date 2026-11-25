"""Fonte ANM Extra: tabelas oficiais de arrecadação da CFEM, referência independente da validação.

RN-VPU-07 e RN-CFE-12: a tabela por município e mês do Pará (`arrecadacao_cfem_muni.aspx`) e o total
nacional do rodapé da tabela por estado (`arrecadacao_cfem_ano.aspx`) conferem o arquivo
`CFEM_Arrecadacao.csv`. O corpo HTTP de cada página é guardado comprimido; o SHA-256 registrado é o do
HTML. Célula vazia é lacuna, nunca zero (RN-CFE-07). A fonte não aprova nem publica: só produz as
referências, que a validação usa.
"""

import gzip
import hashlib
import ssl
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from observatorio.modelo.territorios import MUNICIPIOS

BASE = "https://sistemas.anm.gov.br/arrecadacao/extra/relatorios"
AGENTE = "Mozilla/5.0 ObservatorioCFEM/1.0"
MESES = 12


class ReferenciaMensal(TypedDict):
    municipio_id: str
    ano: int
    mes: int
    valor: str
    documento: str
    url: str
    consultado_em: str
    sha256: str


class ReferenciaNacional(TypedDict):
    ano: int
    valor: str
    documento: str
    url: str
    consultado_em: str
    sha256: str


@dataclass(frozen=True)
class Pagina:
    """Uma página capturada: o HTML (texto) e o SHA-256 do corpo HTTP original."""

    html: str
    sha256: str
    comprimido: bytes


def url_municipal(ano: int) -> str:
    return f"{BASE}/arrecadacao_cfem_muni.aspx?ano={ano}&uf=PA"


def url_nacional(ano: int) -> str:
    return f"{BASE}/arrecadacao_cfem_ano.aspx?ano={ano}"


def _chave_nome(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


_CODIGO_POR_NOME = {_chave_nome(nome): codigo for codigo, nome in MUNICIPIOS.items()}


def valor_brl(texto: str) -> Decimal | None:
    """'1.234,56' → Decimal('1234.56'); célula vazia → None (RN-CFE-07: lacuna, nunca zero)."""
    texto = texto.strip()
    if not texto:
        return None
    try:
        return Decimal(texto.replace(".", "").replace(",", "."))
    except InvalidOperation as erro:
        raise ValueError(f"ANM Extra: valor ilegível: {texto!r}") from erro


class _Tabela(HTMLParser):
    """Linhas (`<tr>`) com o texto de cada `<td>`, separando as do rodapé (`<tfoot>`)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.linhas: list[list[str]] = []
        self.rodape: list[list[str]] = []
        self._linha: list[str] | None = None
        self._celula: list[str] | None = None
        self._no_rodape = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tfoot":
            self._no_rodape = True
        elif tag == "tr":
            self._linha = []
        elif tag == "td" and self._linha is not None:
            self._celula = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "tfoot":
            self._no_rodape = False
        elif tag == "td" and self._linha is not None and self._celula is not None:
            self._linha.append(" ".join("".join(self._celula).split()))
            self._celula = None
        elif tag == "tr" and self._linha is not None:
            (self.rodape if self._no_rodape else self.linhas).append(self._linha)
            self._linha = None

    def handle_data(self, data: str) -> None:
        if self._celula is not None:
            self._celula.append(data)


def _ler(html: str) -> _Tabela:
    tabela = _Tabela()
    tabela.feed(html)
    tabela.close()
    return tabela


def _conferir_total(rotulo: str, meses: list[Decimal | None], total: Decimal | None) -> None:
    """RN-VPU-04: uma linha cujos meses não fecham com o total indica leitura errada da página."""
    soma = sum((m for m in meses if m is not None), Decimal(0))
    if total is None or soma != total:
        raise ValueError(f"ANM Extra, {rotulo}: soma dos meses ({soma}) diferente do total ({total})")


def extrair_municipal(html: str, ano: int) -> dict[str, list[Decimal | None]]:
    """Valores mensais dos 12 municípios da RI na tabela do Pará; município sem linha fica de fora."""
    saida: dict[str, list[Decimal | None]] = {}
    for linha in _ler(html).linhas:
        if len(linha) != 2 + MESES:
            continue
        codigo = _CODIGO_POR_NOME.get(_chave_nome(linha[0]))
        if codigo is None:
            continue
        if codigo in saida:
            raise ValueError(f"ANM Extra, {ano}: município repetido na tabela: {linha[0]}")
        meses = [valor_brl(c) for c in linha[1 : 1 + MESES]]
        _conferir_total(f"{ano} {linha[0]}", meses, valor_brl(linha[-1]))
        saida[codigo] = meses
    if not saida:
        raise ValueError(f"ANM Extra, {ano}: nenhum município da RI na tabela (layout alterado?)")
    return saida


def extrair_nacional(html: str, ano: int) -> Decimal:
    """RN-CFE-12: total anual do rodapé `Total:` da tabela por estado."""
    rodapes = [r for r in _ler(html).rodape if r and r[0].startswith("Total")]
    if len(rodapes) != 1 or len(rodapes[0]) != 2 + MESES:
        raise ValueError(f"ANM Extra, {ano}: rodapé 'Total:' ausente ou com formato inesperado")
    meses = [valor_brl(c) for c in rodapes[0][1 : 1 + MESES]]
    total = valor_brl(rodapes[0][-1])
    _conferir_total(f"{ano} Brasil", meses, total)
    if total is None:
        raise ValueError(f"ANM Extra, {ano}: total nacional vazio")
    return total


def baixar(url: str, certificado: Path | None = None) -> Pagina:
    """GET com User-Agent de navegador (a ANM recusa sem) e TLS verificado (RN-FON-13)."""
    contexto = ssl.create_default_context()
    if certificado:
        contexto.load_verify_locations(cafile=str(certificado))
    requisicao = Request(url, headers={"User-Agent": AGENTE})
    try:
        with urlopen(requisicao, timeout=120, context=contexto) as resposta:
            corpo: bytes = resposta.read()
    except (HTTPError, URLError) as erro:
        raise ValueError(f"ANM Extra indisponível em {url}: {erro}") from erro
    return Pagina(corpo.decode("utf-8"), hashlib.sha256(corpo).hexdigest(), gzip.compress(corpo, mtime=0))


def ler_captura(arquivo: Path) -> Pagina:
    """Página guardada em `.html.gz`; o hash é do HTML original, não do arquivo comprimido."""
    comprimido = arquivo.read_bytes()
    corpo = gzip.decompress(comprimido)
    return Pagina(corpo.decode("utf-8"), hashlib.sha256(corpo).hexdigest(), comprimido)


def referencias_municipais(
    pagina: Pagina, ano: int, consultado_em: str, ate_mes: int = MESES
) -> list[ReferenciaMensal]:
    """Uma referência por célula preenchida até `ate_mes` (no ano corrente, só os meses já fechados)."""
    saida: list[ReferenciaMensal] = []
    for codigo, meses in sorted(extrair_municipal(pagina.html, ano).items()):
        for mes, valor in enumerate(meses[:ate_mes], 1):
            if valor is None:
                continue
            saida.append(
                {
                    "municipio_id": codigo,
                    "ano": ano,
                    "mes": mes,
                    "valor": f"{valor:.2f}",
                    "documento": f"ANM Extra: Arrecadação CFEM por Ano/Estado, PA, {ano}; tabela municipal",
                    "url": url_municipal(ano),
                    "consultado_em": consultado_em,
                    "sha256": pagina.sha256,
                }
            )
    return saida


def referencia_nacional(pagina: Pagina, ano: int, consultado_em: str) -> ReferenciaNacional:
    return {
        "ano": ano,
        "valor": f"{extrair_nacional(pagina.html, ano):.2f}",
        "documento": f"ANM Extra: Arrecadação CFEM por Ano/Estado, Brasil, {ano}",
        "url": url_nacional(ano),
        "consultado_em": consultado_em,
        "sha256": pagina.sha256,
    }
