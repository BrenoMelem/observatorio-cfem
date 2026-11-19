from decimal import Decimal

from scripts.financas.conferir_fonte_cfem import cfem_distribuida, estagios_msc, totais_dca


def msc(conta, natureza, fonte, valor, ano="2024", cod="1505536"):
    return {"cod_ibge": cod, "ano": ano, "conta_contabil": conta, "natureza_conta": natureza,
            "fonte_recursos": fonte, "valor": valor}


def test_estagios_somam_credito_menos_debito_e_separam_a_fonte_cfem():
    linhas = [
        msc("622130100", "C", "1708", "100"),   # empenho
        msc("622130100", "D", "1708", "100"),   # sai do "a liquidar"...
        msc("622130300", "C", "1708", "100"),   # ...e vira "liquidado a pagar"
        msc("622130300", "D", "1708", "60"),
        msc("622130400", "C", "1708", "60"),    # pagamento
        msc("622130400", "C", "1500", "40"),    # outra fonte
        msc("622110000", "C", "1500", "999"),   # crédito disponível: fora dos estágios
    ]
    s = estagios_msc(linhas)
    assert s[("1505536", 2024, "cfem")] == {"empenhada": Decimal(100), "liquidada": Decimal(100), "paga": Decimal(60)}
    assert s[("1505536", 2024, "total")]["paga"] == Decimal(100)


def test_dca_e_anm():
    dca = totais_dca([{"anexo": "I-D", "cod_conta": "TotalDespesas", "coluna": "Despesas Pagas",
                       "cod_ibge": "1505536", "exercicio": "2024", "valor": "100.5"},
                      {"anexo": "I-C", "cod_conta": "TotalDespesas", "coluna": "Despesas Pagas",
                       "cod_ibge": "1505536", "exercicio": "2024", "valor": "1"}])
    assert dca[("1505536", 2024)] == {"paga": Decimal("100.5")}
    anm = cfem_distribuida([{"CodigoEnte": "1505536", "Ente": "Município", "Ano": "2024", "Valor": "1,50"},
                            {"CodigoEnte": "15", "Ente": "Estado", "Ano": "2024", "Valor": "9,00"}])
    assert anm == {("1505536", 2024): Decimal("1.50")}
