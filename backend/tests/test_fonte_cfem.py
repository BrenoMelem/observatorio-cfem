"""RN-VPU-04/11 e RN-CFE-11: contrato, duplicatas e dinheiro (fixtures sintéticas)."""

import csv
from decimal import Decimal
from pathlib import Path

import pytest

CABECALHO = [
    "Ano",
    "Mês",
    "Processo",
    "AnoDoProcesso",
    "Tipo_PF_PJ",
    "CPF_CNPJ",
    "Substância",
    "UF",
    "CodigoMunicipio",
    "Município",
    "QuantidadeComercializada",
    "UnidadeDeMedida",
    "ValorRecolhido",
    "DataCriacao",
]


def arquivo_sintetico(pasta: Path, valor: str = "0,0049", duplicar: bool = True) -> Path:
    arquivo = pasta / "sintetico.csv"
    linha = [
        "2025",
        "1",
        "teste",
        "2025",
        "J",
        "",
        "FERRO",
        "PA",
        "1505536",
        "PARAUAPEBAS",
        "1",
        "t",
        valor,
        "2025-01-01",
    ]
    with arquivo.open("w", encoding="latin-1", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(CABECALHO)
        escritor.writerow(linha)
        if duplicar:
            escritor.writerow(linha)
    return arquivo


def test_soma_antes_de_arredondar_e_preserva_duplicatas(tmp_path: Path) -> None:
    """RN-CFE-11, RN-VPU-11: 0,0049 + 0,0049 = 0,01; duas linhas preservadas."""
    from observatorio.fontes.cfem_arrecadacao import converter

    lote = converter(arquivo_sintetico(tmp_path), tmp_path / "bruto")
    assert lote.observacoes[0].valor == Decimal("0.01")
    assert lote.duplicatas == 1
    assert lote.linhas_recorte == 2
    assert lote.observacoes[0].estado_validacao == "provisório"
    assert lote.sha256 and lote.bruto.is_file()


@pytest.mark.parametrize("valor", ["", "abc", "NaN", "1,23456"])
def test_valor_invalido_falha(tmp_path: Path, valor: str) -> None:
    """RN-VPU-04: não converter erro em nulo."""
    from observatorio.fontes.cfem_arrecadacao import converter

    with pytest.raises(ValueError):
        converter(arquivo_sintetico(tmp_path, valor), tmp_path / "bruto")


def test_layout_alterado_falha(tmp_path: Path) -> None:
    """RN-VPU-04: mudança de cabeçalho bloqueia explicitamente."""
    from observatorio.fontes.cfem_arrecadacao import converter

    arquivo = arquivo_sintetico(tmp_path)
    arquivo.write_text(
        arquivo.read_text(encoding="latin-1").replace("ValorRecolhido", "Valor"), encoding="latin-1"
    )
    with pytest.raises(ValueError, match="colunas"):
        converter(arquivo, tmp_path / "bruto")


def test_amostra_real_anonimizada_confere_colunas(tmp_path: Path) -> None:
    """RN-VPU-04: amostra real de oito linhas, processo/documento anonimizados."""
    from observatorio.fontes.cfem_arrecadacao import converter

    amostra = Path(__file__).parent / "fixtures" / "cfem-arrecadacao-real.csv"
    with amostra.open(encoding="latin-1", newline="") as entrada:
        assert tuple(next(csv.reader(entrada))) == tuple(CABECALHO)
    lote = converter(amostra, tmp_path / "bruto")
    assert lote.linhas_lidas == 8
    assert lote.linhas_recorte == 8
    assert {o.municipio_id for o in lote.observacoes} == {"1502152", "1505536"}
