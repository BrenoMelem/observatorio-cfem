import json

from scripts.cfem.anm_arquivos import FONTES
from scripts.cfem.arquivar_anm import arquivar
from scripts.cfem.comparar_versoes_anm import comparar
from scripts.testes.conftest import CABECALHO_ANM, csv_anm, gravar_csv, linha_anm


def _arrecadacao(*linhas):
    return csv_anm([CABECALHO_ANM, *linhas])


def test_comparar_conta_linhas_removidas_e_adicionadas_no_recorte(tmp_path):
    comum = linha_anm("2024", "2", "1505536", "100,00")
    antigo = gravar_csv(tmp_path / "a.csv", _arrecadacao(comum, comum, linha_anm("2024", "3", "1504208", "50,50")))
    novo = gravar_csv(tmp_path / "n.csv", _arrecadacao(comum, linha_anm("2024", "3", "1504208", "60,00"),
                                                       linha_anm("2024", "3", "3550308", "9,00")))
    r = comparar("arrecadacao", antigo, novo)
    assert (r["linhas_antigo"], r["linhas_novo"]) == (3, 3)
    assert r["adicionadas"] == 2 and r["removidas"] == 2
    assert r["recorte_removidas"]["2024"]["Parauapebas"] == {"linhas": 1, "valor": "100.00"}
    assert r["recorte_removidas"]["2024"]["Marabá"] == {"linhas": 1, "valor": "50.50"}
    assert r["recorte_adicionadas"]["2024"]["Marabá"] == {"linhas": 1, "valor": "60.00"}
    assert "São Paulo" not in json.dumps(r) and "3550308" not in json.dumps(r)  # fora do recorte


def test_arquivar_so_acrescenta_ao_manifesto_quando_algo_mudou(tmp_path):
    conteudo = {"v": _arrecadacao(linha_anm("2024", "2", "1505536", "100,00"))}

    def baixador(url, destino):
        nome = destino.stem
        if nome == "arrecadacao":
            destino.write_bytes(conteudo["v"].encode("latin-1"))
        else:
            destino.write_bytes('"Ano","Valor","CodigoEnte","Município","UF","AnoPublicação"\n'.encode("latin-1"))
        return {"last_modified": "x", "etag": None, "content_length": None}

    manifesto = tmp_path / "manifesto.json"
    r1 = arquivar(tmp_path / "p1", manifesto, baixador=baixador)
    assert r1["mudou"] and set(r1["arquivos_alterados"]) == set(FONTES)
    r2 = arquivar(tmp_path / "p2", manifesto, anterior=tmp_path / "p1", baixador=baixador)
    assert not r2["mudou"] and len(json.loads(manifesto.read_text())) == 1
    conteudo["v"] = _arrecadacao(linha_anm("2024", "2", "1505536", "999,00"))
    r3 = arquivar(tmp_path / "p3", manifesto, anterior=tmp_path / "p1", baixador=baixador)
    assert r3["arquivos_alterados"] == ["arrecadacao"]
    entradas = json.loads(manifesto.read_text())
    assert len(entradas) == 2 and entradas[1]["arquivos"]["arrecadacao"]["mudou"] is True
    assert entradas[1]["arquivos"]["arrecadacao"]["recorte_por_ano"]["2024"]["valor"] == "999.00"
    assert "removidas 1" in (tmp_path / "p3" / "diferencas.md").read_text(encoding="utf-8")
