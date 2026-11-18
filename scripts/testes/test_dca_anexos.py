"""Testes offline do coletor de anexos da DCA (scripts/financas/dca_anexos.py)."""

import csv

import pytest

from scripts.financas import dca_anexos as d


def payload_para(codigo, exercicio, anexo, itens):
    return {
        "hasMore": False,
        "items": [
            {"cod_ibge": codigo, "exercicio": exercicio, "anexo": anexo, "coluna": coluna,
             "cod_conta": cod, "conta": conta, "valor": valor}
            for coluna, cod, conta, valor in itens
        ],
    }


def test_nome_do_anexo_muda_em_2013():
    assert d.nome_do_anexo("I-C", 2013) == "Anexo I-C"
    assert d.nome_do_anexo("I-C", 2014) == "DCA-Anexo I-C"
    assert d.nome_do_anexo("I-D", 2024) == "DCA-Anexo I-D"


def test_linhas_do_anexo_mapeia_campos_e_mantem_valor():
    p = payload_para(1502152, 2024, "DCA-Anexo I-C", [
        ("Receitas Brutas Realizadas", "RO1.7.2.1.50.0.0", "Cota-Parte do ICMS", 656005758.85),
    ])
    linhas = d.linhas_do_anexo(p, "Canaã dos Carajás", 1502152, "I-C", 2024)
    assert linhas == [{
        "municipio": "Canaã dos Carajás", "cod_ibge": 1502152, "exercicio": 2024, "anexo": "I-C",
        "coluna": "Receitas Brutas Realizadas", "cod_conta": "RO1.7.2.1.50.0.0",
        "conta": "Cota-Parte do ICMS", "valor": 656005758.85,
    }]


def test_resposta_de_outro_municipio_ou_anexo_levanta_erro():
    outro_ente = payload_para(1505536, 2024, "DCA-Anexo I-C", [("c", "x", "y", 1)])
    with pytest.raises(d.ContratoSiconfiError):
        d.linhas_do_anexo(outro_ente, "Canaã dos Carajás", 1502152, "I-C", 2024)
    outro_anexo = payload_para(1502152, 2024, "DCA-Anexo I-D", [("c", "x", "y", 1)])
    with pytest.raises(d.ContratoSiconfiError):
        d.linhas_do_anexo(outro_anexo, "Canaã dos Carajás", 1502152, "I-C", 2024)


def test_coletar_registra_erro_sem_interromper_a_coleta(monkeypatch):
    monkeypatch.setattr(d, "MUNICIPIOS", {"Canaã dos Carajás": 1502152, "Parauapebas": 1505536})

    def consultar(anexo, ano, codigo):
        if codigo == 1505536:
            raise OSError("HTTP 503")
        return payload_para(codigo, ano, d.nome_do_anexo(anexo, ano), [("c", "k", "n", 10.0)])

    linhas, resumo = d.coletar(["I-C"], [2024], consultar=consultar, pausa=0)
    assert [r["municipio"] for r in linhas] == ["Canaã dos Carajás"]
    erros = [r for r in resumo if r[5]]
    assert len(erros) == 1 and "HTTP 503" in erros[0][5]


def test_main_grava_csv_com_cabecalho_fora_do_pacote(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "MUNICIPIOS", {"Canaã dos Carajás": 1502152})
    monkeypatch.setattr(d, "consultar_anexo", lambda anexo, ano, codigo: payload_para(
        codigo, ano, d.nome_do_anexo(anexo, ano), [("Despesas Pagas", "DO4.4.00.00.00.00", "Investimentos", 504210130.93)]))
    monkeypatch.setattr(d.time, "sleep", lambda s: None)
    saida = tmp_path / "dca.csv"
    assert d.main(["--anexos", "I-D", "--inicio", "2024", "--fim", "2024", "--saida", str(saida)]) == 0
    with saida.open(encoding="utf-8") as f:
        lidas = list(csv.DictReader(f))
    assert lidas == [{"municipio": "Canaã dos Carajás", "cod_ibge": "1502152", "exercicio": "2024",
                      "anexo": "I-D", "coluna": "Despesas Pagas", "cod_conta": "DO4.4.00.00.00.00",
                      "conta": "Investimentos", "valor": "504210130.93"}]
