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
