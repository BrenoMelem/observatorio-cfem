import pytest

from scripts.cfem.preparar import CABECALHO_ANM, ContratoAnmError, analisar_cfem, centesimos
from scripts.testes.conftest import csv_anm, gravar_csv, linha_anm


def test_grao_mensal_ausencia_e_meses_nacionais_sem_total_anual_incompleto(tmp_path):
    arquivo = gravar_csv(tmp_path / "a.csv", csv_anm(
        [CABECALHO_ANM, linha_anm("2025", "1", "1502152", "1.234,50"), linha_anm("2025", "1", "3550308", "3,00"),
         linha_anm("2025", "2", "1502152", "0,00")], fim="\r\n"))
    relatorio, mensais, anuais = analisar_cfem(arquivo)
    assert relatorio["linhas_lidas"] == 3
    assert relatorio["meses_nacionais"]["2025"] == [1, 2]
    assert len(mensais) == 24
    por = {(o["municipio_id"], o["mes"]): o for o in mensais}
    assert por[("1502152", 1)]["valor"] == 1234.5
    assert por[("1502152", 2)]["natureza_valor"] == "zero real"
    assert por[("1507151", 1)]["natureza_valor"] == "ausente"
    assert por[("1507151", 1)]["valor"] is None
    assert anuais == []


def test_total_anual_so_com_doze_meses(tmp_path):
    linhas = [CABECALHO_ANM] + [linha_anm("2024", str(m), "1502152", "1,00") for m in range(1, 13)]
    _, _, anuais = analisar_cfem(gravar_csv(tmp_path / "a.csv", csv_anm(linhas)))
    assert len(anuais) == 1
    assert anuais[0]["municipio_id"] == "1502152" and anuais[0]["valor"] == 12


def test_coluna_alterada_duplicata_e_valor_invalido_bloqueiam(tmp_path):
    trocado = [("CodigoEnte" if c == "CodigoMunicipio" else c) for c in CABECALHO_ANM]
    with pytest.raises(ContratoAnmError):
        analisar_cfem(gravar_csv(tmp_path / "1.csv", csv_anm([trocado, linha_anm("2025", "1", "1502152", "1,00")])))
    repetida = linha_anm("2025", "1", "1502152", "1,00")
    with pytest.raises(ContratoAnmError, match="duplicadas"):
        analisar_cfem(gravar_csv(tmp_path / "2.csv", csv_anm([CABECALHO_ANM, repetida, repetida])))
    with pytest.raises(ContratoAnmError):
        analisar_cfem(gravar_csv(tmp_path / "3.csv", csv_anm([CABECALHO_ANM, linha_anm("2025", "1", "1502152", "abc")])))
    assert centesimos("1.234,5678") == 12345678
