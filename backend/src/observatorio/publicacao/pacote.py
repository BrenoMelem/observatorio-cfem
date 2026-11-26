"""Publica somente lotes aprovados com ponteiro atômico (RN-VPU-01/03, ADR-014)."""

import hashlib
import io
import json
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from observatorio.modelo.lote import Resultado
from observatorio.modelo.pacote import ArquivoIndicador, DescricaoPacote, calcular_versao


def publicar(
    resultado: Resultado,
    pasta: Path,
    manifesto: Path,
    consumo: Path | None = None,
    *,
    qualidade: str = "qualidade-cfem.json",
    retificados: frozenset[tuple[str, int]] = frozenset(),
    indicadores_da_fonte: frozenset[str] = frozenset(),
) -> str:
    """RN-VPU-03: monta tudo antes de trocar pacote.json; falha conserva a versão anterior.

    Cada indicador do resultado vira o seu parquet; os indicadores de outras fontes do pacote anterior são
    mantidos. `indicadores_da_fonte` são os que a fonte substitui por inteiro: um deles sem observação no
    resultado conta como série vazia. `retificados` são os pares (município, ano) cuja entrega mudou na
    fonte (RN-TMP-04): neles uma linha já publicada pode sair; fora deles, a série homologada não pode
    encolher (RN-VPU-02).
    """
    if not resultado.aprovado or not resultado.observacoes or resultado.erros:
        raise ValueError("Lote reprovado ou vazio: publicação preservada")
    for indicador in {o.indicador for o in resultado.observacoes}:
        linhas = [o for o in resultado.observacoes if o.indicador == indicador]
        ultimo_ano = max(o.ano for o in linhas)
        if any(o.estado_validacao != "validado" and o.ano != ultimo_ano for o in linhas):
            # RN-CFE-06: só o último ano, ainda aberto, pode ter observações provisórias.
            raise ValueError(
                f"{indicador}: observações provisórias fora do último ano (ano aberto, RN-CFE-06)"
            )
    if not re.fullmatch(r"qualidade-[a-z]+\.json", qualidade):
        raise ValueError("Nome do relatório de qualidade inválido")
    pasta.mkdir(parents=True, exist_ok=True)
    trava = pasta / ".publicando"
    trava.open("x").close()
    try:
        substituidos = indicadores_da_fonte | {o.indicador for o in resultado.observacoes}
        return _montar(resultado, pasta, manifesto, consumo, qualidade, retificados, substituidos)
    finally:
        trava.unlink(missing_ok=True)


def _chaves(tabela: pl.DataFrame) -> set[tuple[object, ...]]:
    """Chave de cada linha publicada: município, ano, mês e categoria (nula nos pacotes sem categoria)."""
    if "categoria" not in tabela.columns:
        tabela = tabela.with_columns(pl.lit(None, dtype=pl.String).alias("categoria"))
    return set(tabela.select("municipio_id", "ano", "mes", "categoria").iter_rows())


def _montar(
    resultado: Resultado,
    pasta: Path,
    manifesto: Path,
    consumo: Path | None,
    qualidade: str,
    retificados: frozenset[tuple[str, int]],
    substituidos: frozenset[str],
) -> str:
    arquivos: dict[str, bytes] = {}
    indicadores: dict[str, ArquivoIndicador] = {}
    ponteiro = pasta / "pacote.json"
    if ponteiro.exists():
        anterior = DescricaoPacote.model_validate_json(ponteiro.read_bytes())
        indicadores.update(anterior.indicadores)
        for nome, resumo in anterior.arquivos.items():
            conteudo = (pasta / "versoes" / anterior.versao / nome).read_bytes()
            if hashlib.sha256(conteudo).hexdigest() != resumo:
                raise ValueError("Pacote anterior corrompido; publicação interrompida")
            arquivos[nome] = conteudo
        # Não remover uma chave homologada já publicada ao restringir a referência (RN-VPU-02).
        for indicador in sorted(substituidos):
            if f"{indicador}.parquet" not in arquivos:
                continue
            antigas = pl.read_parquet(io.BytesIO(arquivos[f"{indicador}.parquet"])).filter(
                pl.col("estado_validacao") == "validado"
            )
            # Um mês provisório pode sair se a fonte o revisar; só o que já foi validado não pode sumir,
            # salvo no município e ano cuja entrega foi retificada (RN-TMP-04).
            novas = {
                (o.municipio_id, o.ano, o.mes, o.categoria)
                for o in resultado.observacoes
                if o.indicador == indicador
            }
            sumidas = {c for c in _chaves(antigas) if c not in novas and (c[0], c[1]) not in retificados}
            if sumidas:
                raise ValueError(
                    f"Série homologada de {indicador} encolheu; publicação preservada (RN-VPU-02)"
                )
            if not novas:  # todas as linhas saíram por retificação: o indicador deixa o pacote
                del arquivos[f"{indicador}.parquet"]
                indicadores.pop(indicador, None)
    elif (pasta / "populacao.json").exists():
        arquivos["populacao.json"] = (pasta / "populacao.json").read_bytes()
    arquivos["indicadores.json"] = manifesto.read_bytes()
    definicoes = json.loads(arquivos["indicadores.json"])
    publicados = sorted({o.indicador for o in resultado.observacoes})
    if not isinstance(definicoes, dict) or any(i not in definicoes for i in publicados):
        raise ValueError("Manifesto sem algum indicador publicado (RN-MOD-25)")
    if any(
        not isinstance(v, dict)
        or any(not isinstance(v.get(c), str) for c in ("fonte", "metodo", "limitacoes"))
        for v in definicoes.values()
    ):
        raise ValueError("Manifesto inválido")
    if consumo:
        arquivos["consumo_assistente.json"] = consumo.read_bytes()
    controle = json.loads(arquivos.get("consumo_assistente.json", b"{}"))
    if isinstance(controle, dict) and any(i not in controle for i in publicados):
        for indicador in publicados:
            controle.setdefault(
                indicador, {"habilitado": True, "motivo": "Somente recortes oficialmente reconciliados"}
            )
        arquivos["consumo_assistente.json"] = json.dumps(controle, ensure_ascii=False).encode()
    if not isinstance(controle, dict) or any(
        not isinstance(v, dict)
        or type(v.get("habilitado")) is not bool
        or not isinstance(v.get("motivo"), str)
        for v in controle.values()
    ):
        raise ValueError("Controle de consumo do assistente inválido")
    for indicador in publicados:
        linhas = [o.model_dump() for o in resultado.observacoes if o.indicador == indicador]
        esquema = {nome: pl.String for nome in linhas[0]}
        tabela = pl.DataFrame(
            linhas,
            schema_overrides={**esquema, "ano": pl.Int64, "mes": pl.Int64, "valor": pl.Decimal(38, 2)},
        )
        buffer = io.BytesIO()
        tabela.write_parquet(buffer, compression="zstd")
        arquivos[f"{indicador}.parquet"] = buffer.getvalue()
    arquivos[qualidade] = json.dumps(resultado.relatorio, ensure_ascii=False, sort_keys=True).encode()
    hashes = {nome: hashlib.sha256(conteudo).hexdigest() for nome, conteudo in arquivos.items()}
    for indicador in publicados:
        linhas_indicador = [o for o in resultado.observacoes if o.indicador == indicador]
        indicadores[indicador] = ArquivoIndicador(
            arquivo=f"{indicador}.parquet",
            sha256=hashes[f"{indicador}.parquet"],
            ano_referencia=max(o.ano for o in linhas_indicador),
            atualizado_em=max(o.atualizado_em or "" for o in linhas_indicador),
        )
    return gravar_versao(pasta, arquivos, hashes, indicadores)


def gravar_versao(
    pasta: Path,
    arquivos: dict[str, bytes],
    hashes: dict[str, str],
    indicadores: dict[str, ArquivoIndicador],
) -> str:
    """RN-VPU-03: grava a versão imutável e só então troca o ponteiro, de forma atômica."""
    ponteiro = pasta / "pacote.json"
    versao = calcular_versao(hashes, indicadores)
    descricao = DescricaoPacote(
        versao=versao, gerado_em=datetime.now(UTC).isoformat(), arquivos=hashes, indicadores=indicadores
    )
    versoes = pasta / "versoes"
    versoes.mkdir(exist_ok=True)
    destino = versoes / versao
    # A versão só fica visível após a troca do ponteiro. Evita renomear diretórios
    # abertos por indexadores/OneDrive no Windows; arquivos existentes não mudam.
    destino.mkdir(exist_ok=True)
    for nome, conteudo in arquivos.items():
        caminho = destino / nome
        if caminho.exists():
            if caminho.read_bytes() != conteudo:
                raise ValueError("Versão imutável alterada")
        else:
            with caminho.open("xb") as saida_arquivo:
                saida_arquivo.write(conteudo)
    with tempfile.NamedTemporaryFile(dir=pasta, suffix=".json.tmp", delete=False) as saida:
        temporario = Path(saida.name)
        saida.write(descricao.model_dump_json(indent=2).encode())
    try:
        temporario.replace(ponteiro)
    finally:
        temporario.unlink(missing_ok=True)
    return versao
