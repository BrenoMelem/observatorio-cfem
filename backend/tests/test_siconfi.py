"""Fonte, conferência e publicação da despesa por função do SICONFI (RN-FNT-04, RN-VPU-04/07/12, RN-TMP-04).

Usa um recorte real da API (Piçarra, 2024; ver `fixtures/siconfi/README.md`). As outras combinações de
município e exercício respondem sem linhas, como a API faz com um exercício ainda não entregue.
"""

import gzip
import hashlib
import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from observatorio.fontes import siconfi
from observatorio.modelo.lote import LoteDespesa
from observatorio.validacao import siconfi as validacao

FIXTURES = Path(__file__).parent / "fixtures" / "siconfi"
ENTE, ANO = "1505635", 2024
ARQUIVOS = {
    "dca": "dca.json",
    "rreo": "rreo.json",
    "msc_orcamentaria": "msc.json",
    "extrato_entregas": "extrato.json",
}

# RN-VPU-04: as colunas que a fonte exige de cada resposta.
COLUNAS_ESPERADAS = {
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

Alterar = Callable[[str, list[dict[str, Any]]], list[dict[str, Any]]]


def buscador(alterar: Alterar | None = None) -> siconfi.Buscar:
    """Responde com o recorte real para Piçarra 2024 e com página vazia para o resto."""

    def buscar(url: str) -> bytes:
        partes = urlparse(url)
        rota = partes.path.rsplit("/", 1)[1]
        consulta = {k: v[0] for k, v in parse_qs(partes.query).items()}
        ano = int(consulta.get("an_exercicio") or consulta["an_referencia"])
        itens: list[dict[str, Any]] = []
        if consulta["id_ente"] == ENTE and ano == ANO:
            itens = json.loads((FIXTURES / ARQUIVOS[rota]).read_text(encoding="utf-8"))["items"]
            if alterar:
                itens = alterar(rota, itens)
        return json.dumps({"items": itens, "hasMore": False, "limit": 5000, "offset": 0}).encode()

    return buscar


def coletar(tmp_path: Path, alterar: Alterar | None = None) -> LoteDespesa:
    return siconfi.coletar(
        tmp_path / "bruto", buscador(alterar), anos=[2023, ANO], municipios=[ENTE, "1501576"]
    )


def test_colunas_esperadas_e_amostra_real() -> None:
    """RN-VPU-04: a lista de colunas exigidas é a documentada, e o recorte real a cumpre."""
    assert siconfi.CHAVES == COLUNAS_ESPERADAS
    for rota, arquivo in ARQUIVOS.items():
        for item in json.loads((FIXTURES / arquivo).read_text(encoding="utf-8"))["items"]:
            assert set(COLUNAS_ESPERADAS[rota]) <= set(item)


def test_fonte_converte_dca_com_decimal_categoria_e_proveniencia(tmp_path: Path) -> None:
    """RN-FNT-04, RN-CFE-11, RN-FON-13/14, RN-TMP-04: categorias, Decimal, edição da entrega e bruto."""
    lote = coletar(tmp_path)
    assert {o.municipio_id for o in lote.observacoes} == {ENTE}  # Bom Jesus sem DCA: ausente, não zero
    paga = {o.categoria: o for o in lote.observacoes if o.indicador == "despesa_funcao_paga"}
    assert paga["total"].categoria_nome == "Despesas Exceto Intraorçamentárias"
    assert paga["12"].categoria_nome == "Educação"
    categorias = [c for c in paga if c is not None]
    assert any(c.endswith(".demais") for c in categorias) and any(len(c) == 6 for c in categorias)
    assert all(isinstance(o.valor, Decimal) for o in lote.observacoes)
    assert paga["total"].edicao_fonte is not None and paga["total"].edicao_fonte.startswith("DCA HO ")
    bruto_dca = json.loads((FIXTURES / "dca.json").read_text(encoding="utf-8"))["items"]
    assert lote.intraorcamentarias == sum(i["conta"] == "Despesas Intraorçamentárias" for i in bruto_dca)
    indice = json.loads((tmp_path / "bruto" / "indice.json").read_text(encoding="utf-8"))
    primeira = indice["respostas"][0]
    corpo = gzip.decompress((tmp_path / "bruto" / primeira["arquivo"]).read_bytes())
    assert hashlib.sha256(corpo).hexdigest() == primeira["sha256"]  # SHA-256 do conteúdo, não do .gz
    assert len(lote.sha256) == 64 and lote.sha256 == coletar(tmp_path / "de-novo").sha256


def test_conta_2013_e_conta_desconhecida() -> None:
    """RN-FNT-04: o total de 2013 tem hífen; conta nova é layout novo (RN-VPU-04)."""
    assert siconfi.classificar_conta("Despesas (Exceto Intra-Orçamentárias)") == (
        "total",
        "Despesas (Exceto Intra-Orçamentárias)",
    )
    assert siconfi.classificar_conta("Despesas Intraorçamentárias") is None
    assert siconfi.classificar_conta("FU12 - Demais Subfunções") == ("12.demais", "Demais Subfunções")
    with pytest.raises(ValueError, match="Conta desconhecida"):
        siconfi.classificar_conta("Reserva de Contingência")


def test_layout_alterado_falha(tmp_path: Path) -> None:
    """RN-VPU-04: coluna esperada ausente falha de forma explícita."""

    def sem_conta(rota: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{k: v for k, v in i.items() if k != "conta"} for i in itens] if rota == "dca" else itens

    with pytest.raises(ValueError, match="faltam conta"):
        coletar(tmp_path, sem_conta)


def test_conferencia_real_coincide_nos_tres_estagios(tmp_path: Path) -> None:
    """RN-FNT-04, RN-VPU-07/12: Piçarra 2024 coincide com o RREO e com a MSC, ao centavo."""
    resultado = validacao.validar(coletar(tmp_path))
    assert resultado.aprovado, resultado.erros
    assert resultado.relatorio["conferidos"] == [
        f"{ENTE}:{ANO}:{e}" for e in ("empenhada", "liquidada", "paga")
    ]
    assert all(o.estado_validacao == "validado" for o in resultado.observacoes)
    assert f"1501576:{ANO}" in resultado.relatorio["ausencias_municipais"]  # type: ignore[operator]


def test_divergencia_de_um_centavo_tira_so_o_estagio(tmp_path: Path) -> None:
    """RN-VPU-12: R$ 0,01 de diferença no RREO tira a empenhada; liquidada e paga continuam."""

    def um_centavo(rota: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if rota != "rreo":
            return itens
        alvo = next(
            i for i in itens if i["coluna"].startswith("DESPESAS EMPENHADAS") and i["conta"] == "Educação"
        )
        return [{**i, "valor": i["valor"] + 0.01} if i is alvo else i for i in itens]

    resultado = validacao.validar(coletar(tmp_path, um_centavo))
    assert resultado.aprovado
    assert {o.indicador for o in resultado.observacoes} == {"despesa_funcao_liquidada", "despesa_funcao_paga"}
    fora = resultado.relatorio["fora_da_publicacao"]
    assert isinstance(fora, list) and fora[0]["chave"] == f"{ENTE}:{ANO}:empenhada"
    assert "12:" in fora[0]["diferencas"][0]


def test_sem_msc_a_paga_fica_fora(tmp_path: Path) -> None:
    """RN-VPU-07: sem referência, nada é homologado; o motivo vai para o relatório."""

    def sem_msc(rota: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [] if rota == "msc_orcamentaria" else itens

    resultado = validacao.validar(coletar(tmp_path, sem_msc))
    assert "despesa_funcao_paga" not in {o.indicador for o in resultado.observacoes}
    assert resultado.relatorio["conferencia"]["paga"]["sem_referencia"] == 1  # type: ignore[index]


def test_fechamento_quebrado_reprova_o_lote(tmp_path: Path) -> None:
    """RN-FNT-04: se a soma das funções não bate com o total, o lote bloqueia."""

    def total_errado(rota: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if rota != "dca":
            return itens
        return [
            {**i, "valor": i["valor"] + 1}
            if i["conta"].startswith("Despesas Exceto") and i["coluna"] == "Despesas Pagas"
            else i
            for i in itens
        ]

    resultado = validacao.validar(coletar(tmp_path, total_errado))
    assert not resultado.aprovado and not resultado.observacoes
    assert any("Fechamento da DCA" in e for e in resultado.erros)


def test_publicacao_conserva_cfem_e_api_filtra_categoria(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-VPU-02/03, RN-ENT-01, RN-MOD-03: o pacote ganha a despesa sem perder a CFEM; filtro por categoria."""
    from test_publicacao_cfem import lote_aprovado

    from observatorio.api.main import app
    from observatorio.publicacao.pacote import publicar

    pasta = tmp_path / "publicado"
    publicar(lote_aprovado(tmp_path), pasta, manifesto)
    resultado = validacao.validar(coletar(tmp_path))
    versao = publicar(resultado, pasta, manifesto, qualidade="qualidade-siconfi.json")
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(pasta))
    cliente = TestClient(app)
    corpo = cliente.get("/api/v1/dimensoes/economica", params={"categoria": "12"}).json()
    assert corpo["versao_dados"] == versao
    indicadores = {d["indicador"] for d in corpo["dados"]}
    assert indicadores == {"despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga"}
    assert all(d["categoria_nome"] == "Educação" and isinstance(d["valor"], str) for d in corpo["dados"])
    todos = cliente.get("/api/v1/dimensoes/economica").json()["dados"]
    assert any(d["indicador"] == "cfem_arrecadada" and d["categoria"] is None for d in todos)
    csv = cliente.get("/api/v1/dimensoes/economica.csv", params={"categoria": "total"}).text
    assert ";categoria;categoria_nome;" in csv.splitlines()[0]
    # RN-VPU-02: uma coleta que perde um estágio já publicado não troca o pacote...
    menor = validacao.validar(coletar(tmp_path / "b", lambda r, i: [] if r == "msc_orcamentaria" else i))
    da_fonte = frozenset(siconfi.INDICADORES.values())
    with pytest.raises(ValueError, match="encolheu"):
        publicar(menor, pasta, manifesto, qualidade="qualidade-siconfi.json", indicadores_da_fonte=da_fonte)
    # ...salvo quando a entrega daquele município e ano mudou (RN-TMP-04): a paga sai do pacote.
    publicar(
        menor,
        pasta,
        manifesto,
        qualidade="qualidade-siconfi.json",
        retificados=frozenset({(ENTE, ANO)}),
        indicadores_da_fonte=da_fonte,
    )
    depois = {d["indicador"] for d in cliente.get("/api/v1/dimensoes/economica").json()["dados"]}
    assert "despesa_funcao_paga" not in depois and "cfem_arrecadada" in depois


def test_entregas_alteradas_detecta_retificacao(tmp_path: Path) -> None:
    """RN-TMP-04: a data nova de uma entrega marca o município e o exercício."""
    lote = coletar(tmp_path)
    anterior: dict[str, object] = {"entregas": validacao.resumo_entregas(lote.entregas)}
    assert validacao.entregas_alteradas(lote.entregas, anterior) == []

    def retificada(rota: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if rota != "extrato_entregas":
            return itens
        return [{**i, "status_relatorio": "RE", "data_status": "2026-11-01T00:00:00Z"} for i in itens]

    novo = coletar(tmp_path / "novo", retificada)
    assert validacao.entregas_alteradas(novo.entregas, anterior) == [f"{ENTE}:{ANO}"]


def test_coleta_siconfi_somente_se_mudou(
    tmp_path: Path, manifesto: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-TMP-02 (exceção de 25/11/2026) e RN-VPU-06: publica uma vez; sem entrega nova, não coleta de novo."""
    from observatorio import coleta

    monkeypatch.setenv("OBS_DATA_DIR", str(tmp_path / "dados"))
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path / "dados" / "publicado"))
    monkeypatch.setenv("OBS_MANIFESTO", str(manifesto))
    monkeypatch.setattr(siconfi, "anos_da_serie", lambda agora=None: (2023, ANO))
    primeira = coleta.executar_siconfi(True, buscador())
    assert primeira["situacao"] == "aprovado", primeira
    segunda = coleta.executar_siconfi(True, buscador())
    assert segunda["situacao"] == "sem_mudanca"
    relatorio = json.loads(Path(str(primeira["relatorio"])).read_text(encoding="utf-8"))
    bruto = Path(str(primeira["bruto"]))
    assert (bruto / "indice.json").is_file() and (bruto / "entregas" / "indice.json").is_file()
    assert relatorio["conferencia"]["paga"]["conferidos"] == 1
