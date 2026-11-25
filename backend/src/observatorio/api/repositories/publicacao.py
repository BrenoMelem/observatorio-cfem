"""Lê exclusivamente o pacote publicado, sem consultar fonte externa (RN-ENT-01)."""

import hashlib
import io
import json
from pathlib import Path

import polars as pl
from pydantic import ValidationError

from observatorio import config
from observatorio.api.dtos.publicacao import Observacao
from observatorio.modelo.pacote import DescricaoPacote

MANIFESTO = "indicadores.json"
CAMPOS_MANIFESTO = ("fonte", "metodo", "limitacoes")


class PublicacaoInvalida(Exception):
    pass


def resolver_pacote(pasta: Path | None = None) -> tuple[Path, DescricaoPacote | None]:
    """RN-ENT-01: lê o ponteiro uma vez; arquivos ficam numa versão imutável."""
    raiz = pasta or pasta_publicada()
    try:
        conteudo = (raiz / "pacote.json").read_bytes()
    except FileNotFoundError:
        return raiz, None  # compatibilidade explícita com publicação de população da Fase 1
    except OSError as erro:
        raise PublicacaoInvalida("Pacote publicado ilegível") from erro
    try:
        descricao = DescricaoPacote.model_validate_json(conteudo)
        versao = raiz / "versoes" / descricao.versao
        for nome, resumo in descricao.arquivos.items():
            if hashlib.sha256((versao / nome).read_bytes()).hexdigest() != resumo:
                raise ValueError("Hash divergente")
        return versao, descricao
    except (OSError, ValueError) as erro:
        raise PublicacaoInvalida("Integridade do pacote publicado inválida") from erro


def indicadores_publicados(pasta: Path, descricao: DescricaoPacote) -> list[Observacao]:
    """RN-VPU-01, RN-MOD-03: confere tipos, chaves, indicador e estado em cada parquet."""
    observacoes: list[Observacao] = []
    try:
        for indicador, item in descricao.indicadores.items():
            conteudo = (pasta / item.arquivo).read_bytes()
            if hashlib.sha256(conteudo).hexdigest() != item.sha256:
                raise ValueError("Hash divergente")
            tabela = pl.read_parquet(io.BytesIO(conteudo))
            if set(tabela.columns) != set(Observacao.model_fields):
                raise ValueError("Esquema de observação inválido")
            if tabela.schema["ano"] != pl.Int64 or tabela.schema["mes"] != pl.Int64:
                raise ValueError("Tipos temporais inválidos")
            if indicador == "cfem_arrecadada" and tabela.schema["valor"] != pl.Decimal(38, 2):
                raise ValueError("Dinheiro sem precisão decimal")
            linhas = [Observacao.model_validate(linha) for linha in tabela.iter_rows(named=True)]
            # RN-CFE-06: "provisório" só no último ano publicado (o ano aberto); o resto é validado.
            ultimo_ano = max((o.ano for o in linhas), default=0)
            if any(
                o.indicador != indicador or (o.estado_validacao != "validado" and o.ano != ultimo_ano)
                for o in linhas
            ):
                raise ValueError("Indicador ou estado inválido")
            chaves = [(o.municipio_id, o.ano, o.mes) for o in linhas]
            if len(chaves) != len(set(chaves)):
                raise ValueError("Chaves duplicadas")
            observacoes.extend(linhas)
        return observacoes
    except (OSError, ValueError, pl.exceptions.PolarsError) as erro:
        raise PublicacaoInvalida("Observações publicadas inválidas") from erro


def pasta_publicada() -> Path:
    return config.carregar().publicado_dir


def manifesto_publicado(pasta: Path | None = None) -> dict[str, dict[str, object]]:
    """Manifesto de indicadores (RN-MOD-25), lido de dentro do pacote publicado (ADR-014)."""
    caminho = (pasta or pasta_publicada()) / MANIFESTO
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise PublicacaoInvalida("Pacote publicado sem o manifesto de indicadores") from erro
    except OSError as erro:  # permissão, pasta no lugar do arquivo etc.
        raise PublicacaoInvalida("Manifesto de indicadores ilegível") from erro
    except ValueError as erro:
        raise PublicacaoInvalida("Manifesto de indicadores inválido") from erro
    if not isinstance(bruto, dict) or not all(
        isinstance(d, dict) and all(isinstance(d.get(c), str) for c in CAMPOS_MANIFESTO)
        for d in bruto.values()
    ):
        raise PublicacaoInvalida("Manifesto de indicadores inválido")
    return bruto


def populacao_publicada(pasta: Path | None = None) -> list[Observacao]:
    caminho = (pasta or pasta_publicada()) / "populacao.json"
    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
        if not isinstance(bruto, list):
            raise PublicacaoInvalida("Publicação de população não é uma lista")
        linhas = [Observacao.model_validate(o) for o in bruto]
        if any(o.indicador != "populacao_estimada" or o.estado_validacao != "validado" for o in linhas):
            raise PublicacaoInvalida("Publicação de população contém indicador ou validação incompatível")
        chaves = [(o.municipio_id, o.ano, o.mes) for o in linhas]
        if len(chaves) != len(set(chaves)):
            raise PublicacaoInvalida("Publicação de população contém duplicatas")
        return linhas
    except FileNotFoundError:
        return []
    except OSError as erro:  # permissão, pasta no lugar do arquivo etc.
        raise PublicacaoInvalida("Publicação de população ilegível") from erro
    except (ValueError, ValidationError) as erro:
        raise PublicacaoInvalida("Publicação de população inválida") from erro
