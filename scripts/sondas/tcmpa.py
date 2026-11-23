"""Sonda: confere o que o site do TCM-PA oferece como dado aberto sobre orçamento e despesa municipal.

Script de teste/laboratório (não é o produto). Responde ao conflito B4 de
docs/regras-de-negocio/pendencias.md (o PB-08 do backlog cita o TCM-PA como fonte; as regras só têm
o SICONFI, RN-FNT-04). Não baixa dados de municípios: só verifica se existe portal de dados abertos ou
API, e em que forma o TCM-PA publica o que publica (painel, exportação de grade, sistema com login).

Uso:
    uv run python -m scripts.sondas.tcmpa [--saida output/sonda-tcmpa.json]
"""

from __future__ import annotations

import argparse
import re
import socket
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

import httpx

from scripts.comum.arquivos import escrever_json

SAIDA_PADRAO = Path("output/sonda-tcmpa.json")
SITE = "https://www.tcmpa.tc.br"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# Páginas do site que poderiam trazer dado municipal (achadas no menu da página inicial em 19/11/2026).
PAGINAS = {
    "inicio": "/",
    "portal_transparencia": "/portal-da-transparencia/",
    "raio_x_municipios": "/raio-x-dos-municipios/",
    "raio_x_transicao_2024_2025": "/raio-x-dos-municipios/transicao-2024-2025/",
    "raio_x_saneamento": "/raio-x-dos-municipios/saneamento-basico/",
    "mural_licitacoes_grade": "/portalsc/LISTAGEM_LICITACOES_CONTRATOS_GRID/",
    "geo_obras": "/portal-do-gestor/geo-obras-tcm-pa/",
    "e_contas_analisador": "/portal-do-gestor/e-contas-analisador/",
}
# Termos procurados na busca do próprio site (API do WordPress).
TERMOS_BUSCA = ["dados abertos", "orçamento", "despesa por função", "API"]
# Endereços que um portal de dados abertos costuma ter; a sonda confere se o nome existe no DNS.
HOSTS_CANDIDATOS = ["dadosabertos.tcm.pa.gov.br", "api.tcm.pa.gov.br", "dados.tcmpa.tc.br", "api.tcmpa.tc.br"]

_EXPORTACAO = re.compile(r"_config_(csv|json|xls|xml|pdf)\.php", re.IGNORECASE)
_POWER_BI = re.compile(r"app\.powerbi\.com/view", re.IGNORECASE)
_ARQUIVO = re.compile(r'href="([^"]+\.(?:csv|xlsx?|json|zip|ods))"', re.IGNORECASE)
_EXECUTAVEL = re.compile(r'href="([^"]+\.exe)"', re.IGNORECASE)


def classificar_pagina(html: str) -> dict:
    """Diz em que forma a página publica dados: exportação de grade, painel Power BI, arquivo, programa.

    `arquivos_para_baixar` lista links com extensão de dado ou zip; o tipo não diz o conteúdo (no e-Contas,
    em 19/11/2026, os zips eram instaladores e leiautes de envio, não dados de municípios).
    """
    return {
        "exportacoes_da_grade": sorted({m.lower() for m in _EXPORTACAO.findall(html)}),
        "paineis_power_bi": len(set(re.findall(r'app\.powerbi\.com/view\?r=[^"&\s]+', html))),
        "arquivos_para_baixar": sorted(set(_ARQUIVO.findall(html))),
        "programas_para_baixar": sorted(set(_EXECUTAVEL.findall(html))),
        "cita_dados_abertos": "dados abertos" in html.lower(),
        "tem_power_bi": bool(_POWER_BI.search(html)),
    }


def _pagina(cliente: httpx.Client, nome: str, caminho: str) -> dict:
    linha: dict = {"pagina": nome, "url": SITE + caminho, "status": None, "erro": None}
    try:
        resposta = cliente.get(SITE + caminho, timeout=45)
        linha["status"] = resposta.status_code
        linha["url_final"] = str(resposta.url)
        linha.update(classificar_pagina(resposta.text))
    except httpx.HTTPError as erro:
        linha["erro"] = str(erro)
    return linha


def _busca(cliente: httpx.Client, termo: str) -> dict:
    url = f"{SITE}/wp-json/wp/v2/search?per_page=20&search={quote(termo)}"
    try:
        resposta = cliente.get(url, timeout=45)
        resposta.raise_for_status()
        itens = resposta.json()
        return {"termo": termo, "status": resposta.status_code, "resultados": len(itens),
                "titulos": [str(i.get("title", "")) for i in itens], "erro": None}
    except (httpx.HTTPError, ValueError) as erro:
        return {"termo": termo, "status": None, "resultados": None, "titulos": [], "erro": str(erro)}


def _host_existe(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    args = parser.parse_args(argv)
    with httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as cliente:
        paginas = [_pagina(cliente, n, c) for n, c in PAGINAS.items()]
        buscas = [_busca(cliente, t) for t in TERMOS_BUSCA]
    hosts = {h: _host_existe(h) for h in HOSTS_CANDIDATOS}
    escrever_json(args.saida, {
        "checked_at_utc": datetime.now(UTC).isoformat(), "source": "TCM-PA (site institucional)",
        "pergunta": "O TCM-PA publica orçamento ou despesa municipal como dado aberto (API ou arquivo)?",
        "paginas": paginas, "buscas_no_site": buscas, "hosts_candidatos_no_dns": hosts})
    for p in paginas:
        formas = [f"grade:{','.join(p.get('exportacoes_da_grade', []))}" if p.get("exportacoes_da_grade") else "",
                  f"power_bi:{p['paineis_power_bi']}" if p.get("paineis_power_bi") else "",
                  f"arquivos:{len(p["arquivos_para_baixar"])}" if p.get("arquivos_para_baixar") else "",
                  f"programas:{len(p['programas_para_baixar'])}" if p.get("programas_para_baixar") else ""]
        print(f"{p['pagina']:28} {p['status'] or p['erro']} {' '.join(f for f in formas if f)}")
    for b in buscas:
        print(f"busca '{b['termo']}': {b['resultados']} -> {b['titulos'][:5]}")
    print("hosts:", hosts)
    print(f"salvo em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
