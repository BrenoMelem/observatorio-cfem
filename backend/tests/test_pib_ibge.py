"""PIB municipal do SIDRA 5938: leitura, conferência interna e coleta (RN-FNT-02, RN-FNT-19, RN-VPU-04/07/12)."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import polars as pl
import pytest

from observatorio import coleta
from observatorio.fontes import pib_ibge
from observatorio.modelo.lote import LotePib
from observatorio.validacao import pib_ibge as validacao

FIXTURES = Path(__file__).parent / "fixtures" / "pib_ibge"
DADOS = (FIXTURES / "sidra-5938-recorte.json").read_bytes()
PERIODOS = (FIXTURES / "periodos-recorte.json").read_bytes()
ANOS = [2012, 2022, 2023]
VARIAVEIS_ESPERADAS = ["37", "543", "498", "513", "517", "6575", "525"]
INDICADORES_ESPERADOS = [
    "pib_municipal",
    "pib_impostos_liquidos",
    "vab_total",
    "vab_agropecuaria",
    "vab_industria",
    "vab_servicos",
    "vab_administracao_publica",
]
PARAUAPEBAS = "1505536"


def buscar_falso(url: str) -> bytes:
    return PERIODOS if url == pib_ibge.URL_PERIODOS else DADOS


def alterar(funcao: Any) -> bytes:
    dados = json.loads(DADOS)
    funcao(dados)
    return json.dumps(dados).encode()


def lote(tmp_path: Path) -> LotePib:
    return pib_ibge.coletar(tmp_path / "bruto", buscar_falso)


def test_variaveis_e_unidade_esperadas() -> None:
    """RN-VPU-04: as sete variáveis, os indicadores do manifesto e a unidade em mil reais."""
    assert list(pib_ibge.VARIAVEIS) == VARIAVEIS_ESPERADAS
    assert list(pib_ibge.INDICADORES) == INDICADORES_ESPERADOS
    assert pib_ibge.UNIDADE_SIDRA == "Mil Reais" and pib_ibge.UNIDADE == "BRL mil nominal"
    nomes = {v["id"]: v["variavel"] for v in json.loads(DADOS)}
    assert nomes == {id_: nome for id_, (_, nome) in pib_ibge.VARIAVEIS.items()}


def test_periodos_desde_2010() -> None:
    """RN-TMP-16: só os anos a partir de 2010, com a data de modificação de cada um."""
    assert pib_ibge.ler_periodos(PERIODOS) == {2012: "14/12/2016", 2022: "19/12/2025", 2023: "19/12/2025"}


def test_observacoes_lacunas_e_negativos(tmp_path: Path) -> None:
    """RN-MOD-10/12: `...` é lacuna, nunca zero; VAB negativo publicado como o IBGE publica (27/11/2026)."""
    observacoes = lote(tmp_path).observacoes
    assert len(observacoes) == 12 * len(ANOS) * 7
    assert {o.unidade for o in observacoes} == {"BRL mil nominal"}
    assert all(o.mes is None and o.nivel_territorial == "município" for o in observacoes)
    pib_2023 = next(
        o
        for o in observacoes
        if o.indicador == "pib_municipal" and o.ano == 2023 and o.municipio_id == "1501576"
    )
    assert (pib_2023.valor, pib_2023.natureza_valor) == (Decimal(336974), "informado")
    componentes_recentes = [o for o in observacoes if o.ano >= 2022 and o.indicador != "pib_municipal"]
    assert len(componentes_recentes) == 12 * 2 * 6
    assert all(o.valor is None and o.natureza_valor == "ausente" for o in componentes_recentes)
    negativos = sorted((o.municipio_id, o.valor) for o in observacoes if o.valor is not None and o.valor < 0)
    assert negativos == [
        ("1501576", Decimal(-2890)),
        ("1501758", Decimal(-1252)),
        ("1507151", Decimal(-1750)),
        ("1507508", Decimal(-456)),
    ]


def test_proveniencia_do_bruto(tmp_path: Path) -> None:
    """RN-FON-13/14: as duas respostas guardadas, com URL, SHA-256 e filtros."""
    lido = lote(tmp_path)
    indice = json.loads((lido.bruto / "indice.json").read_text(encoding="utf-8"))
    assert set(indice["arquivos"]) == {"periodos.json", "sidra-5938.json"}
    assert indice["arquivos"]["sidra-5938.json"]["sha256"] == lido.sha256
    assert indice["filtros"]["anos"] == ANOS
    assert (lido.bruto / "sidra-5938.json").read_bytes() == DADOS


def test_unidade_alterada_falha() -> None:
    """RN-VPU-04: unidade diferente de mil reais falha de forma explícita."""
    corpo = alterar(lambda d: d[0].update(unidade="Reais"))
    with pytest.raises(ValueError, match="unidade inesperada"):
        pib_ibge.converter(corpo, ANOS, "agora", "x")


def test_variavel_ausente_falha() -> None:
    """RN-VPU-04: resposta sem uma das sete variáveis."""
    with pytest.raises(ValueError, match="diferentes das esperadas"):
        pib_ibge.converter(alterar(lambda d: d.pop()), ANOS, "agora", "x")


def test_municipio_faltando_ou_trocado_falha() -> None:
    """RN-FNT-19: falta de município ou nome que não confere bloqueia o lote."""
    with pytest.raises(ValueError, match="sem os municípios"):
        pib_ibge.converter(alterar(lambda d: d[0]["resultados"][0]["series"].pop()), ANOS, "agora", "x")

    def trocar_nome(d: list[dict[str, Any]]) -> None:
        d[0]["resultados"][0]["series"][0]["localidade"]["nome"] = "Marabá (PA)"

    with pytest.raises(ValueError, match="RN-TER-07"):
        pib_ibge.converter(alterar(trocar_nome), ANOS, "agora", "x")


def test_nome_sem_acento_confere() -> None:
    """RN-TER-07: o nome é conferido sem acento e sem diferença de caixa."""

    def sem_acento(d: list[dict[str, Any]]) -> None:
        for variavel in d:
            for serie in variavel["resultados"][0]["series"]:
                serie["localidade"]["nome"] = serie["localidade"]["nome"].upper().replace("Ã", "A")

    assert len(pib_ibge.converter(alterar(sem_acento), ANOS, "agora", "x")) == 12 * len(ANOS) * 7


def test_valor_nao_numerico_falha() -> None:
    """RN-VPU-04: texto que não é número nem sinal do SIDRA."""
    corpo = alterar(lambda d: d[0]["resultados"][0]["series"][0]["serie"].update({"2012": "1.234,5"}))
    with pytest.raises(ValueError, match="valor inesperado"):
        pib_ibge.converter(corpo, ANOS, "agora", "x")


def test_validacao_identidades_e_lacunas(tmp_path: Path) -> None:
    """Exceção de RN-VPU-07/12: identidades dentro do arredondamento; anos sem componentes publicados como lacuna."""
    resultado = validacao.validar(lote(tmp_path))
    assert resultado.aprovado
    assert len(resultado.observacoes) == 12 * len(ANOS) * 7
    assert {o.estado_validacao for o in resultado.observacoes} == {"validado"}
    relatorio = resultado.relatorio
    assert relatorio["referencia_externa"] is None
    assert relatorio["conferencia"] == {
        "municipio_ano_com_identidades_fechadas": 12,
        "municipio_ano_sem_todos_os_componentes": 24,
        "municipio_ano_excluidos": 0,
    }
    assert len(cast(list[str], relatorio["negativos"])) == 4


def _com_valor(tmp_path: Path, indicador: str, ano: int, delta: int) -> LotePib:
    original = lote(tmp_path)
    observacoes = tuple(
        o.model_copy(update={"valor": Decimal(str(o.valor)) + delta})
        if (o.indicador, o.municipio_id, o.ano) == (indicador, PARAUAPEBAS, ano)
        else o
        for o in original.observacoes
    )
    return LotePib(**{**original.__dict__, "observacoes": observacoes})


def test_identidade_fora_da_tolerancia_exclui_municipio_e_ano(tmp_path: Path) -> None:
    """Exceção de RN-VPU-12: 3 mil reais a mais num setor tira as sete observações do município e ano."""
    resultado = validacao.validar(_com_valor(tmp_path, "vab_industria", 2012, 3))
    assert resultado.aprovado
    excluidos = cast(list[dict[str, Any]], resultado.relatorio["excluidos"])
    assert [(e["municipio_id"], e["ano"]) for e in excluidos] == [(PARAUAPEBAS, 2012)]
    assert "soma dos setores" in str(excluidos[0]["motivo"])
    assert not any(o.municipio_id == PARAUAPEBAS and o.ano == 2012 for o in resultado.observacoes)


def test_pib_fora_da_tolerancia_exclui(tmp_path: Path) -> None:
    """Exceção de RN-VPU-12: 3 mil reais a mais no PIB passam do limite de 1 em VAB + impostos = PIB."""
    resultado = validacao.validar(_com_valor(tmp_path, "pib_municipal", 2012, 3))
    excluidos = cast(list[dict[str, Any]], resultado.relatorio["excluidos"])
    assert "difere do PIB" in str(excluidos[0]["motivo"])


def test_arredondamento_dentro_da_tolerancia_passa(tmp_path: Path) -> None:
    """Exceção de RN-VPU-12: deslocar um setor em 1 mil reais ainda fica dentro do arredondamento."""
    resultado = validacao.validar(_com_valor(tmp_path, "vab_agropecuaria", 2012, 1))
    assert resultado.relatorio["excluidos"] == []


def configurar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifesto: Path) -> Path:
    monkeypatch.setenv("OBS_DATA_DIR", str(tmp_path / "dados"))
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path / "publicado"))
    monkeypatch.setenv("OBS_MANIFESTO", str(manifesto))
    return tmp_path / "publicado"


def test_coleta_publica_e_so_se_mudou(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifesto: Path
) -> None:
    """RN-VPU-01/03 e RN-TMP-02: publica o parcial; sem mudança no SIDRA, não publica de novo."""
    publicado = configurar(tmp_path, monkeypatch, manifesto)
    primeiro = coleta.executar_pib(buscar=buscar_falso)
    assert primeiro["situacao"] == "aprovado"
    pacote = json.loads((publicado / "pacote.json").read_text(encoding="utf-8"))
    assert set(pacote["indicadores"]) == set(INDICADORES_ESPERADOS)
    tabela = pl.read_parquet(publicado / "versoes" / pacote["versao"] / "pib_municipal.parquet")
    assert tabela.schema["valor"] == pl.Decimal(38, 2) and tabela.height == 12 * len(ANOS)
    segundo = coleta.executar_pib(somente_se_mudou=True, buscar=buscar_falso)
    assert segundo["situacao"] == "sem_mudanca"
    assert json.loads((publicado / "pacote.json").read_text(encoding="utf-8"))["versao"] == pacote["versao"]


def test_revisao_prevalece_e_vai_para_o_relatorio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifesto: Path
) -> None:
    """Decisão de 27/11/2026: a edição nova prevalece; os anos alterados ficam no relatório."""
    configurar(tmp_path, monkeypatch, manifesto)
    coleta.executar_pib(buscar=buscar_falso)

    def revisar(d: list[dict[str, Any]]) -> None:
        for serie in d[0]["resultados"][0]["series"]:
            if serie["localidade"]["id"] == "1501576":
                serie["serie"]["2023"] = "336975"

    revisado = alterar(revisar)
    resumo = coleta.executar_pib(
        somente_se_mudou=True, buscar=lambda url: PERIODOS if url == pib_ibge.URL_PERIODOS else revisado
    )
    assert resumo["situacao"] == "aprovado"
    relatorio = json.loads(Path(str(resumo["relatorio"])).read_text(encoding="utf-8"))
    assert relatorio["anos_alterados"] == ["pib_municipal:2023"]


def test_layout_alterado_preserva_o_pacote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifesto: Path
) -> None:
    """RN-VPU-03: lote reprovado não troca o pacote publicado."""
    publicado = configurar(tmp_path, monkeypatch, manifesto)
    coleta.executar_pib(buscar=buscar_falso)
    antes = (publicado / "pacote.json").read_bytes()
    quebrado = alterar(lambda d: d[0].update(unidade="Reais"))
    resumo = coleta.executar_pib(buscar=lambda url: PERIODOS if url == pib_ibge.URL_PERIODOS else quebrado)
    assert resumo["situacao"] == "reprovado"
    assert (publicado / "pacote.json").read_bytes() == antes
