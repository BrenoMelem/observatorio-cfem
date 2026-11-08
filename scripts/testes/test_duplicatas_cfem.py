from scripts.cfem.analisar_duplicatas import analisar_duplicatas
from scripts.cfem.preparar import CABECALHO_ANM
from scripts.testes.conftest import csv_anm, gravar_csv


def test_relatorio_confirma_campos_integrais_sem_exportar_identificador(tmp_path):
    linha = {c: "" for c in CABECALHO_ANM}
    linha.update({"Ano": "2025", "Mês": "9", "CodigoMunicipio": "1505536", "CPF_CNPJ": "IDENTIFICADOR_FICTICIO",
                  "DataCriacao": "2025-10-01"})
    valores = [linha[c] for c in CABECALHO_ANM]
    origem = gravar_csv(tmp_path / "origem.csv", csv_anm([CABECALHO_ANM, valores, valores]))
    destino = tmp_path / "relatorio.json"
    r = analisar_duplicatas(origem, destino)
    assert r["duplicatas"] == 1
    assert r["linhas_duplicadas"][0]["campos_identicos_incluindo_identificador"] is True
    assert r["linhas_duplicadas"][0]["datas_criacao_iguais"] is True
    texto = destino.read_text(encoding="utf-8")
    assert "IDENTIFICADOR_FICTICIO" not in texto and "CPF_CNPJ" not in texto
