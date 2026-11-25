"""Coleta anexos da DCA do SICONFI (I-C receitas e I-D despesas) para os 12 municípios da RI Carajás.

Script de teste e laboratório, não é código de produção. Consulta a API pública do SICONFI
(sem login e sem chave), uma vez por município, anexo e exercício, e grava um CSV longo com
uma linha por (município, exercício, anexo, coluna, conta). O CSV é gravado fora do Git
(por padrão em `output/`, que não é versionado).

Serve para verificar a composição da receita corrente (Anexo I-C), a cota-parte do ICMS
(conta RO1.7.2.1.50.0.0) e o investimento (Anexo I-D, conta DO4.4.00.00.00.00). Não calcula
indicadores nem decide método: isso é decisão do mantenedor (RN-ENT-12).

Uso:
    uv run python -m scripts.financas.dca_anexos --inicio 2013 --fim 2025 --saida output/financas/dca_anexos.csv
"""

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from scripts.financas.dca_csv import MUNICIPIOS

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
ANEXOS_PADRAO = ("I-C", "I-D")
CABECALHO = ["municipio", "cod_ibge", "exercicio", "anexo", "coluna", "cod_conta", "conta", "valor"]


class ContratoSiconfiError(RuntimeError):
    """A resposta da API não tem o município, o exercício ou o anexo pedidos."""


def nome_do_anexo(anexo: str, exercicio: int) -> str:
    """Nome do anexo como a API o espera.

    Desde 2014 o nome é "DCA-Anexo I-C"; em 2013 é "Anexo I-C" (AGENTS.md, seção de fontes).
    """
    return f"Anexo {anexo}" if exercicio == 2013 else f"DCA-Anexo {anexo}"


def consultar_anexo(anexo: str, exercicio: int, id_ente: int) -> dict:
    """Devolve a resposta da API para um município, exercício e anexo."""
    params = urllib.parse.urlencode(
        {"an_exercicio": exercicio, "no_anexo": nome_do_anexo(anexo, exercicio), "id_ente": id_ente}
    )
    req = urllib.request.Request(f"{API}?{params}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def _inteiro(valor: object) -> int | None:
    """Inteiro do campo, ou None se vier nulo ou malformado (o item vira divergência de contrato, não queda)."""
    try:
        return int(valor)  # type: ignore[call-overload]
    except (TypeError, ValueError):
        return None


def linhas_do_anexo(payload: dict, municipio: str, codigo: int, anexo: str, exercicio: int) -> list[dict]:
    """Transforma a resposta em linhas planas e confere o contrato da API.

    Levanta ContratoSiconfiError se algum item trouxer outro município, exercício ou anexo.
    """
    esperado_anexo = nome_do_anexo(anexo, exercicio)
    linhas = []
    for item in payload.get("items", []):
        if (_inteiro(item.get("cod_ibge")) != codigo or _inteiro(item.get("exercicio")) != exercicio
                or str(item.get("anexo") or "") != esperado_anexo):
            raise ContratoSiconfiError(
                f"{municipio} {exercicio} {anexo}: resposta divergente "
                f"(ente {item.get('cod_ibge')}, exercício {item.get('exercicio')}, anexo {item.get('anexo')!r})"
            )
        linhas.append({
            "municipio": municipio,
            "cod_ibge": codigo,
            "exercicio": exercicio,
            "anexo": anexo,
            "coluna": item.get("coluna"),
            "cod_conta": item.get("cod_conta"),
            "conta": item.get("conta"),
            "valor": item.get("valor"),
        })
    return linhas


def coletar(anexos, anos, consultar=None, pausa: float = 0.3):
    """Coleta todas as combinações. Devolve (linhas, resumo).

    `resumo` traz, por município, anexo e exercício: quantidade de linhas, se a API indicou
    mais páginas (`hasMore`) e o erro, quando houve. Página adicional não é buscada aqui: o
    resumo deixa isso visível para revisão.
    """
    consultar = consultar or consultar_anexo
    linhas, resumo = [], []
    for anexo in anexos:
        for ano in anos:
            for nome, codigo in MUNICIPIOS.items():
                try:
                    payload = consultar(anexo, ano, codigo)
                    novas = linhas_do_anexo(payload, nome, codigo, anexo, ano)
                except (OSError, ValueError, ContratoSiconfiError) as erro:
                    resumo.append((nome, anexo, ano, 0, None, str(erro)[:120]))
                    continue
                linhas.extend(novas)
                resumo.append((nome, anexo, ano, len(novas), payload.get("hasMore"), ""))
                time.sleep(pausa)
    return linhas, resumo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--anexos", nargs="+", default=list(ANEXOS_PADRAO), help="ex.: I-C I-D")
    ap.add_argument("--inicio", type=int, default=2013)
    ap.add_argument("--fim", type=int, default=2025)
    ap.add_argument("--saida", default="output/financas/dca_anexos.csv")
    args = ap.parse_args(argv)

    anos = range(args.inicio, args.fim + 1)
    linhas, resumo = coletar(args.anexos, anos)

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO)
        w.writeheader()
        w.writerows(linhas)

    print(f"{len(linhas)} linhas gravadas em {saida}")
    for nome, anexo, ano, qtd, mais, erro in resumo:
        marca = f"ERRO: {erro}" if erro else ("SEM DADOS" if qtd == 0 else "")
        print(f"{nome:28} {anexo:4} {ano}  linhas={qtd}  hasMore={mais}  {marca}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
