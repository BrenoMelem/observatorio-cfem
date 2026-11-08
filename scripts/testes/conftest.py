"""Utilidades comuns dos testes."""

import threading
from contextlib import contextmanager

import pytest

from scripts.cfem.preparar import CABECALHO_ANM


def csv_anm(linhas, fim="\n"):
    return fim.join(",".join(f'"{v}"' for v in linha) for linha in linhas) + fim


def linha_anm(ano, mes, codigo, valor, **extra):
    valores = {c: "" for c in CABECALHO_ANM}
    valores.update({"Ano": ano, "Mês": mes, "CodigoMunicipio": codigo, "ValorRecolhido": valor, **extra})
    return [valores[c] for c in CABECALHO_ANM]


def gravar_csv(caminho, texto):
    caminho.write_bytes(texto.encode("latin-1"))
    return caminho


@contextmanager
def servidor_em_thread(servidor):
    fio = threading.Thread(target=servidor.serve_forever, daemon=True)
    fio.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_address[1]}"
    finally:
        servidor.shutdown()
        servidor.server_close()


@pytest.fixture
def pasta_dados(tmp_path):
    return tmp_path / "observatorio"
