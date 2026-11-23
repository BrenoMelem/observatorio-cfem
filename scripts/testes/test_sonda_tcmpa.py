from scripts.sondas.tcmpa import classificar_pagina


def test_reconhece_exportacao_de_grade_e_power_bi():
    html = (
        '<a href="/portalsc/X/LISTAGEM_GRID_config_csv.php?a=1">CSV</a>'
        '<a href="/portalsc/X/LISTAGEM_GRID_config_json.php?a=1">JSON</a>'
        '<iframe src="https://app.powerbi.com/view?r=abc123"></iframe>'
    )
    c = classificar_pagina(html)
    assert c["exportacoes_da_grade"] == ["csv", "json"]
    assert c["paineis_power_bi"] == 1
    assert c["tem_power_bi"] is True
    assert c["arquivos_para_baixar"] == []


def test_separa_arquivos_e_programas():
    html = '<a href="https://x/eContas2024_documentacao.zip">doc</a><a href="https://x/analisador.exe">exe</a>'
    c = classificar_pagina(html)
    assert c["arquivos_para_baixar"] == ["https://x/eContas2024_documentacao.zip"]
    assert c["programas_para_baixar"] == ["https://x/analisador.exe"]
    assert c["cita_dados_abertos"] is False
