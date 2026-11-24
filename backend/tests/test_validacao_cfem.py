"""RN-VPU-07/12: gabaritos sintéticos, sem rede nem homologação de dados reais."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

from test_fonte_cfem import arquivo_sintetico

from observatorio.fontes.cfem_arrecadacao import converter


def test_sem_referencia_nao_homologa(tmp_path: Path) -> None:
    """RN-VPU-07: outra implementação do mesmo CSV não é publicação independente."""
    from observatorio.validacao.cfem import validar

    lote = converter(arquivo_sintetico(tmp_path), tmp_path / "bruto")
    resultado = validar(lote, [])
    assert not resultado.aprovado
    assert not resultado.observacoes


def test_referencia_mensal_nao_fecha_ano(tmp_path: Path) -> None:
    """RN-CFE-05/06, RN-VPU-12: um centavo bloqueia; mês isolado não fecha ano."""
    from observatorio.validacao.cfem import Referencia, validar

    lote = converter(arquivo_sintetico(tmp_path), tmp_path / "bruto")
    ref = Referencia(
        municipio_id="1505536",
        ano=2025,
        mes=1,
        valor=Decimal(".01"),
        documento="Fixture sintética oficial",
        url="https://sistemas.anm.gov.br/teste",
        consultado_em=date(2026, 11, 23),
        sha256="a" * 64,
    )
    assert not validar(lote, [ref]).aprovado  # o arquivo nacional tem só um mês
    lote = replace(lote, registros_mensais={f"2025:{m}": 100 for m in range(1, 13)})
    resultado = validar(lote, [ref])
    assert resultado.aprovado and len(resultado.observacoes) == 1
    assert resultado.observacoes[0].estado_validacao == "validado"
    assert not validar(lote, [ref.model_copy(update={"valor": Decimal(".02")})]).aprovado


def test_queda_nacional_e_perda_registros_bloqueiam(tmp_path: Path) -> None:
    """RN-VPU-02: queda >2% e perda de qualquer registro regional bloqueiam."""
    from observatorio.validacao.cfem import validar

    lote = converter(arquivo_sintetico(tmp_path), tmp_path / "bruto")
    resultado = validar(
        lote, [], anterior={"totais_nacionais": {"2025": "100"}, "registros_municipais": {"1505536:2025": 3}}
    )
    assert any("encolheu" in motivo for motivo in resultado.erros)
