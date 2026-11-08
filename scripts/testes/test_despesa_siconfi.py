import json
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from scripts.financas.dca_lote import ContratoSiconfiError, executar_despesa, validar_pagina


def test_dca_valida_ente_anexo_estagio_e_mantem_lote_sem_homologacao(pasta_dados):
    def buscar(url):
        q = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        itens = [{"exercicio": int(q["an_exercicio"]), "cod_ibge": q["id_ente"], "anexo": "DCA-Anexo I-E",
                  "conta": "12 - Educação", "cod_conta": "12", "coluna": coluna, "valor": 100 - i}
                 for i, coluna in enumerate(["Despesas Empenhadas", "Despesas Liquidadas", "Despesas Pagas"])]
        return 200, json.dumps({"items": itens, "hasMore": False, "limit": 5000})

    r = executar_despesa(pasta_dados, 2025, buscar, lambda: datetime(2026, 10, 30, 12, tzinfo=timezone.utc))
    assert r["situacao"] == "bloqueado" and len(r["municipios_presentes"]) == 12
    tratado = json.loads((pasta_dados / "tratado" / "siconfi" / "dca-2025.json").read_text(encoding="utf-8"))
    assert len(tratado) == 36
    assert not (pasta_dados / "publicado" / "despesa-siconfi.json").exists()
    with pytest.raises(ContratoSiconfiError):
        validar_pagina({"items": [{"exercicio": 2025, "cod_ibge": "1502152", "anexo": "DCA-Anexo I-E",
                                   "conta": "12 - Educação", "coluna": "Despesas Pagas", "valor": None}],
                        "hasMore": False}, "1502152", 2025, 0)
