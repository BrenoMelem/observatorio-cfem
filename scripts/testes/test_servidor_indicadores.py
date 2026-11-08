import json

import httpx

from scripts.servidor.servidor import criar_servidor
from scripts.testes.conftest import servidor_em_thread


def test_painel_itera_manifesto_commodities_globais_e_despesa_bloqueada(pasta_dados):
    (pasta_dados / "publicado").mkdir(parents=True)
    (pasta_dados / "publicado" / "commodities.json").write_text(json.dumps([{
        "indicador": "preco_cobre", "municipio_id": None, "ano": 2025, "mes": 9, "valor": 8000,
        "estado_validacao": "provisório", "atualizado_em": "2026-10-30T12:00:00.000Z"}]), encoding="utf-8")
    with servidor_em_thread(criar_servidor(pasta_dados)) as base:
        html = httpx.get(f"{base}/status").text
        assert "População residente estimada" in html
        assert "Preço internacional do cobre" in html
        assert "2025" in html and "Sem publicação" in html
        resposta = httpx.get(f"{base}/api/v1/commodities", params={"indicador": "preco_cobre"})
        assert resposta.status_code == 200 and len(resposta.json()) == 1
        assert httpx.get(f"{base}/api/v1/despesa-funcao").status_code == 503
