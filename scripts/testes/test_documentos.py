import json

from scripts.cfem.arquivar_documentos import arquivar_documentos


def test_documento_novo_so_entra_quando_o_conteudo_muda_e_erro_nao_derruba_os_outros(tmp_path):
    lista = tmp_path / "lista.json"
    lista.write_text(json.dumps([
        {"nome": "a", "url": "https://x/a.pdf"}, {"nome": "b", "url": "https://x/b.pdf"}]), encoding="utf-8")
    conteudo = {"a": b"v1"}

    def baixador(url, destino):
        if url.endswith("b.pdf"):
            raise OSError("HTTP 404")
        destino.write_bytes(conteudo["a"])
        return {"content_type": "application/pdf", "last_modified": None, "etag": None}

    manifesto = tmp_path / "m.json"
    r1 = arquivar_documentos(tmp_path / "p1", lista, manifesto, baixador)
    assert r1["mudou"] and len(r1["novos"]) == 1 and r1["erros"][0]["nome"] == "b"
    r2 = arquivar_documentos(tmp_path / "p2", lista, manifesto, baixador)
    assert not r2["mudou"] and len(json.loads(manifesto.read_text())["a"]["versoes"]) == 1
    conteudo["a"] = b"v2"
    r3 = arquivar_documentos(tmp_path / "p3", lista, manifesto, baixador)
    assert r3["mudou"] and len(json.loads(manifesto.read_text())["a"]["versoes"]) == 2


def _cliente_falso(monkeypatch, respostas):
    """Troca `httpx.stream` por um transporte falso que devolve `respostas` em ordem (exceção ou status)."""
    import httpx

    chamadas = []

    def manipulador(requisicao):
        chamadas.append(requisicao)
        item = respostas[min(len(chamadas), len(respostas)) - 1]
        if isinstance(item, Exception):
            raise item
        return httpx.Response(item, content=b"%PDF-ok", headers={"content-type": "application/pdf"})

    def stream(metodo, url, **kw):
        cliente = httpx.Client(transport=httpx.MockTransport(manipulador))
        return cliente.stream(metodo, url, headers=kw.get("headers"))

    monkeypatch.setattr(httpx, "stream", stream)
    return chamadas


def test_baixar_http_repete_em_reset_de_conexao_e_acaba_baixando(tmp_path, monkeypatch):
    import httpx

    from scripts.cfem.arquivar_anm import baixar_http

    chamadas = _cliente_falso(monkeypatch, [httpx.ConnectError("reset"), httpx.ConnectError("reset"), 200])
    esperas = []
    destino = tmp_path / "a.pdf"
    cab = baixar_http("https://x/a.pdf", destino, (1, 2, 3), esperas.append)
    assert destino.read_bytes() == b"%PDF-ok" and cab["content_type"] == "application/pdf"
    assert len(chamadas) == 3 and esperas == [1, 2]
    assert "Accept-Language" in chamadas[0].headers


def test_baixar_http_repete_5xx_mas_nao_repete_404(tmp_path, monkeypatch):
    import pytest

    from scripts.cfem.arquivar_anm import baixar_http

    chamadas = _cliente_falso(monkeypatch, [503, 200])
    baixar_http("https://x/a.pdf", tmp_path / "a.pdf", (0,), lambda s: None)
    assert len(chamadas) == 2

    chamadas = _cliente_falso(monkeypatch, [404])
    with pytest.raises(OSError, match="HTTP 404"):
        baixar_http("https://x/b.pdf", tmp_path / "b.pdf", (0, 0), lambda s: None)
    assert len(chamadas) == 1


def test_baixar_http_desiste_depois_de_esgotar_as_tentativas(tmp_path, monkeypatch):
    import httpx
    import pytest

    from scripts.cfem.arquivar_anm import baixar_http

    chamadas = _cliente_falso(monkeypatch, [httpx.ConnectError("reset")])
    with pytest.raises(OSError, match="ConnectError"):
        baixar_http("https://x/a.pdf", tmp_path / "a.pdf", (0, 0), lambda s: None)
    assert len(chamadas) == 3
    assert not (tmp_path / "a.pdf").exists()
