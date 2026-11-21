from scripts.cfem.meses_por_municipio import meses_por_ano


def test_conta_meses_dos_doze_a_partir_do_ano():
    linhas = [
        {"CodigoMunicipio": "1501576", "Ano": "2025", "Mês": "1"},
        {"CodigoMunicipio": "1501576", "Ano": "2025", "Mês": "1"},
        {"CodigoMunicipio": "1501576", "Ano": "2024", "Mês": "6"},
        {"CodigoMunicipio": "1501576", "Ano": "2021", "Mês": "3"},
        {"CodigoMunicipio": "1501402", "Ano": "2025", "Mês": "5"},
    ]
    meses = meses_por_ano(linhas, "CodigoMunicipio", 2022)
    assert meses["1501576"] == {2024: [6], 2025: [1]}
    assert meses["1505536"] == {}
    assert "1501402" not in meses
