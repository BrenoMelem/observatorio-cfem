"""Monta o pacote publicado a partir dos pacotes parciais aprovados de cada fonte (RN-VPU-01/03, ADR-011).

Cada fonte publica o seu pacote parcial (só os indicadores dela) depois de aprovada na validação; esta
montagem junta o último parcial de cada fonte, confere os hashes e troca o ponteiro por último. Uma fonte
não conhece as outras, e nenhuma coleta parte do pacote de outra.
"""

import hashlib
import json
import re
from pathlib import Path

from observatorio.modelo.pacote import ArquivoIndicador, DescricaoPacote
from observatorio.publicacao.pacote import gravar_versao

_RELATORIO = re.compile(r"qualidade-[a-z]+\.json")


def _ler_parcial(pasta: Path) -> tuple[DescricaoPacote, dict[str, bytes]]:
    """RN-VPU-01: lê um pacote parcial e confere o hash de cada arquivo antes de usá-lo."""
    ponteiro = pasta / "pacote.json"
    if not ponteiro.is_file():
        raise ValueError(f"Pacote parcial sem pacote.json: {pasta}")
    descricao = DescricaoPacote.model_validate_json(ponteiro.read_bytes())
    arquivos: dict[str, bytes] = {}
    for nome, resumo in descricao.arquivos.items():
        conteudo = (pasta / "versoes" / descricao.versao / nome).read_bytes()
        if hashlib.sha256(conteudo).hexdigest() != resumo:
            raise ValueError(f"Pacote parcial corrompido: {pasta} ({nome})")
        arquivos[nome] = conteudo
    return descricao, arquivos


def montar(parciais: list[Path], pasta: Path, manifesto: Path) -> str:
    """RN-VPU-03: junta os parciais num pacote novo; erro em qualquer um conserva o pacote anterior."""
    if not parciais:
        raise ValueError("Nenhum pacote parcial para montar")
    arquivos: dict[str, bytes] = {}
    indicadores: dict[str, ArquivoIndicador] = {}
    controle: dict[str, object] = {}
    for parcial in parciais:
        descricao, conteudos = _ler_parcial(parcial)
        for indicador, item in descricao.indicadores.items():
            if indicador in indicadores:
                raise ValueError(f"Indicador {indicador} em mais de um pacote parcial")
            indicadores[indicador] = item
            arquivos[item.arquivo] = conteudos[item.arquivo]
        for nome, conteudo in conteudos.items():
            if _RELATORIO.fullmatch(nome) or nome == "populacao.json":
                if nome in arquivos and arquivos[nome] != conteudo:
                    raise ValueError(f"Arquivo {nome} diferente em dois pacotes parciais")
                arquivos[nome] = conteudo
        lido = json.loads(conteudos["consumo_assistente.json"])
        if not isinstance(lido, dict):
            raise TypeError("Controle de consumo do assistente inválido")
        controle.update(lido)
    definicoes = json.loads(manifesto.read_bytes())
    if not isinstance(definicoes, dict) or any(i not in definicoes for i in indicadores):
        raise ValueError("Manifesto sem algum indicador publicado (RN-MOD-25)")
    arquivos["indicadores.json"] = manifesto.read_bytes()
    arquivos["consumo_assistente.json"] = json.dumps(controle, ensure_ascii=False).encode()
    hashes = {nome: hashlib.sha256(conteudo).hexdigest() for nome, conteudo in arquivos.items()}
    indicadores = {
        k: item.model_copy(update={"sha256": hashes[item.arquivo]}) for k, item in indicadores.items()
    }
    pasta.mkdir(parents=True, exist_ok=True)
    trava = pasta / ".publicando"
    trava.open("x").close()
    try:
        return gravar_versao(pasta, arquivos, hashes, indicadores)
    finally:
        trava.unlink(missing_ok=True)
