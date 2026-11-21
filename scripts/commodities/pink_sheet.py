"""Coleta os preços mensais de ferro e cobre do Pink Sheet do World Bank (script de teste/laboratório).

Não é o produto. Faz o que RN-FNT-05 descreve: localiza o arquivo mensal na página do World Bank (o endereço
traz um código que muda a cada edição), baixa, lê as colunas pelo nome, valida o contrato e publica uma camada
provisória no mesmo formato de `fred.py`. Cada edição baixada é guardada datada, com endereço e SHA-256.
Se o endereço ou as colunas não forem achados, falha com aviso e não altera o lote publicado.

O ferro sai em duas séries separadas (RN-TMP-13, RN-TMP-14; corrigido em 21/11/2026): o contrato anual em
¢/dmtu de 1985 a 2005 (`preco_minerio_ferro_contrato`) e o spot mensal em $/dmt desde dezembro de 2008
(`preco_minerio_ferro_spot`); o trecho de 2006 a novembro de 2008 fica fora. O cobre sai mensal desde 2000.

O FRED (`fred.py`) fica só como reserva da spot e do cobre e nunca é emendado com esta série.

Uso:
    uv run python -m scripts.commodities.pink_sheet
"""

from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
import re
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from scripts.comum.arquivos import (
    PASTA_PADRAO,
    agora,
    escrever_json,
    escrever_json_atomico,
    id_execucao,
    iso_utc,
)

PAGINA = "https://www.worldbank.org/en/research/commodity-markets"
PADRAO_LINK = re.compile(r"https://thedocs\.worldbank\.org/[^\"'\s<>]*CMO-Historical-Data-Monthly\.xlsx")
ABA = "Monthly Prices"
CABECALHO_NAVEGADOR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

# coluna da planilha -> unidade que a planilha traz e que se espera.
COLUNAS = {"Iron ore, cfr spot": "($/dmtu)", "Copper": "($/mt)"}
# Recortes de RN-TMP-13 e RN-TMP-14: o ferro são duas séries separadas e o trecho de 2006 a nov/2008 fica fora.
CONTRATO_ANOS = (1985, 2005)          # contrato anual, ¢/dmtu (o Pink Sheet repete o valor anual nos 12 meses)
SPOT_INICIO = (2008, 12)              # spot mensal, $/dmt (62% Fe, cfr China)
COBRE_INICIO = (2000, 1)              # cobre mensal, período vigente desde 2000
IND_CONTRATO, IND_SPOT, IND_COBRE = "preco_minerio_ferro_contrato", "preco_minerio_ferro_spot", "preco_cobre"
UNIDADES = {IND_CONTRATO: "¢/dmtu", IND_SPOT: "USD/dmt", IND_COBRE: "USD/t"}

Buscar = Callable[[str], tuple[int, bytes]]


class ContratoPinkSheetError(Exception):
    """A página ou a planilha do World Bank mudou de forma."""


def buscar_http_bytes(url: str) -> tuple[int, bytes]:
    import httpx

    resposta = httpx.get(url, timeout=60, headers=CABECALHO_NAVEGADOR, follow_redirects=True)
    return resposta.status_code, resposta.content


def achar_link_mensal(html: str) -> str:
    achados = sorted(set(PADRAO_LINK.findall(html)))
    if len(achados) != 1:
        raise ContratoPinkSheetError(f"link do arquivo mensal: {len(achados)} achados na página")
    return achados[0]


def _ler_colunas(conteudo: bytes) -> dict[str, dict[tuple[int, int], float | None]]:
    """Lê as colunas de ferro e cobre da aba mensal, conferindo nomes, unidades e meses."""
    from openpyxl import load_workbook

    try:
        livro = load_workbook(io.BytesIO(conteudo), read_only=True, data_only=True)
        linhas_planilha = list(livro[ABA].iter_rows(values_only=True))
    except Exception as erro:
        raise ContratoPinkSheetError(f"planilha ilegível ou sem a aba {ABA!r}") from erro
    cabecalho = next((k for k, r in enumerate(linhas_planilha[:15]) if all(n in r for n in COLUNAS)), None)
    if cabecalho is None or cabecalho + 1 >= len(linhas_planilha):
        raise ContratoPinkSheetError("colunas de ferro e cobre não encontradas")
    nomes, unidades = linhas_planilha[cabecalho], linhas_planilha[cabecalho + 1]
    colunas: dict[str, dict[tuple[int, int], float | None]] = {}
    for nome, unidade in COLUNAS.items():
        coluna = nomes.index(nome)
        if str(unidades[coluna]).strip() != unidade:
            raise ContratoPinkSheetError(f"{nome}: unidade inesperada {unidades[coluna]!r}")
        valores: dict[tuple[int, int], float | None] = {}
        for r in linhas_planilha[cabecalho + 2:]:
            periodo = r[0]
            achado = re.fullmatch(r"(\d{4})M(\d{2})", periodo) if isinstance(periodo, str) else None
            if not achado:
                continue
            ano, mes = int(achado[1]), int(achado[2])
            if not 1 <= mes <= 12 or (ano, mes) in valores:
                raise ContratoPinkSheetError(f"{nome}: mês inválido ou duplicado ({periodo})")
            bruto = r[coluna]
            if isinstance(bruto, (int, float)) and not isinstance(bruto, bool):
                if not math.isfinite(bruto) or bruto < 0:
                    raise ContratoPinkSheetError(f"{nome}: preço inválido em {periodo}")
                valores[(ano, mes)] = float(bruto)
            else:
                valores[(ano, mes)] = None  # "…", "..", vazio: preservado como ausente
        colunas[nome] = valores
    return colunas


def _mensal(valores: dict[tuple[int, int], float | None], inicio: tuple[int, int], nome: str) -> list[tuple[int, int, float | None]]:
    """Meses a partir de `inicio`, sem lacuna na sequência."""
    meses = sorted(p for p in valores if p >= inicio)
    if not meses or meses[0] != inicio:
        raise ContratoPinkSheetError(f"{nome}: série não começa em {inicio[0]}-{inicio[1]:02d}")
    for (a1, m1), (a2, m2) in itertools.pairwise(meses):
        if a2 * 12 + m2 != a1 * 12 + m1 + 1:
            raise ContratoPinkSheetError(f"{nome}: lacuna na sequência mensal")
    return [(a, m, valores[(a, m)]) for a, m in meses]


def _contrato_anual(valores: dict[tuple[int, int], float | None]) -> list[tuple[int, None, float]]:
    """Valor anual do contrato: o Pink Sheet repete o preço anual nos 12 meses; qualquer variação falha o lote."""
    saida: list[tuple[int, None, float]] = []
    for ano in range(CONTRATO_ANOS[0], CONTRATO_ANOS[1] + 1):
        doze = {valores.get((ano, mes)) for mes in range(1, 13)}
        if len(doze) != 1 or None in doze:
            raise ContratoPinkSheetError(f"ferro, contrato: {ano} não tem um valor único nos 12 meses")
        saida.append((ano, None, doze.pop()))  # type: ignore[arg-type]
    return saida


def extrair_pink_sheet(conteudo: bytes, instante: str, edicao: str | None = None) -> list[dict]:
    """Observações de ferro (contrato e spot, separadas) e cobre, nos recortes de RN-TMP-13 e RN-TMP-14."""
    colunas = _ler_colunas(conteudo)
    ferro, cobre = colunas["Iron ore, cfr spot"], colunas["Copper"]
    series = {
        IND_CONTRATO: ("Iron ore, cfr spot (contrato anual)", _contrato_anual(ferro)),
        IND_SPOT: ("Iron ore, cfr spot (spot 62% Fe)", _mensal(ferro, SPOT_INICIO, "ferro, spot")),
        IND_COBRE: ("Copper", _mensal(cobre, COBRE_INICIO, "cobre")),
    }
    saida: list[dict] = []
    for indicador, (coluna, pontos) in series.items():
        if not any(v is not None for _, _, v in pontos):
            raise ContratoPinkSheetError(f"{indicador}: série sem valores")
        for ano, mes, valor in pontos:
            saida.append({
                "indicador": indicador, "municipio_id": None, "municipio_nome": None,
                "nivel_territorial": "global", "ano": ano, "mes": mes, "valor": valor,
                "unidade": UNIDADES[indicador],
                "natureza_valor": "ausente" if valor is None else "zero real" if valor == 0 else "informado",
                "estado_validacao": "provisório", "fonte": f"World Bank, Pink Sheet mensal, coluna {coluna}",
                "edicao_fonte": edicao, "atualizado_em": instante, "versao_tratamento": "2.0.0",
            })
    return saida


def executar_pink_sheet(pasta_dados: str | Path = PASTA_PADRAO, buscar: Buscar = buscar_http_bytes,
                        agora_fn: Callable[[], datetime] = agora) -> dict:
    pasta = Path(pasta_dados)
    pasta_rel, pasta_bruto, pasta_pub = pasta / "qualidade", pasta / "bruto" / "pink-sheet", pasta / "publicado"
    for p in (pasta_rel, pasta_bruto, pasta_pub):
        p.mkdir(parents=True, exist_ok=True)
    instante = iso_utc(agora_fn())
    execucao = id_execucao(instante)
    relatorio: dict = {
        "execucao": execucao, "atualizado_em": instante, "indicador": "commodities", "situacao": "bloqueado",
        "fonte": "World Bank, Pink Sheet mensal", "pagina": PAGINA, "arquivo_url": None, "arquivo_sha256": None,
        "linhas_lidas": 0, "nulos": 0, "anos": [], "faixa_valores": {},
        "divergencia_fonte_primaria": "Reconciliação independente pendente; valores provisórios",
        "erro": None,
    }
    try:
        status, corpo = buscar(PAGINA)
        if not 200 <= status < 300:
            raise ContratoPinkSheetError(f"página do World Bank: HTTP {status}")
        url = achar_link_mensal(corpo.decode("utf-8", errors="replace"))
        relatorio["arquivo_url"] = url
        status, conteudo = buscar(url)
        if not 200 <= status < 300 or not conteudo:
            raise ContratoPinkSheetError(f"arquivo mensal: HTTP {status}")
        relatorio["arquivo_sha256"] = hashlib.sha256(conteudo).hexdigest()
        (pasta_bruto / f"{execucao}-CMO-Historical-Data-Monthly.xlsx").write_bytes(conteudo)
        linhas = extrair_pink_sheet(conteudo, instante, edicao=relatorio["arquivo_sha256"][:12])
        relatorio["linhas_lidas"] = len(linhas)
        relatorio["nulos"] = sum(1 for l in linhas if l["valor"] is None)
        relatorio["anos"] = sorted({l["ano"] for l in linhas})
        for indicador in UNIDADES:
            valores = [l["valor"] for l in linhas if l["indicador"] == indicador and l["valor"] is not None]
            relatorio["faixa_valores"][indicador] = {"minimo": min(valores), "maximo": max(valores)}
        escrever_json_atomico(pasta_pub / "commodities.json", linhas, execucao)
        relatorio["situacao"] = "publicado_provisorio"
        return relatorio
    except Exception as erro:
        relatorio["erro"] = f"{type(erro).__name__}: {erro}"
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise
    finally:
        escrever_json(pasta_rel / f"{execucao}-commodities-pink-sheet.json", relatorio)


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args(argv)
    try:
        r = executar_pink_sheet()
    except Exception as erro:  # noqa: BLE001
        print(getattr(erro, "relatorio", {}).get("erro") or str(erro), file=sys.stderr)
        return 1
    print(json.dumps({"situacao": r["situacao"], "linhas": r["linhas_lidas"], "execucao": r["execucao"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
