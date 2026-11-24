"""Contrato monetário comum: RN-MOD-03/12 e RN-CFE-11."""

from decimal import Decimal

import pytest

from observatorio.api.dtos.publicacao import Observacao


def observacao(valor: object = "1234567890.12") -> Observacao:
    return Observacao.model_validate(
        {
            "indicador": "cfem_arrecadada",
            "municipio_id": "1505536",
            "municipio_nome": "Parauapebas",
            "nivel_territorial": "município",
            "ano": 2025,
            "mes": 1,
            "valor": valor,
            "unidade": "BRL nominal",
            "natureza_valor": "informado",
            "estado_validacao": "provisório",
            "fonte": "ANM",
            "edicao_fonte": "teste sintético",
            "atualizado_em": "2026-11-23T00:00:00Z",
            "versao_tratamento": "1",
        }
    )


def test_dinheiro_decimal_sem_perda() -> None:
    """RN-CFE-11: decimal no domínio e texto no JSON."""
    item = observacao()
    assert isinstance(item.valor, Decimal)
    assert item.model_dump(mode="json")["valor"] == "1234567890.12"


def test_dinheiro_nao_finito_rejeitado() -> None:
    """RN-MOD-12: erro não se converte em ausência."""
    with pytest.raises(ValueError):
        observacao("NaN")
