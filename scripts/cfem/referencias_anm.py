"""Captura as tabelas oficiais de arrecadação da CFEM da ANM e gera as referências da validação.

Script de laboratório (não é o produto). Gerou a primeira versão das referências em 25/11/2026; a versão
do produto, usada pelo workflow mensal, é `observatorio.referencias` (backend). Baixa, para cada ano, as páginas
`arrecadacao_cfem_muni.aspx?ano=AAAA&uf=PA` (por município e mês) e `arrecadacao_cfem_ano.aspx?ano=AAAA`
(total nacional), guarda o corpo HTTP original comprimido (`anm-pa-AAAA.html.gz`,
`anm-brasil-AAAA.html.gz`) e escreve `data/referencia-cfem-mensal-anm.json` e
`data/referencia-cfem-nacional-anm.json`, com URL, data e o SHA-256 do HTML de cada página (RN-VPU-07,
RN-CFE-12). Célula vazia na tabela é lacuna: não vira referência nem zero (RN-CFE-07).

Uso (da raiz):
    uv run python -m scripts.cfem.referencias_anm --pasta docs/registros/evidencias-anm-AAAA-MM-DD \
        --anos 2008-2025 --certificado scripts/cfem/certificados/sectigo-ov-r36.pem
    uv run python -m scripts.cfem.referencias_anm --pasta ... --anos 2008-2025 --sem-baixar   # só extrai
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import ssl
import time
import unicodedata
from datetime import date
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

from scripts.comum.municipios import MUNICIPIOS

BASE = "https://sistemas.anm.gov.br/arrecadacao/extra/relatorios"
AGENTE = "Mozilla/5.0 ObservatorioCFEM/1.0"
MESES = 12


def url_municipal(ano: int) -> str:
    return f"{BASE}/arrecadacao_cfem_muni.aspx?ano={ano}&uf=PA"


def url_nacional(ano: int) -> str:
    return f"{BASE}/arrecadacao_cfem_ano.aspx?ano={ano}"


def _chave_nome(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


_CODIGO_POR_NOME = {_chave_nome(nome): codigo for codigo, nome in MUNICIPIOS.items()}


def valor_brl(texto: str) -> Decimal | None:
    """'1.234,56' → Decimal('1234.56'); célula vazia → None (lacuna, nunca zero)."""
    texto = texto.strip()
    if not texto:
        return None
    return Decimal(texto.replace(".", "").replace(",", "."))


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
    soma = sum((m for m in meses if m is not None), Decimal(0))
    if total is None or soma != total:
        raise ValueError(f"{rotulo}: soma dos meses ({soma}) diferente do total da tabela ({total})")


def extrair_municipal(html: str, ano: int) -> dict[str, list[Decimal | None]]:
    """Valores mensais dos 12 municípios da RI na tabela do PA; município sem linha fica de fora."""
    saida: dict[str, list[Decimal | None]] = {}
    for linha in _ler(html).linhas:
        if len(linha) != 2 + MESES:
            continue
        codigo = _CODIGO_POR_NOME.get(_chave_nome(linha[0]))
        if codigo is None:
            continue
        if codigo in saida:
            raise ValueError(f"{ano}: município repetido na tabela: {linha[0]}")
        meses = [valor_brl(c) for c in linha[1 : 1 + MESES]]
        _conferir_total(f"{ano} {linha[0]}", meses, valor_brl(linha[-1]))
        saida[codigo] = meses
    return saida


def extrair_nacional(html: str, ano: int) -> Decimal:
    """Total anual do rodapé `Total:` da tabela por estado."""
    rodapes = [r for r in _ler(html).rodape if r and r[0].startswith("Total")]
    if len(rodapes) != 1 or len(rodapes[0]) != 2 + MESES:
        raise ValueError(f"{ano}: rodapé 'Total:' ausente ou com formato inesperado")
    rodape = rodapes[0]
    meses = [valor_brl(c) for c in rodape[1 : 1 + MESES]]
    total = valor_brl(rodape[-1])
    _conferir_total(f"{ano} Brasil", meses, total)
    assert total is not None
    return total


def baixar(url: str, destino: Path, contexto: ssl.SSLContext) -> None:
    """GET com User-Agent de navegador (a ANM recusa sem); guarda o corpo original comprimido."""
    requisicao = Request(url, headers={"User-Agent": AGENTE})
    with urlopen(requisicao, timeout=120, context=contexto) as resposta:
        if resposta.status != 200:
            raise ValueError(f"{url}: HTTP {resposta.status}")
        corpo = resposta.read()
    destino.write_bytes(gzip.compress(corpo, mtime=0))


def ler_html(arquivo: Path) -> tuple[str, str]:
    """(texto, SHA-256 do HTML original): o hash é do corpo HTTP, não do arquivo comprimido."""
    corpo = gzip.decompress(arquivo.read_bytes())
    return corpo.decode("utf-8"), hashlib.sha256(corpo).hexdigest()


def gerar(pasta: Path, anos: list[int], consultado_em: str) -> tuple[list[dict], list[dict]]:
    mensais: list[dict] = []
    nacionais: list[dict] = []
    for ano in anos:
        html, sha = ler_html(pasta / f"anm-pa-{ano}.html.gz")
        for codigo, meses in sorted(extrair_municipal(html, ano).items()):
            for mes, valor in enumerate(meses, 1):
                if valor is None:
                    continue
                mensais.append(
                    {
                        "municipio_id": codigo,
                        "ano": ano,
                        "mes": mes,
                        "valor": f"{valor:.2f}",
                        "documento": f"ANM Extra: Arrecadação CFEM por Ano/Estado, PA, {ano}; tabela municipal",
                        "url": url_municipal(ano),
                        "consultado_em": consultado_em,
                        "sha256": sha,
                    }
                )
        html, sha = ler_html(pasta / f"anm-brasil-{ano}.html.gz")
        nacionais.append(
            {
                "ano": ano,
                "valor": f"{extrair_nacional(html, ano):.2f}",
                "documento": f"ANM Extra: Arrecadação CFEM por Ano/Estado, Brasil, {ano}",
                "url": url_nacional(ano),
                "consultado_em": consultado_em,
                "sha256": sha,
            }
        )
    return mensais, nacionais


def comparar(anteriores: list[dict], novas: list[dict], chave: tuple[str, ...]) -> list[str]:
    """Diferenças de valor nas chaves presentes nas duas versões; chaves novas não são diferença."""
    antigas = {tuple(r[c] for c in chave): r["valor"] for r in anteriores}
    return [
        f"{tuple(r[c] for c in chave)}: {antigas[k]} → {r['valor']}"
        for r in novas
        if (k := tuple(r[c] for c in chave)) in antigas and Decimal(antigas[k]) != Decimal(r["valor"])
    ]


def _anos(texto: str) -> list[int]:
    inicio, _, fim = texto.partition("-")
    return list(range(int(inicio), int(fim or inicio) + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pasta", type=Path, required=True, help="Pasta das páginas capturadas (.html.gz)")
    parser.add_argument("--anos", required=True, help="Ano ou faixa, por exemplo 2008-2025")
    parser.add_argument("--certificado", type=Path, help="Certificado intermediário da ANM (cadeia incompleta)")
    parser.add_argument("--sem-baixar", action="store_true", help="Só extrai das páginas já capturadas")
    parser.add_argument("--consultado-em", default=date.today().isoformat())
    parser.add_argument("--mensal", type=Path, default=Path("data/referencia-cfem-mensal-anm.json"))
    parser.add_argument("--nacional", type=Path, default=Path("data/referencia-cfem-nacional-anm.json"))
    args = parser.parse_args()
    anos = _anos(args.anos)
    if not args.sem_baixar:
        args.pasta.mkdir(parents=True, exist_ok=True)
        contexto = ssl.create_default_context()
        if args.certificado:
            contexto.load_verify_locations(cafile=str(args.certificado))
        for ano in anos:
            for url, nome in ((url_municipal(ano), f"anm-pa-{ano}"), (url_nacional(ano), f"anm-brasil-{ano}")):
                baixar(url, args.pasta / f"{nome}.html.gz", contexto)
                print(f"baixado {nome}")
                time.sleep(1)  # uma requisição por vez, sem pressa: o servidor é público e lento
    mensais, nacionais = gerar(args.pasta, anos, args.consultado_em)
    diferencas = []
    for caminho, novas, chave in (
        (args.mensal, mensais, ("municipio_id", "ano", "mes")),
        (args.nacional, nacionais, ("ano",)),
    ):
        if caminho.exists():
            diferencas += comparar(json.loads(caminho.read_text(encoding="utf-8")), novas, chave)
        caminho.write_text(json.dumps(novas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(mensais)} células municipais e {len(nacionais)} totais nacionais de {anos[0]} a {anos[-1]}")
    for linha in diferencas:
        print("diferença em relação à versão anterior:", linha)
    return 1 if diferencas else 0


if __name__ == "__main__":
    raise SystemExit(main())
