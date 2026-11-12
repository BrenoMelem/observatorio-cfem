import json
from datetime import datetime, timezone

import pytest
from openpyxl import Workbook

from scripts.emissoes.seeg import (
    ContratoSeegError, codigo_ibge, edicao_do_nome, executar_seeg, extrair_seeg,
)

AGORA = lambda: datetime(2026, 11, 10, 12, tzinfo=timezone.utc)  # noqa: E731
CABECALHO = ["Emissão/Remoção/Bunker", "Setor de emissão", "Categoria emissora", "Município", "ID Território", 1990, 1991]


def planilha(caminho, linhas, cabecalho=CABECALHO, aba="Dados"):
    livro = Workbook()
    livro.active.title = "Leia antes"
    dados = livro.create_sheet(aba)
    dados.append(cabecalho)
    for linha in linhas:
        dados.append(linha)
    livro.save(caminho)
    return caminho


LINHAS = [
    ["Emissão", "Energia", "Industrial", "Canaã dos Carajás (PA)", "11502152", 10.0, 20.0],
    ["Emissão", "Energia", "Transportes", "Canaã dos Carajás (PA)", "11502152", 1.5, 2.5],   # soma com a anterior
    ["Remoção", "Energia", "Floresta", "Canaã dos Carajás (PA)", "11502152", 4.0, None],      # não compensa a emissão
    ["Emissão", "Agropecuária", "Solos", "Marabá (PA)", 11504208, 7.0, 8.0],                   # id numérico
    ["Emissão", "Energia", "Industrial", "Candói (PR)", "14104428", 99.0, 99.0],              # fora do recorte
    ["Emissão", "Energia", "Industrial", "Sem prefixo (PA)", "1502152", 5.0, 5.0],            # formato inesperado
]


def test_reconstitui_o_ibge_do_id_territorio():
    assert codigo_ibge("14104428") == "4104428" and codigo_ibge(11502152) == "1502152"
    assert codigo_ibge("11502152.0") == "1502152"
    assert codigo_ibge("1502152") is None and codigo_ibge(None) is None and codigo_ibge("21502152") is None


def test_edicao_vem_do_nome_do_arquivo():
    assert edicao_do_nome("Dados-municipais-resumido-CO2e-GWP-AR5-14.0.xlsx") == "14.0"
    assert edicao_do_nome("outro.xlsx") is None


def test_extrai_o_recorte_agregado_sem_compensar_remocao(tmp_path):
    caminho = planilha(tmp_path / "m-14.0.xlsx", LINHAS)
    saida, resumo = extrair_seeg(caminho, "2026-11-10T12:00:00Z", "14.0")
    chave = {(l["municipio_id"], l["tipo"], l["setor"], l["ano"]): l["valor"] for l in saida}
    assert chave[("1502152", "Emissão", "Energia", 1990)] == 11.5
    assert chave[("1502152", "Remoção", "Energia", 1990)] == 4.0
    assert ("1502152", "Remoção", "Energia", 1991) not in chave          # valor vazio não vira zero
    assert chave[("1504208", "Emissão", "Agropecuária", 1991)] == 8.0
    assert all(l["municipio_id"] in {"1502152", "1504208"} for l in saida)
    assert resumo["linhas_lidas"] == 6 and resumo["linhas_do_recorte"] == 4
    assert resumo["municipios_encontrados"] == ["1502152", "1504208"] and "1505536" in resumo["municipios_ausentes"]
    assert resumo["anos"] == [1990, 1991] and resumo["nomes_divergentes"] == {}


def test_aponta_nome_divergente_do_municipio(tmp_path):
    linhas = [["Emissão", "Energia", "x", "Outra Cidade (PA)", "11502152", 1.0, 1.0]]
    _, resumo = extrair_seeg(planilha(tmp_path / "m.xlsx", linhas), "x")
    assert resumo["nomes_divergentes"] == {"1502152": "Outra Cidade (PA)"}


@pytest.mark.parametrize("cabecalho,aba", [
    ([c for c in CABECALHO if c != "ID Território"], "Dados"),
    (["a", "b"], "Dados"),
    (CABECALHO, "Outra"),
])
def test_falha_quando_o_contrato_muda(tmp_path, cabecalho, aba):
    with pytest.raises(ContratoSeegError):
        extrair_seeg(planilha(tmp_path / "m.xlsx", [], cabecalho, aba), "x")


def test_executa_com_download_injetado_e_guarda_metadados(tmp_path):
    origem = planilha(tmp_path / "origem.xlsx", LINHAS)

    def baixar(url, destino):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(origem.read_bytes())

    pasta = tmp_path / "obs"
    r = executar_seeg(pasta, "https://exemplo/Dados-municipais-resumido-CO2e-GWP-AR5-14.0.xlsx", None, baixar, AGORA)
    assert r["situacao"] == "publicado_provisorio" and r["edicao"] == "14.0"
    assert r["linhas_publicadas"] == 5  # Canaã: emissão (2 anos) e remoção (1 ano); Marabá: emissão (2 anos)
    assert len(r["arquivo_sha256"]) == 64 and r["arquivo_bytes"] > 0
    assert "acessado em 2026-11-10" in r["citacao"]
    assert list((pasta / "bruto" / "seeg").glob("*14.0.xlsx"))
    publicado = json.loads((pasta / "publicado" / "emissoes-seeg.json").read_text(encoding="utf-8"))
    assert publicado and publicado[0]["edicao_fonte"] == "14.0"


def test_falha_preserva_o_lote_e_registra_o_erro(tmp_path):
    pasta = tmp_path / "obs"
    bom = planilha(tmp_path / "bom-14.0.xlsx", LINHAS)
    executar_seeg(pasta, arquivo=bom, agora_fn=AGORA)
    arquivo = pasta / "publicado" / "emissoes-seeg.json"
    antes = arquivo.read_text(encoding="utf-8")
    ruim = planilha(tmp_path / "ruim.xlsx", [], CABECALHO[:3])
    with pytest.raises(ContratoSeegError) as erro:
        executar_seeg(pasta, arquivo=ruim, agora_fn=AGORA)
    assert erro.value.relatorio["situacao"] == "bloqueado" and arquivo.read_text(encoding="utf-8") == antes
    vazio = planilha(tmp_path / "vazio.xlsx", [["Emissão", "Energia", "x", "Candói (PR)", "14104428", 1.0, 1.0]])
    with pytest.raises(ContratoSeegError):
        executar_seeg(pasta, arquivo=vazio, agora_fn=AGORA)
    assert arquivo.read_text(encoding="utf-8") == antes
