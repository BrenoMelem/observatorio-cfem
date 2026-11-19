import struct

from scripts.sondas.ibge_bairros import contar_por_municipio, ler_dbf


def dbf(campos, linhas):
    """Monta um .dbf mínimo (dBase III) com campos de texto."""
    tam_registro = 1 + sum(t for _, t in campos)
    tam_cabecalho = 32 + 32 * len(campos) + 1
    cab = bytes([3, 124, 11, 19]) + struct.pack("<IHH", len(linhas), tam_cabecalho, tam_registro) + bytes(20)
    for nome, tamanho in campos:
        cab += nome.encode().ljust(11, b"\x00") + b"C" + bytes(4) + bytes([tamanho, 0]) + bytes(14)
    cab += b"\x0d"
    corpo = b"".join(b" " + b"".join(v.encode().ljust(t) for v, (_, t) in zip(linha, campos)) for linha in linhas)
    return cab + corpo + b"\x1a"


def test_le_dbf_e_conta_os_doze_municipios():
    conteudo = dbf([("CD_MUN", 7), ("NM_BAIRRO", 10)],
                   [("1501402", "Centro"), ("1501402", "Nazaré"), ("1505536", "Rio Verde")])
    registros = ler_dbf(conteudo)
    assert registros[1] == {"CD_MUN": "1501402", "NM_BAIRRO": "Nazaré"}
    contagem = contar_por_municipio(registros)
    assert contagem["1505536"] == 1
    assert contagem["1502152"] == 0
    assert "1501402" not in contagem  # Belém não é da RI Carajás
