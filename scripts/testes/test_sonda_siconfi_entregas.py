from scripts.sondas.siconfi_entregas import entregas_dca


def test_filtra_so_a_dca():
    itens = [{"entregavel": "Balanço Anual (DCA)", "status_relatorio": "RE", "data_status": "2025-05-28T19:06:59Z",
              "forma_envio": "M"},
             {"entregavel": "MSC Agregada", "status_relatorio": None}]
    assert entregas_dca(itens) == [{"status": "RE", "data_status": "2025-05-28T19:06:59Z", "forma_envio": "M"}]
