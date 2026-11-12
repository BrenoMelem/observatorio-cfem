import json

from scripts.cfem.anm_arquivos import FONTES
from scripts.cfem.arquivar_anm import arquivar
from scripts.cfem.comparar_versoes_anm import comparar, texto_markdown
from scripts.testes.conftest import CABECALHO_ANM, csv_anm, gravar_csv, linha_anm


def _arrecadacao(*linhas):
    return csv_anm([CABECALHO_ANM, *linhas])


def test_comparar_separa_adicionadas_removidas_e_modificadas_no_recorte(tmp_path):
    comum = linha_anm("2024", "2", "1505536", "100,00")
    antigo = gravar_csv(tmp_path / "a.csv", _arrecadacao(comum, comum, linha_anm("2024", "3", "1504208", "50,50")))
    novo = gravar_csv(tmp_path / "n.csv", _arrecadacao(comum, linha_anm("2024", "3", "1504208", "60,00"),
                                                       linha_anm("2024", "3", "3550308", "9,00"),
                                                       linha_anm("2024", "4", "1502152", "7,00")))
    r = comparar("arrecadacao", antigo, novo)
    assert (r["linhas_antigo"], r["linhas_novo"]) == (3, 4)
    assert (r["adicionadas"], r["removidas"], r["modificadas"]) == (2, 1, 1)
    assert r["recorte_removidas"] == {"2024": {"Parauapebas": {"linhas": 1, "valor": "100.00"}}}  # a duplicata que saiu
    assert r["recorte_adicionadas"] == {"2024": {"Canaã dos Carajás": {"linhas": 1, "valor": "7.00"}}}
    assert r["recorte_modificadas"] == {"2024": {"Marabá": {"linhas": 1, "valor_antes": "50.50", "valor_depois": "60.00"}}}
    assert "São Paulo" not in json.dumps(r) and "3550308" not in json.dumps(r)  # fora do recorte
    texto = texto_markdown(r)
    assert "adicionadas 2, removidas 1, modificadas 1" in texto
    assert "| 2024 | Marabá | 1 | 50.50 | 60.00 | 9.50 |" in texto


def test_comparar_pareia_uma_a_uma_quando_a_chave_se_repete(tmp_path):
    def linha(valor):
        return linha_anm("2024", "3", "1504208", valor)

    antigo = gravar_csv(tmp_path / "a.csv", _arrecadacao(linha("1,00"), linha("2,00")))
    novo = gravar_csv(tmp_path / "n.csv", _arrecadacao(linha("5,00"), linha("6,00"), linha("7,00")))
    r = comparar("arrecadacao", antigo, novo)
    assert (r["adicionadas"], r["removidas"], r["modificadas"]) == (1, 0, 2)
    assert r["recorte_modificadas"]["2024"]["Marabá"] == {"linhas": 2, "valor_antes": "3.00", "valor_depois": "11.00"}
    assert r["recorte_adicionadas"]["2024"]["Marabá"] == {"linhas": 1, "valor": "7.00"}


def test_comparar_nao_pareia_linha_que_mudou_em_outra_coluna(tmp_path):
    antigo = gravar_csv(tmp_path / "a.csv", _arrecadacao(linha_anm("2024", "3", "1504208", "50,00")))
    novo = gravar_csv(tmp_path / "n.csv", _arrecadacao(linha_anm("2024", "4", "1504208", "50,00")))
    r = comparar("arrecadacao", antigo, novo)
    assert (r["adicionadas"], r["removidas"], r["modificadas"]) == (1, 1, 0)


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
    assert "removidas 0, modificadas 1" in (tmp_path / "p3" / "diferencas.md").read_text(encoding="utf-8")
