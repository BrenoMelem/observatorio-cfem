"""Lê a planilha municipal do SEEG e extrai o recorte dos 12 municípios da RI Carajás (script de teste/laboratório).

Não é o produto. Faz o que RN-FNT-14 e RN-FON-15 descrevem: a planilha bruta (centenas de MB) fica fora do Git;
só o recorte agregado e os metadados (edição, endereço, data, SHA-256 e a citação do SEEG) são o resultado.

A aba `Dados` traz uma linha por emissão/setor/categoria/subcategoria/recorte/atividade/município e uma coluna
por ano. A coluna `ID Território` vem como "1" + código IBGE de 7 dígitos (por exemplo, 14104428 para Candói/PR);
o código do município é reconstituído, não copiado. Emissão, remoção e bunker ficam separados (não se compensam).

Uso (o endereço é o que o mantenedor indicou em 10/11/2026; a leitura de 229 MB leva alguns minutos):
    uv run python -m scripts.emissoes.seeg
    uv run python -m scripts.emissoes.seeg --arquivo CAMINHO/Dados-municipais-resumido-CO2e-GWP-AR5-14.0.xlsx
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Callable

from scripts.comum.arquivos import PASTA_PADRAO, agora, escrever_json, escrever_json_atomico, id_execucao, iso_utc
from scripts.comum.municipios import MUNICIPIOS

URL_MUNICIPAL = ("https://seeg.obass.haus/wp-content/uploads/2026/11/"
                 "Dados-municipais-resumido-CO2e-GWP-AR5-14.0.xlsx")
ABA = "Dados"
COLUNAS_OBRIGATORIAS = ("Emissão/Remoção/Bunker", "Setor de emissão", "Município", "ID Território")
CITACAO = ("Fonte: SEEG – Sistema de Estimativa de Emissões e Remoções de Gases de Efeito Estufa, "
           "Observatório do Clima, acessado em {data} – seeg.eco.br")
CABECALHO_NAVEGADOR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

Baixar = Callable[[str, Path], None]


class ContratoSeegError(Exception):
    """A planilha do SEEG mudou de forma."""


def baixar_http(url: str, destino: Path) -> None:
    import httpx

    destino.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=600, headers=CABECALHO_NAVEGADOR, follow_redirects=True) as resposta:
        if not 200 <= resposta.status_code < 300:
            raise ContratoSeegError(f"download: HTTP {resposta.status_code}")
        with destino.open("wb") as saida:
            for pedaco in resposta.iter_bytes(1 << 20):
                saida.write(pedaco)


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for pedaco in iter(lambda: arquivo.read(1 << 20), b""):
            h.update(pedaco)
    return h.hexdigest()


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


def codigo_ibge(id_territorio) -> str | None:
    """`ID Território` = '1' + IBGE de 7 dígitos; devolve o IBGE ou None se o formato não for esse."""
    texto = str(id_territorio).strip()
    texto = texto[:-2] if texto.endswith(".0") else texto
    return texto[1:] if re.fullmatch(r"1\d{7}", texto) else None


def edicao_do_nome(nome: str) -> str | None:
    achado = re.search(r"-(\d+\.\d+)\.xlsx$", nome)
    return achado[1] if achado else None


def extrair_seeg(caminho: Path, instante: str, edicao: str | None = None) -> tuple[list[dict], dict]:
    from openpyxl import load_workbook

    try:
        livro = load_workbook(caminho, read_only=True, data_only=True)
        aba = livro[ABA]
    except Exception as erro:  # noqa: BLE001
        raise ContratoSeegError(f"planilha ilegível ou sem a aba {ABA!r}") from erro
    linhas = aba.iter_rows(values_only=True)
    cabecalho = next(linhas, None)
    if not cabecalho:
        raise ContratoSeegError("aba sem cabeçalho")
    nomes = [str(c).strip() if c is not None else "" for c in cabecalho]
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in nomes]
    anos_col = {i: int(n) for i, n in enumerate(nomes) if re.fullmatch(r"\d{4}", n)}
    if faltando or not anos_col:
        raise ContratoSeegError(f"colunas ausentes: {faltando or 'anos'}")
    i_tipo, i_setor, i_nome, i_id = (nomes.index(c) for c in COLUNAS_OBRIGATORIAS)
    alvo = set(MUNICIPIOS)
    soma: dict[tuple, float] = {}
    nomes_vistos: dict[str, str] = {}
    lidas = casadas = 0
    for r in linhas:
        lidas += 1
        ibge = codigo_ibge(r[i_id])
        if ibge not in alvo:
            continue
        casadas += 1
        nomes_vistos.setdefault(ibge, str(r[i_nome]))
        for i, ano in anos_col.items():
            v = r[i]
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                chave = (str(r[i_tipo]), str(r[i_setor]), ibge, ano)
                soma[chave] = soma.get(chave, 0.0) + float(v)
    divergentes = {c: n for c, n in nomes_vistos.items()
                   if _sem_acento(MUNICIPIOS[c]) not in _sem_acento(n)}
    saida = [{
        "indicador": "emissao_seeg_co2e", "municipio_id": ibge, "municipio_nome": MUNICIPIOS[ibge],
        "nivel_territorial": "municipio", "ano": ano, "mes": None, "valor": valor,
        "unidade": "CO2e (GWP-AR5), unidade da planilha a confirmar", "natureza_valor": "informado",
        "tipo": tipo, "setor": setor, "estado_validacao": "provisório",
        "fonte": "SEEG, Dados municipais resumido CO2e GWP-AR5", "edicao_fonte": edicao,
        "atualizado_em": instante, "versao_tratamento": "1.0.0",
    } for (tipo, setor, ibge, ano), valor in sorted(soma.items(), key=lambda kv: (kv[0][2], kv[0][0], kv[0][1], kv[0][3]))]
    resumo = {
        "linhas_lidas": lidas, "linhas_do_recorte": casadas,
        "municipios_encontrados": sorted(nomes_vistos), "municipios_ausentes": sorted(alvo - set(nomes_vistos)),
        "nomes_divergentes": divergentes, "anos": [min(anos_col.values()), max(anos_col.values())],
        "colunas": len(nomes),
    }
    return saida, resumo


def executar_seeg(pasta_dados: str | Path = PASTA_PADRAO, url: str = URL_MUNICIPAL, arquivo: Path | None = None,
                  baixar: Baixar = baixar_http, agora_fn: Callable[[], datetime] = agora) -> dict:
    pasta = Path(pasta_dados)
    pasta_rel, pasta_bruto, pasta_pub = pasta / "qualidade", pasta / "bruto" / "seeg", pasta / "publicado"
    for p in (pasta_rel, pasta_bruto, pasta_pub):
        p.mkdir(parents=True, exist_ok=True)
    instante = iso_utc(agora_fn())
    execucao = id_execucao(instante)
    relatorio: dict = {
        "execucao": execucao, "atualizado_em": instante, "indicador": "emissoes-seeg", "situacao": "bloqueado",
        "arquivo_url": None if arquivo else url, "arquivo_local": None, "arquivo_bytes": None,
        "arquivo_sha256": None, "edicao": None, "citacao": CITACAO.format(data=instante[:10]),
        "orientacao": "O bruto fica fora do Git (RN-FON-15); só este relatório e o recorte são resultado.",
        "erro": None,
    }
    try:
        if arquivo is None:
            nome = url.rsplit("/", 1)[-1]
            arquivo = pasta_bruto / f"{execucao}-{nome}"
            baixar(url, arquivo)
        arquivo = Path(arquivo)
        relatorio["arquivo_local"] = str(arquivo)
        relatorio["arquivo_bytes"] = arquivo.stat().st_size
        relatorio["arquivo_sha256"] = sha256_arquivo(arquivo)
        relatorio["edicao"] = edicao_do_nome(arquivo.name)
        linhas, resumo = extrair_seeg(arquivo, instante, relatorio["edicao"])
        relatorio.update(resumo)
        if not linhas:
            raise ContratoSeegError("nenhuma linha dos 12 municípios na planilha")
        escrever_json_atomico(pasta_pub / "emissoes-seeg.json", linhas, execucao)
        relatorio["linhas_publicadas"] = len(linhas)
        relatorio["situacao"] = "publicado_provisorio"
        return relatorio
    except Exception as erro:
        relatorio["erro"] = f"{type(erro).__name__}: {erro}"
        erro.relatorio = relatorio  # type: ignore[attr-defined]
        raise
    finally:
        escrever_json(pasta_rel / f"{execucao}-emissoes-seeg.json", relatorio)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arquivo", type=Path, help="planilha municipal já baixada (evita o download)")
    ap.add_argument("--url", default=URL_MUNICIPAL)
    args = ap.parse_args(argv)
    try:
        r = executar_seeg(url=args.url, arquivo=args.arquivo)
    except Exception as erro:  # noqa: BLE001
        print(getattr(erro, "relatorio", {}).get("erro") or str(erro), file=sys.stderr)
        return 1
    print(json.dumps({"situacao": r["situacao"], "linhas": r["linhas_publicadas"], "execucao": r["execucao"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
