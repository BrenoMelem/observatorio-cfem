from decimal import Decimal

from scripts.sondas.pib_per_capita_ri import per_capita_ri


def test_soma_sobre_soma_e_media_das_razoes():
    pib = {"a": Decimal(1_000_000), "b": Decimal(50_000)}      # mil reais
    pop = {"a": Decimal(250_000), "b": Decimal(5_000)}
    soma, media = per_capita_ri(pib, pop)
    assert round(soma) == 4118
    assert media == Decimal(7000)
