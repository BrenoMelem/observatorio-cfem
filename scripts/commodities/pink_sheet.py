"""Coleta os preços mensais de ferro e cobre do Pink Sheet do World Bank (script de teste/laboratório).

Não é o produto. Faz o que RN-FNT-05 descreve: localiza o arquivo mensal na página do World Bank (o endereço
traz um código que muda a cada edição), baixa, lê as colunas pelo nome, valida o contrato e publica uma camada
provisória no mesmo formato de `fred.py`. Cada edição baixada é guardada datada, com endereço e SHA-256.
Se o endereço ou as colunas não forem achados, falha com aviso e não altera o lote publicado.

O FRED (`fred.py`) fica só como reserva e nunca é emendado com esta série.

Uso:
    uv run python -m scripts.commodities.pink_sheet
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from scripts.comum.arquivos import (
    PASTA_PADRAO, agora, escrever_json, escrever_json_atomico, id_execucao, iso_utc,
)

PAGINA = "https://www.worldbank.org/en/research/commodity-markets"
PADRAO_LINK = re.compile(r"https://thedocs\.worldbank\.org/[^\"'\s<>]*CMO-Historical-Data-Monthly\.xlsx")
ABA = "Monthly Prices"
CABECALHO_NAVEGADOR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

# coluna da planilha -> indicador; "unidade_planilha" é o rótulo que a planilha traz e que se espera.
SERIES = {
    "Iron ore, cfr spot": {"indicador": "preco_minerio_ferro", "unidade": "USD/dmt", "unidade_planilha": "($/dmtu)"},
    "Copper": {"indicador": "preco_cobre", "unidade": "USD/t", "unidade_planilha": "($/mt)"},
}

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


def extrair_pink_sheet(conteudo: bytes, instante: str, edicao: str | None = None) -> list[dict]:
    from openpyxl import load_workbook

    try:
        livro = load_workbook(io.BytesIO(conteudo), read_only=True, data_only=True)
        linhas_planilha = list(livro[ABA].iter_rows(values_only=True))
    except Exception as erro:  # noqa: BLE001
        raise ContratoPinkSheetError(f"planilha ilegível ou sem a aba {ABA!r}") from erro
    cabecalho = next((k for k, r in enumerate(linhas_planilha[:15]) if all(n in r for n in SERIES)), None)
    if cabecalho is None or cabecalho + 1 >= len(linhas_planilha):
        raise ContratoPinkSheetError("colunas de ferro e cobre não encontradas")
    nomes, unidades = linhas_planilha[cabecalho], linhas_planilha[cabecalho + 1]
    colunas = {}
    for nome, config in SERIES.items():
        coluna = nomes.index(nome)
        if str(unidades[coluna]).strip() != config["unidade_planilha"]:
            raise ContratoPinkSheetError(f"{nome}: unidade inesperada {unidades[coluna]!r}")
        colunas[nome] = coluna
    saida: list[dict] = []
    for nome, config in SERIES.items():
        vistos: set[tuple[int, int]] = set()
        serie: list[dict] = []
        for r in linhas_planilha[cabecalho + 2:]:
            periodo = r[0]
            achado = re.fullmatch(r"(\d{4})M(\d{2})", periodo) if isinstance(periodo, str) else None
            if not achado:
                continue
            ano, mes = int(achado[1]), int(achado[2])
            if not 1 <= mes <= 12 or (ano, mes) in vistos:
                raise ContratoPinkSheetError(f"{nome}: mês inválido ou duplicado ({periodo})")
            vistos.add((ano, mes))
            bruto = r[colunas[nome]]
            if isinstance(bruto, (int, float)) and not isinstance(bruto, bool):
                if not math.isfinite(bruto) or bruto < 0:
                    raise ContratoPinkSheetError(f"{nome}: preço inválido em {periodo}")
                valor = float(bruto)
            else:
                valor = None  # "…", "..", vazio: preservado como ausente
            serie.append({
                "indicador": config["indicador"], "municipio_id": None, "municipio_nome": None,
                "nivel_territorial": "global", "ano": ano, "mes": mes, "valor": valor,
                "unidade": config["unidade"],
                "natureza_valor": "ausente" if valor is None else "zero real" if valor == 0 else "informado",
                "estado_validacao": "provisório", "fonte": f"World Bank, Pink Sheet mensal, coluna {nome}",
                "edicao_fonte": edicao, "atualizado_em": instante, "versao_tratamento": "1.0.0",
            })
        if not any(l["valor"] is not None for l in serie):
            raise ContratoPinkSheetError(f"{nome}: série sem valores")
        serie.sort(key=lambda l: (l["ano"], l["mes"]))
        for anterior, atual in zip(serie, serie[1:]):
            if atual["ano"] * 12 + atual["mes"] != anterior["ano"] * 12 + anterior["mes"] + 1:
                raise ContratoPinkSheetError(f"{nome}: lacuna na sequência mensal")
        saida.extend(serie)
    return saida


def anos_com_valor_repetido(linhas: list[dict], indicador: str) -> list[int]:
    """Anos com 12 meses de valor idêntico: o World Bank repete o valor anual em cada mês (RN-TMP-13)."""
    por_ano: dict[int, list] = {}
    for l in linhas:
        if l["indicador"] == indicador:
            por_ano.setdefault(l["ano"], []).append(l["valor"])
    return sorted(a for a, v in por_ano.items() if len(v) == 12 and None not in v and len(set(v)) == 1)


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
        "linhas_lidas": 0, "nulos": 0, "anos": [], "anos_valor_repetido_ferro": [], "faixa_valores": {},
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
        relatorio["anos_valor_repetido_ferro"] = anos_com_valor_repetido(linhas, "preco_minerio_ferro")
        for nome, config in SERIES.items():
            valores = [l["valor"] for l in linhas if l["indicador"] == config["indicador"] and l["valor"] is not None]
            relatorio["faixa_valores"][nome] = {"minimo": min(valores), "maximo": max(valores)}
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
