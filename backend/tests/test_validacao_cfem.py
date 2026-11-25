"""RN-VPU-07/12: gabaritos sintéticos, sem rede nem homologação de dados reais."""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from test_fonte_cfem import arquivo_sintetico

from observatorio.fontes.cfem_arrecadacao import converter
from observatorio.validacao.cfem import Referencia


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


def test_controle_nacional_oficial_bloqueia_diferenca_superior_a_um_por_cento(tmp_path: Path) -> None:
    """RN-CFE-12: compara o ano fechado com total nacional publicado, sem substituir RN-VPU-07."""
    from observatorio.validacao.cfem import Referencia, ReferenciaNacional, validar

    lote = converter(arquivo_sintetico(tmp_path), tmp_path / "bruto")
    lote = replace(lote, registros_mensais={f"2025:{m}": 100 for m in range(1, 13)})
    referencia = ReferenciaNacional(
        ano=2025,
        valor=Decimal("100.00"),
        documento="Tabela nacional da ANM, fixture sintética",
        url="https://sistemas.anm.gov.br/arrecadacao/extra/relatorios/arrecadacao_cfem_ano.aspx?ano=2025",
        consultado_em=date(2026, 11, 23),
        sha256="a" * 64,
    )
    item = lote.observacoes[0]
    municipal = Referencia(
        municipio_id=item.municipio_id or "",
        ano=item.ano,
        mes=item.mes or 1,
        valor=Decimal(str(item.valor)),
        documento="Tabela municipal, fixture sintética",
        url="https://sistemas.anm.gov.br/teste",
        consultado_em=date(2026, 11, 23),
        sha256="b" * 64,
    )
    resultado = validar(lote, [municipal], referencias_nacionais=[referencia])
    assert any("RN-CFE-12" in erro for erro in resultado.erros)
    controle = resultado.relatorio["controle_nacional"]
    assert isinstance(controle, list)
    assert controle[0]["referencia"] == "100.00"


def test_captura_alterada_bloqueia_referencia(tmp_path: Path) -> None:
    """RN-VPU-07: o SHA declarado precisa corresponder à captura disponível."""
    from observatorio.coleta import conferir_evidencias
    from observatorio.validacao.cfem import Referencia

    (tmp_path / "anm-pa-2025.md").write_text("conteúdo diferente", encoding="utf-8")
    referencia = Referencia(
        municipio_id="1505536",
        ano=2025,
        mes=1,
        valor=Decimal("1.00"),
        documento="Fixture sintética",
        url="https://sistemas.anm.gov.br/teste",
        consultado_em=date(2026, 11, 23),
        sha256="a" * 64,
    )
    with pytest.raises(ValueError, match="SHA-256"):
        conferir_evidencias([referencia], [], tmp_path)


def _referencia_2025(sha256: str) -> Referencia:
    return Referencia(
        municipio_id="1505536",
        ano=2025,
        mes=1,
        valor=Decimal("1.00"),
        documento="Fixture sintética",
        url="https://sistemas.anm.gov.br/teste",
        consultado_em=date(2026, 11, 25),
        sha256=sha256,
    )


def test_captura_html_gz_confere_o_hash_do_html_original(tmp_path: Path) -> None:
    """RN-VPU-07: na captura .html.gz, o SHA-256 é do corpo HTTP, não do arquivo comprimido."""
    import gzip
    import hashlib

    from observatorio.coleta import conferir_evidencias

    corpo = b"<table><tr><td>PARAUAPEBAS</td></tr></table>"
    (tmp_path / "anm-pa-2025.html.gz").write_bytes(gzip.compress(corpo))

    conferir_evidencias([_referencia_2025(hashlib.sha256(corpo).hexdigest())], [], tmp_path)
    with pytest.raises(ValueError, match="SHA-256"):
        conferir_evidencias([_referencia_2025("a" * 64)], [], tmp_path)


def test_captura_html_gz_corrompida_falha(tmp_path: Path) -> None:
    """RN-VPU-07: captura ilegível bloqueia a homologação com erro explícito."""
    from observatorio.coleta import conferir_evidencias

    (tmp_path / "anm-pa-2025.html.gz").write_bytes(b"nao e gzip")
    with pytest.raises(ValueError, match="ilegível"):
        conferir_evidencias([_referencia_2025("a" * 64)], [], tmp_path)
