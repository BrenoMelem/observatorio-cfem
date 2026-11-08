"""Servidor local do protótipo: lê a camada publicada e a expõe por HTTP (população, commodities, despesa, status).

Script de teste/laboratório (não é o produto). Porte do protótipo em Node (servidor.mjs); as rotas seguem
`docs/api/openapi.yaml`. Só lê o que está em `publicado/`; nunca lê dado bruto.

Uso:
    uv run python -m scripts.servidor.servidor        # http://localhost:3000/status

Variáveis de ambiente: PORT (padrão 3000) e OBS_DATA_DIR (padrão output/observatorio).
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts.comum.arquivos import PASTA_PADRAO
from scripts.commodities.fred import csv_commodities, ler_commodities_publicadas
from scripts.financas.dca_lote import ler_despesa_publicada
from scripts.populacao.atualizar import csv_populacao, ler_publicado

MANIFESTO_PADRAO = Path(__file__).resolve().parents[2] / "data" / "indicadores.json"
JSON_UTF8 = "application/json; charset=utf-8"
INDICADORES_COMMODITIES = ("preco_minerio_ferro", "preco_cobre")
INDICADORES_DESPESA = ("despesa_funcao_empenhada", "despesa_funcao_liquidada", "despesa_funcao_paga")


def _json(valor) -> bytes:
    return json.dumps(valor, ensure_ascii=False).encode()


def _maior_ano(linhas: list[dict]) -> int | None:
    return max(o["ano"] for o in linhas) if linhas else None


def _ultima(linhas: list[dict]) -> str | None:
    datas = sorted(o["atualizado_em"] for o in linhas if o.get("atualizado_em"))
    return datas[-1] if datas else None


def criar_servidor(pasta_dados: str | Path = PASTA_PADRAO, caminho_manifesto: str | Path = MANIFESTO_PADRAO,
                   porta: int = 0, endereco: str = "127.0.0.1") -> ThreadingHTTPServer:
    class Manipulador(BaseHTTPRequestHandler):
        def log_message(self, *args):  # silencioso
            pass

        def _enviar(self, status: int, tipo: str, corpo: bytes | str) -> None:
            dados = corpo.encode() if isinstance(corpo, str) else corpo
            self.send_response(status)
            self.send_header("Content-Type", tipo)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        def _erro(self, status: int, mensagem: str) -> None:
            self._enviar(status, JSON_UTF8, _json({"erro": mensagem}))

        def do_GET(self):  # noqa: N802
            url = urlparse(self.path)
            consulta = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                self._rotear(url.path, consulta)
            except Exception:  # noqa: BLE001
                self._erro(500, "Falha ao ler camada publicada")

        def _rotear(self, caminho: str, consulta: dict) -> None:
            if caminho in ("/api/v1/populacao", "/api/v1/populacao.csv"):
                linhas = ler_publicado(pasta_dados)
                if not linhas:
                    return self._erro(503, "Nenhum lote homologado publicado")
                if caminho.endswith(".csv"):
                    return self._enviar(200, "text/csv; charset=utf-8", csv_populacao(linhas))
                municipio = consulta.get("municipio_id")
                if municipio and not re.fullmatch(r"\d{7}", municipio):
                    return self._erro(400, "municipio_id inválido")
                return self._enviar(200, JSON_UTF8, _json([o for o in linhas if not municipio or o["municipio_id"] == municipio]))
            if caminho in ("/api/v1/commodities", "/api/v1/commodities.csv"):
                linhas = ler_commodities_publicadas(pasta_dados)
                if not linhas:
                    return self._erro(503, "Nenhuma série provisória publicada")
                indicador = consulta.get("indicador")
                if indicador and indicador not in INDICADORES_COMMODITIES:
                    return self._erro(400, "indicador inválido")
                filtradas = [o for o in linhas if not indicador or o["indicador"] == indicador]
                if caminho.endswith(".csv"):
                    return self._enviar(200, "text/csv; charset=utf-8", csv_commodities(filtradas))
                return self._enviar(200, JSON_UTF8, _json(filtradas))
            if caminho == "/api/v1/despesa-funcao":
                linhas = ler_despesa_publicada(pasta_dados)
                if not linhas:
                    return self._erro(503, "Despesa por função aguarda definição de contas e reconciliação independente")
                indicador = consulta.get("indicador")
                if indicador and indicador not in INDICADORES_DESPESA:
                    return self._erro(400, "indicador inválido")
                return self._enviar(200, JSON_UTF8, _json([o for o in linhas if not indicador or o["indicador"] == indicador]))
            if caminho == "/api/v1/status":
                linhas = ler_publicado(pasta_dados)
                return self._enviar(200, JSON_UTF8, _json({
                    "indicador": "populacao_estimada", "situacao": "publicado" if linhas else "sem_publicacao",
                    "ano_referencia": _maior_ano(linhas), "atualizado_em": _ultima(linhas)}))
            if caminho == "/status":
                return self._enviar(200, "text/html; charset=utf-8", self._painel())
            return self._erro(404, "Rota não encontrada")

        def _painel(self) -> str:
            manifesto = json.loads(Path(caminho_manifesto).read_text(encoding="utf-8"))
            commodities = ler_commodities_publicadas(pasta_dados)
            despesa = ler_despesa_publicada(pasta_dados)
            dados = {
                "populacao_estimada": ler_publicado(pasta_dados),
                "preco_minerio_ferro": [o for o in commodities if o["indicador"] == "preco_minerio_ferro"],
                "preco_cobre": [o for o in commodities if o["indicador"] == "preco_cobre"],
            }
            for ind in INDICADORES_DESPESA:
                dados[ind] = [o for o in despesa if o["indicador"] == ind]
            linhas_html = []
            for indicador, definicao in manifesto.items():
                linhas = dados.get(indicador, [])
                situacao = ("Provisório" if all(o["estado_validacao"] == "provisório" for o in linhas)
                            else "Publicado") if linhas else "Sem publicação"
                ano, atualizado = _maior_ano(linhas), _ultima(linhas)
                linhas_html.append(
                    f"<tr><td>{html.escape(definicao['nome'])}</td><td>{situacao}</td><td>{ano or '—'}</td>"
                    f"<td>{html.escape(atualizado) if atualizado else '—'}</td></tr>")
            return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Status do Observatório</title>'
                    "<main><h1>Status dos indicadores</h1><table><caption>Publicações por indicador</caption>"
                    "<thead><tr><th>Indicador</th><th>Situação</th><th>Ano de referência</th>"
                    f"<th>Última atualização</th></tr></thead><tbody>{''.join(linhas_html)}</tbody></table>"
                    '<p><a href="/api/v1/populacao.csv">Baixar CSV da população</a></p></main></html>')

    return ThreadingHTTPServer((endereco, porta), Manipulador)


def main() -> int:
    porta = int(os.environ.get("PORT", "3000"))
    servidor = criar_servidor(porta=porta)
    print(f"Observatório: http://localhost:{porta}/status")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
