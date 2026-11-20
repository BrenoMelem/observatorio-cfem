from scripts.sondas.basedosdados_colunas import colunas


def test_extrai_dataset_tabela_e_colunas():
    resposta = {"data": {"allTable": {"edges": [{"node": {
        "slug": "microdados_movimentacao", "dataset": {"slug": "caged"},
        "columns": {"edges": [{"node": {"name": "ano"}}, {"node": {"name": "id_municipio"}}]}}}]}}}
    assert colunas(resposta) == [("caged", "microdados_movimentacao", ["ano", "id_municipio"])]
