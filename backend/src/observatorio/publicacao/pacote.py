"""Publica somente lotes aprovados com ponteiro atômico (RN-VPU-01/03, ADR-014)."""

import hashlib
import io
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from observatorio.modelo.pacote import ArquivoIndicador, DescricaoPacote, calcular_versao
from observatorio.validacao.cfem import Resultado


def publicar(resultado: Resultado, pasta: Path, manifesto: Path, consumo: Path | None = None) -> str:
    """RN-VPU-03: monta tudo antes de trocar pacote.json; falha conserva a versão anterior."""
    if not resultado.aprovado or not resultado.observacoes or resultado.erros:
        raise ValueError("Lote reprovado ou vazio: publicação preservada")
    ultimo_ano = max(o.ano for o in resultado.observacoes)
    if any(
        o.indicador != "cfem_arrecadada" or (o.estado_validacao != "validado" and o.ano != ultimo_ano)
        for o in resultado.observacoes
    ):
        # RN-CFE-06: só o último ano, ainda aberto, pode ter meses provisórios.
        raise ValueError("A publicação CFEM exige observações validadas fora do ano aberto")
    pasta.mkdir(parents=True, exist_ok=True)
    trava = pasta / ".publicando"
    trava.open("x").close()
    try:
        return _montar(resultado, pasta, manifesto, consumo)
    finally:
        trava.unlink(missing_ok=True)


def _montar(resultado: Resultado, pasta: Path, manifesto: Path, consumo: Path | None) -> str:
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
        # Não remover uma chave homologada já publicada ao restringir a referência.
        if "cfem_arrecadada.parquet" in arquivos:
            antigas = pl.read_parquet(io.BytesIO(arquivos["cfem_arrecadada.parquet"])).filter(
                pl.col("estado_validacao") == "validado"
            )
            # Um mês provisório pode sair se a ANM o revisar; só o que já foi validado não pode sumir.
            chaves = {(o.municipio_id, o.ano, o.mes) for o in resultado.observacoes}
            if not set(antigas.select("municipio_id", "ano", "mes").iter_rows()) <= chaves:
                raise ValueError("Série homologada encolheu; publicação preservada (RN-VPU-02)")
    elif (pasta / "populacao.json").exists():
        arquivos["populacao.json"] = (pasta / "populacao.json").read_bytes()
    arquivos["indicadores.json"] = manifesto.read_bytes()
    definicoes = json.loads(arquivos["indicadores.json"])
    if not isinstance(definicoes, dict) or "cfem_arrecadada" not in definicoes:
        raise ValueError("Manifesto sem CFEM")
    if any(
        not isinstance(v, dict)
        or any(not isinstance(v.get(c), str) for c in ("fonte", "metodo", "limitacoes"))
        for v in definicoes.values()
    ):
        raise ValueError("Manifesto inválido")
    if consumo:
        arquivos["consumo_assistente.json"] = consumo.read_bytes()
    elif "consumo_assistente.json" not in arquivos:
        arquivos["consumo_assistente.json"] = json.dumps(
            {
                "cfem_arrecadada": {
                    "habilitado": True,
                    "motivo": "Somente recortes oficialmente reconciliados",
                }
            },
            ensure_ascii=False,
        ).encode()
    controle = json.loads(arquivos["consumo_assistente.json"])
    if not isinstance(controle, dict) or any(
        not isinstance(v, dict)
        or type(v.get("habilitado")) is not bool
        or not isinstance(v.get("motivo"), str)
        for v in controle.values()
    ):
        raise ValueError("Controle de consumo do assistente inválido")
    linhas = [o.model_dump() for o in resultado.observacoes]
    esquema = {nome: pl.String for nome in linhas[0]}
    tabela = pl.DataFrame(
        linhas, schema_overrides={**esquema, "ano": pl.Int64, "mes": pl.Int64, "valor": pl.Decimal(38, 2)}
    )
    buffer = io.BytesIO()
    tabela.write_parquet(buffer, compression="zstd")
    arquivos["cfem_arrecadada.parquet"] = buffer.getvalue()
    arquivos["qualidade-cfem.json"] = json.dumps(
        resultado.relatorio, ensure_ascii=False, sort_keys=True
    ).encode()
    hashes = {nome: hashlib.sha256(conteudo).hexdigest() for nome, conteudo in arquivos.items()}
    indicadores["cfem_arrecadada"] = ArquivoIndicador(
        arquivo="cfem_arrecadada.parquet",
        sha256=hashes["cfem_arrecadada.parquet"],
        ano_referencia=max(o.ano for o in resultado.observacoes),
        atualizado_em=max(o.atualizado_em or "" for o in resultado.observacoes),
    )
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
