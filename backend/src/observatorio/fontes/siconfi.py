"""Fonte SICONFI: despesa por função da DCA e as referências do mesmo município (RN-FNT-04).

Baixa da API pública do Tesouro (sem chave) a DCA Anexo I-E, o RREO Anexo 2 do 6º bimestre, a MSC de
dezembro e o extrato de entregas dos 12 municípios (RN-TER-01), do exercício de 2013 até o ano corrente,
sem fixar o último ano (RN-TMP-01). Cada resposta é guardada comprimida, com o SHA-256 do corpo HTTP, num
índice de proveniência (RN-FON-13, RN-FON-14, RN-TMP-18, exceção de 25/11/2026). Chave esperada ausente,
exercício ou ente diferentes do pedido e conta desconhecida falham de forma explícita (RN-VPU-04).

Dinheiro em `Decimal` (RN-CFE-11); município sem linha fica ausente, nunca zero (RN-MOD-10). Não confere,
não aprova nem publica: isso é da validação.
"""

import gzip
import hashlib
import json
import re
import time
import unicodedata
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from observatorio.modelo.lote import Entrega, LinhaReferencia, LoteDespesa
from observatorio.modelo.observacao import Observacao
from observatorio.modelo.territorios import MUNICIPIOS

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
PRIMEIRO_ANO = 2013  # RN-FNT-04 e RN-TMP-15: a série começa em 2013
LIMITE = 5000
VERSAO_TRATAMENTO = "1.0.0"
FONTE = "SICONFI, DCA Anexo I-E"

ESTAGIOS_DCA = {
    "Despesas Empenhadas": "empenhada",
    "Despesas Liquidadas": "liquidada",
    "Despesas Pagas": "paga",
}
ESTAGIOS_RREO = {
    "DESPESAS EMPENHADAS ATÉ O BIMESTRE": "empenhada",
    "DESPESAS LIQUIDADAS ATÉ O BIMESTRE": "liquidada",
}
INDICADORES = {estagio: f"despesa_funcao_{estagio}" for estagio in ESTAGIOS_DCA.values()}
CONTA_PAGA_MSC = "622130400"  # crédito empenhado liquidado pago (RN-CFE-24, mapeamento de 19/11/2026)
MODALIDADE_INTRA = "91"

# Entregas que mudam o lote: DCA, RREO do 6º bimestre e MSC de dezembro (RN-TMP-04).
ENTREGAVEIS = {
    "Balanço Anual (DCA)": None,
    "Relatório Resumido de Execução Orçamentária": 6,
    "MSC Agregada": 12,
}

# Colunas esperadas de cada resposta (RN-VPU-04). A API devolve mais campos; estes são os que o lote usa.
CHAVES = {
    "dca": ("exercicio", "cod_ibge", "anexo", "coluna", "conta", "valor"),
    "rreo": ("exercicio", "cod_ibge", "anexo", "rotulo", "coluna", "conta", "valor", "periodo"),
    "msc_orcamentaria": (
        "exercicio",
        "cod_ibge",
        "mes_referencia",
        "conta_contabil",
        "funcao",
        "subfuncao",
        "natureza_despesa",
        "natureza_conta",
        "valor",
    ),
    "extrato_entregas": (
        "exercicio",
        "cod_ibge",
        "entregavel",
        "periodo",
        "instituicao",
        "status_relatorio",
        "data_status",
    ),
}

FUNCAO = re.compile(r"^(\d{2}) - (.+)$")
SUBFUNCAO = re.compile(r"^(\d{2})\.(\d{3}) - (.+)$")
DEMAIS = re.compile(r"^FU(\d{2}) - (Demais Subfun.+)$")

Buscar = Callable[[str], bytes]


def buscar_http(url: str) -> bytes:
    """GET com User-Agent; três tentativas em erro de rede ou 5xx. Outro HTTP falha na hora."""
    for tentativa in range(3):
        requisicao = Request(url, headers={"User-Agent": "Mozilla/5.0 ObservatorioCFEM/1.0"})
        try:
            with urlopen(requisicao, timeout=240) as resposta:
                corpo: bytes = resposta.read()
                return corpo
        except HTTPError as erro:
            if erro.code < 500 or tentativa == 2:
                raise ValueError(f"SICONFI respondeu HTTP {erro.code} em {url}") from erro
        except (URLError, TimeoutError) as erro:
            if tentativa == 2:
                raise ValueError(f"SICONFI inacessível em {url}: {erro}") from erro
        time.sleep(5 * (tentativa + 1))
    raise AssertionError("inalcançável")


class Arquivo:
    """Guarda cada resposta comprimida e monta o índice de proveniência (RN-FON-13, RN-TMP-18)."""

    def __init__(self, pasta: Path, buscar: Buscar) -> None:
        self.pasta = pasta
        self.buscar = buscar
        self.indice: list[dict[str, object]] = []
        pasta.mkdir(parents=True, exist_ok=True)

    def consultar(self, rota: str, parametros: dict[str, object]) -> list[dict[str, Any]]:
        """Lê todas as páginas (`hasMore`) e confere o contrato de cada uma."""
        itens: list[dict[str, Any]] = []
        deslocamento = 0
        while True:
            consulta = {**parametros, "offset": deslocamento, "limit": LIMITE}
            url = f"{API}/{rota}?{urlencode(consulta)}"
            corpo = self.buscar(url)
            resumo = hashlib.sha256(corpo).hexdigest()
            nome = f"{rota}-{len(self.indice):05d}.json.gz"
            (self.pasta / nome).write_bytes(gzip.compress(corpo, mtime=0))
            self.indice.append({"arquivo": nome, "url": url, "sha256": resumo, "bytes": len(corpo)})
            try:
                pagina = json.loads(corpo)
            except ValueError as erro:
                raise ValueError(f"SICONFI devolveu JSON inválido em {url}") from erro
            if (
                not isinstance(pagina, dict)
                or not isinstance(pagina.get("items"), list)
                or not isinstance(pagina.get("hasMore"), bool)
            ):
                raise ValueError(f"Paginação do SICONFI alterada em {rota} (RN-VPU-04)")  # noqa: TRY004
            for item in pagina["items"]:
                _conferir_item(rota, item, parametros)
            itens.extend(pagina["items"])
            if not pagina["hasMore"]:
                return itens
            if not pagina["items"] or deslocamento > 200_000:
                raise ValueError(f"Paginação do SICONFI inconsistente em {rota}")
            deslocamento += len(pagina["items"])


def _conferir_item(rota: str, item: object, parametros: dict[str, object]) -> None:
    """RN-VPU-04: chaves esperadas presentes e o mesmo ente e exercício do pedido."""
    if not isinstance(item, dict):
        raise ValueError(f"Linha do SICONFI não é objeto em {rota}")  # noqa: TRY004
    faltantes = [c for c in CHAVES[rota] if c not in item]
    if faltantes:
        raise ValueError(f"Layout do SICONFI alterado em {rota}: faltam {', '.join(faltantes)} (RN-VPU-04)")
    ano = parametros.get("an_exercicio", parametros.get("an_referencia"))
    if str(item["cod_ibge"]) != str(parametros["id_ente"]) or str(item["exercicio"]) != str(ano):
        raise ValueError(f"SICONFI devolveu ente ou exercício diferente do pedido em {rota}")


def _decimal(valor: object, onde: str) -> Decimal:
    """Valor da API em `Decimal`, sem passar por float (RN-CFE-11)."""
    if isinstance(valor, bool) or not isinstance(valor, int | float | str):
        raise ValueError(f"Valor não numérico em {onde} (RN-VPU-04)")  # noqa: TRY004
    try:
        numero = Decimal(str(valor))
    except InvalidOperation as erro:
        raise ValueError(f"Valor não numérico em {onde} (RN-VPU-04)") from erro
    if not numero.is_finite():
        raise ValueError(f"Valor não finito em {onde}")
    return numero.quantize(Decimal("0.01"))


def normalizar(texto: str) -> str:
    """Compara contas de publicações diferentes: sem acento, caixa, espaço nem pontuação."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento.lower() if c.isalnum())


def classificar_conta(conta: str) -> tuple[str, str] | None:
    """Conta da DCA → (categoria, nome). `None` para a linha intraorçamentária, que fica fora.

    RN-FNT-04: o total "Despesas (Exceto Intraorçamentárias)" vira `total` (2013 grafa "Intra-Orçamentárias");
    funções `FF`, subfunções `FF.SSS` e "FUxx - Demais Subfunções" `FF.demais`. Conta desconhecida é layout
    novo e falha (RN-VPU-04).
    """
    chave = normalizar(conta)
    if chave == "despesasexcetointraorcamentarias":
        return "total", conta
    if chave == "despesasintraorcamentarias":
        return None
    if m := SUBFUNCAO.match(conta):
        return f"{m[1]}.{m[2]}", m[3]
    if m := FUNCAO.match(conta):
        return m[1], m[2]
    if m := DEMAIS.match(conta):
        return f"{m[1]}.demais", m[2]
    raise ValueError(f"Conta desconhecida na DCA: {conta!r} (RN-VPU-04)")


def _anexo_dca(ano: int) -> str:
    """De 2014 em diante `DCA-Anexo I-E`; em 2013, `Anexo I-E` (RN-FNT-04)."""
    return "Anexo I-E" if ano == 2013 else "DCA-Anexo I-E"


def consultar_entregas(
    arquivo: Arquivo, anos: Iterable[int], municipios: Iterable[str] = MUNICIPIOS
) -> tuple[Entrega, ...]:
    """Extrato das entregas que alimentam o lote, por município e exercício (RN-TMP-04)."""
    entregas: list[Entrega] = []
    for ano in anos:
        for codigo in municipios:
            for item in arquivo.consultar("extrato_entregas", {"id_ente": codigo, "an_referencia": ano}):
                nome = str(item["entregavel"])
                if nome not in ENTREGAVEIS:
                    continue
                periodo = int(item["periodo"]) if item["periodo"] is not None else None
                if ENTREGAVEIS[nome] is not None and periodo != ENTREGAVEIS[nome]:
                    continue
                entregas.append(
                    Entrega(
                        municipio_id=codigo,
                        ano=ano,
                        entregavel=nome,
                        periodo=periodo,
                        instituicao=str(item["instituicao"]),
                        status=item["status_relatorio"],
                        data_status=str(item["data_status"]),
                    )
                )
    return tuple(sorted(entregas, key=lambda e: (e.municipio_id, e.ano, e.entregavel, e.instituicao)))


def anos_da_serie(agora: datetime | None = None) -> tuple[int, ...]:
    """De 2013 ao ano corrente; os anos ainda sem entrega simplesmente não têm linha (RN-TMP-01)."""
    return tuple(range(PRIMEIRO_ANO, (agora or datetime.now(UTC)).year + 1))


def coletar(
    pasta: Path,
    buscar: Buscar = buscar_http,
    anos: Iterable[int] | None = None,
    municipios: Iterable[str] = MUNICIPIOS,
    entregas: tuple[Entrega, ...] | None = None,
) -> LoteDespesa:
    """Baixa DCA, RREO, MSC e entregas, guarda o bruto e converte a DCA em observações não conferidas."""
    coletado_em = datetime.now(UTC).isoformat()
    lista_anos = tuple(anos) if anos is not None else anos_da_serie()
    lista_municipios = tuple(municipios)
    arquivo = Arquivo(pasta, buscar)
    if entregas is None:
        entregas = consultar_entregas(arquivo, lista_anos, lista_municipios)
    dca_por_chave: dict[tuple[str, int], list[dict[str, Any]]] = {}
    rreo: list[LinhaReferencia] = []
    msc: dict[tuple[str, int], dict[str, Decimal]] = {}
    linhas_lidas = 0
    for ano in lista_anos:
        for codigo in lista_municipios:
            dca = arquivo.consultar(
                "dca", {"an_exercicio": ano, "id_ente": codigo, "no_anexo": _anexo_dca(ano)}
            )
            linhas_lidas += len(dca)
            if dca:
                dca_por_chave[(codigo, ano)] = dca
            parametros_rreo = {
                "an_exercicio": ano,
                "nr_periodo": 6,
                "co_tipo_demonstrativo": "RREO",
                "no_anexo": "RREO-Anexo 02",
                "id_ente": codigo,
            }
            for item in arquivo.consultar("rreo", parametros_rreo):
                linhas_lidas += 1
                estagio = _estagio_rreo(str(item["coluna"]))
                if estagio is None or not normalizar(str(item["rotulo"])).startswith(
                    "totaldasdespesasexcetointra"
                ):
                    continue
                rreo.append(
                    LinhaReferencia(codigo, ano, estagio, str(item["conta"]), _decimal(item["valor"], "RREO"))
                )
            parametros_msc = {
                "id_ente": codigo,
                "an_referencia": ano,
                "me_referencia": 12,
                "co_tipo_matriz": "MSCC",
                "classe_conta": 6,
                "id_tv": "ending_balance",
            }
            itens_msc = arquivo.consultar("msc_orcamentaria", parametros_msc)
            linhas_lidas += len(itens_msc)
            pagas = somar_msc(itens_msc)
            if pagas:
                msc[(codigo, ano)] = pagas
    observacoes, intra = converter_dca(dca_por_chave, entregas, coletado_em)
    indice = {
        "fonte": "SICONFI (API pública do Tesouro Nacional)",
        "api": API,
        "coletado_em": coletado_em,
        "respostas": arquivo.indice,
    }
    conteudo_indice = json.dumps(indice, ensure_ascii=False, indent=1).encode()
    (pasta / "indice.json").write_bytes(conteudo_indice)
    # Edição do lote: o conjunto de corpos HTTP lidos, sem a data da coleta (o mesmo dado dá o mesmo SHA).
    sha = hashlib.sha256(json.dumps([(r["url"], r["sha256"]) for r in arquivo.indice]).encode()).hexdigest()
    return LoteDespesa(
        observacoes=observacoes,
        rreo=tuple(rreo),
        msc=msc,
        entregas=entregas,
        anos=lista_anos,
        bruto=pasta,
        sha256=sha,
        coletado_em=coletado_em,
        origem=API,
        respostas=len(arquivo.indice),
        linhas_lidas=linhas_lidas,
        intraorcamentarias=intra,
        filtros={
            "municipios": list(lista_municipios),
            "anos": [min(lista_anos), max(lista_anos)] if lista_anos else [],
            "dca": "Anexo I-E, colunas Despesas Empenhadas, Liquidadas e Pagas",
            "rreo": "RREO-Anexo 02, 6º bimestre, seção exceto intraorçamentárias, empenhadas e liquidadas até o bimestre",
            "msc": f"MSCC de dezembro, saldo final, classe 6, conta {CONTA_PAGA_MSC} sem a modalidade 91",
        },
    )


def _estagio_rreo(coluna: str) -> str | None:
    texto = normalizar(coluna)
    for prefixo, estagio in ESTAGIOS_RREO.items():
        if texto.startswith(normalizar(prefixo)):
            return estagio
    return None


def somar_msc(itens: list[dict[str, Any]]) -> dict[str, Decimal]:
    """Despesa paga da MSC por função (`FF`) e subfunção (`FF.SSS`), sem intraorçamentária.

    Natureza C soma e D subtrai; a modalidade (3º e 4º dígitos da natureza da despesa) 91 fica fora,
    como na DCA "exceto intraorçamentárias".
    """
    saida: dict[str, Decimal] = defaultdict(Decimal)
    for item in itens:
        if item["conta_contabil"] != CONTA_PAGA_MSC or str(item["mes_referencia"]) != "12":
            continue
        if str(item["natureza_despesa"] or "")[2:4] == MODALIDADE_INTRA:
            continue
        if item["natureza_conta"] not in ("C", "D") or not item["funcao"] or not item["subfuncao"]:
            raise ValueError("Linha da MSC sem natureza, função ou subfunção (RN-VPU-04)")
        valor = _decimal(item["valor"], "MSC")
        sinal = 1 if item["natureza_conta"] == "C" else -1
        saida[str(item["funcao"])] += sinal * valor
        saida[f"{item['funcao']}.{item['subfuncao']}"] += sinal * valor
    return dict(saida)


def converter_dca(
    dca: dict[tuple[str, int], list[dict[str, Any]]], entregas: Iterable[Entrega], coletado_em: str
) -> tuple[tuple[Observacao, ...], int]:
    """Linhas da DCA → observações por estágio e categoria; a edição é o status e a data da entrega."""
    edicoes = {
        (e.municipio_id, e.ano): f"DCA {e.status or 'sem status'} {e.data_status}"
        for e in entregas
        if e.entregavel == "Balanço Anual (DCA)"
    }
    observacoes: list[Observacao] = []
    intra = 0
    for (codigo, ano), itens in sorted(dca.items(), key=lambda par: par[0]):
        for item in itens:
            estagio = ESTAGIOS_DCA.get(str(item["coluna"]))
            if estagio is None:
                continue  # inscrição de restos a pagar: fora do indicador
            classe = classificar_conta(str(item["conta"]))
            if classe is None:
                intra += 1
                continue
            categoria, nome = classe
            valor = _decimal(item["valor"], f"DCA {codigo}/{ano}")
            observacoes.append(
                Observacao(
                    indicador=INDICADORES[estagio],
                    municipio_id=codigo,
                    municipio_nome=MUNICIPIOS[codigo],
                    nivel_territorial="município",
                    ano=ano,
                    mes=None,
                    valor=valor,
                    unidade="BRL nominal",
                    natureza_valor="zero real" if valor == 0 else "informado",
                    estado_validacao="provisório",
                    fonte=FONTE,
                    edicao_fonte=edicoes.get((codigo, ano)),
                    atualizado_em=coletado_em,
                    versao_tratamento=VERSAO_TRATAMENTO,
                    categoria=categoria,
                    categoria_nome=nome,
                )
            )
    return tuple(observacoes), intra
