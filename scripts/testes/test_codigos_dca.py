from scripts.financas.codigos_dca import codigos_por_ano


def linha(ano, anexo, coluna, cod, conta, valor="1"):
    return {"cod_ibge": "1505536", "exercicio": str(ano), "anexo": anexo, "coluna": coluna,
            "cod_conta": cod, "conta": conta, "valor": valor}


def test_acha_os_codigos_de_cada_periodo():
    linhas = [
        linha(2013, "I-C", "Receitas Realizadas", "RO1.7.2.2.01.01.00", "1.7.2.2.01.01.00 - Cota-Parte do ICMS"),
        linha(2019, "I-C", "Receitas Brutas Realizadas", "RO1.7.2.8.01.1.0", "1.7.2.8.01.1.0 Cota-Parte do ICMS"),
        linha(2019, "I-C", "Deduções - FUNDEB", "RO1.7.2.8.01.1.0", "1.7.2.8.01.1.0 Cota-Parte do ICMS"),
        linha(2013, "I-C", "Receitas Realizadas", "RO1.0.0.0.00.00.00", "1.0.0.0.00.00.00 - Receitas Correntes"),
        linha(2024, "I-D", "Despesas Pagas", "DO4.4.00.00.00.00", "4.4.00.00.00 - Investimentos"),
    ]
    r = codigos_por_ano(linhas, "1505536")
    assert r["cota_parte_icms"][2013] == [("RO1.7.2.2.01.01.00", 1.0)]
    assert r["cota_parte_icms"][2019] == [("RO1.7.2.8.01.1.0", 1.0)]
    assert 2013 in r["receita_corrente"]
    assert 2024 in r["investimento_pago"]
