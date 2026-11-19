"""Sonda: confere se o IBGE (Censo 2022) tem limites e dados por bairro e por distrito nos 12 municípios.

Script de teste/laboratório (não é o produto). Responde ao conflito B5 de
docs/regras-de-negocio/pendencias.md (PB-21 a PB-23 pedem bairros e distritos; as regras param no
município). Baixa as malhas de bairros e de distritos do Pará do Censo 2022 (arquivos de poucos
centenas de KB; a de setores censitários tem cerca de 24 MB) para tmp/, lê só a tabela de atributos (.dbf) e conta as unidades por município;
depois consulta no SIDRA a tabela 9923 (população residente por situação do domicílio), que o IBGE
publica também por bairro (N102) e por distrito (N10).

Uso:
    uv run python -m scripts.sondas.ibge_bairros [--saida output/sonda-ibge-bairros.json]
"""

from __future__ import annotations

import argparse
import io
import struct
import sys
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import httpx

from scripts.comum.arquivos import escrever_json
from scripts.comum.municipios import MUNICIPIOS

SAIDA_PADRAO = Path("output/sonda-ibge-bairros.json")
PASTA_DOWNLOAD = Path("tmp/ibge-bairros")
BASE = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/"
        "malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/")
MALHAS = {"bairros": BASE + "bairros/shp/UF/PA_bairros_CD2022.zip",
          "distritos": BASE + "distritos/shp/UF/PA_distritos_CD2022.zip",
          "setores": BASE + "setores/shp/UF/PA_setores_CD2022.zip"}
CAMPO_NOME = {"bairros": "NM_BAIRRO", "distritos": "NM_DIST", "setores": "CD_SETOR"}
SIDRA = "https://servicodados.ibge.gov.br/api/v3/agregados/9923/periodos/2022/variaveis/93"
NIVEIS_SIDRA = {"bairros": "N102", "distritos": "N10"}


def ler_dbf(conteudo: bytes, codificacao: str = "utf-8") -> list[dict[str, str]]:
    """Lê os registros de um arquivo .dbf (dBase III), sem dependência externa."""
    n_registros, tam_cabecalho, tam_registro = struct.unpack("<IHH", conteudo[4:12])
    campos: list[tuple[str, int]] = []
    pos = 32
    while conteudo[pos] != 0x0D:
        nome = conteudo[pos:pos + 11].split(b"\x00")[0].decode("ascii")
        campos.append((nome, conteudo[pos + 16]))
        pos += 32
    registros = []
    for i in range(n_registros):
        inicio = tam_cabecalho + i * tam_registro
        bruto = conteudo[inicio:inicio + tam_registro]
        if bruto[:1] == b"*":  # registro apagado
            continue
        linha, p = {}, 1
        for nome, tamanho in campos:
            linha[nome] = bruto[p:p + tamanho].decode(codificacao, errors="replace").strip()
            p += tamanho
        registros.append(linha)
    return registros


def contar_por_municipio(registros: list[dict[str, str]], campo: str = "CD_MUN") -> dict[str, int]:
    """Quantas unidades (bairros ou distritos) cada um dos 12 municípios tem na malha."""
    contagem = Counter(r.get(campo, "") for r in registros)
    return {codigo: contagem.get(codigo, 0) for codigo in MUNICIPIOS}


def _malha(cliente: httpx.Client, nome: str, url: str) -> dict:
    resposta = cliente.get(url, timeout=120)
    resposta.raise_for_status()
    PASTA_DOWNLOAD.mkdir(parents=True, exist_ok=True)
    (PASTA_DOWNLOAD / Path(url).name).write_bytes(resposta.content)
    with zipfile.ZipFile(io.BytesIO(resposta.content)) as arquivo:
        dbf = next(n for n in arquivo.namelist() if n.lower().endswith(".dbf"))
        registros = ler_dbf(arquivo.read(dbf))
    campo_nome = CAMPO_NOME[nome]
    exemplos = {c: sorted(r.get(campo_nome, "") for r in registros if r.get("CD_MUN") == c)[:5]
                for c in ("1505536", "1502152")}
    return {"url": url, "bytes": len(resposta.content), "registros_no_para": len(registros),
            "campos": sorted(registros[0]) if registros else [],
            "municipios_no_para": len({r.get("CD_MUN") for r in registros}),
            "por_municipio": contar_por_municipio(registros), "exemplos_parauapebas_canaa": exemplos}


def _sidra(cliente: httpx.Client, nivel: str) -> dict[str, int]:
    resultado = {}
    for codigo in MUNICIPIOS:
        resposta = cliente.get(SIDRA, params={"localidades": f"{nivel}[N6[{codigo}]]"}, timeout=90)
        resposta.raise_for_status()
        dados = resposta.json()
        resultado[codigo] = len(dados[0]["resultados"][0]["series"]) if dados else 0
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args(argv)
    with httpx.Client(follow_redirects=True) as cliente:
        malhas = {n: _malha(cliente, n, u) for n, u in MALHAS.items()}
        sidra = {n: _sidra(cliente, nivel) for n, nivel in NIVEIS_SIDRA.items()}
    escrever_json(args.saida, {
        "checked_at_utc": datetime.now(UTC).isoformat(), "source": "IBGE, Censo 2022 (malhas e SIDRA 9923)",
        "pergunta": "Há limites e dados por bairro e por distrito para os 12 municípios?",
        "malhas": malhas, "sidra_9923_unidades_com_dado": sidra})
    print(f"{'municipio':28} {'bairros':>8} {'sidra_b':>8} {'distritos':>9} {'sidra_d':>8} {'setores':>8}")
    for codigo, nome in MUNICIPIOS.items():
        print(f"{nome:28} {malhas['bairros']['por_municipio'][codigo]:>8} {sidra['bairros'][codigo]:>8} "
              f"{malhas['distritos']['por_municipio'][codigo]:>9} {sidra['distritos'][codigo]:>8} "
              f"{malhas['setores']['por_municipio'][codigo]:>8}")
    print("campos bairros:", malhas["bairros"]["campos"])
    print("municípios do Pará com bairros na malha:", malhas["bairros"]["municipios_no_para"])
    print(f"salvo em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
