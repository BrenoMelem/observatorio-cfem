"""Fonte ANM: arquiva bruto e produz observações provisórias (RN-CFE-01/04/11).

Não homologa nem publica. A conversão latin-1 → UTF-8 antecede o Polars;
layout e conversões inválidas falham explicitamente (RN-VPU-04).
"""

import csv
import gzip
import hashlib
import json
import shutil
import ssl
import tempfile
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import polars as pl

from observatorio.modelo.lote import Lote
from observatorio.modelo.observacao import Observacao
from observatorio.modelo.territorios import MUNICIPIOS

URL = "https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv"
CABECALHO = (
    "Ano",
    "Mês",
    "Processo",
    "AnoDoProcesso",
    "Tipo_PF_PJ",
    "CPF_CNPJ",
    "Substância",
    "UF",
    "CodigoMunicipio",
    "Município",
    "QuantidadeComercializada",
    "UnidadeDeMedida",
    "ValorRecolhido",
    "DataCriacao",
)


def hash_arquivo(arquivo: Path) -> str:
    with arquivo.open("rb") as entrada:
        return hashlib.file_digest(entrada, "sha256").hexdigest()


def baixar(pasta: Path, certificado: Path | None = None) -> Path:
    """GET com User-Agent e TLS verificado; bruto preservado (RN-FON-13, RN-TMP-18)."""
    pasta.mkdir(parents=True, exist_ok=True)
    contexto = ssl.create_default_context()
    if certificado:
        contexto.load_verify_locations(cafile=str(certificado))
    requisicao = Request(URL, headers={"User-Agent": "Mozilla/5.0 ObservatorioCFEM/1.0"})
    try:
        with urlopen(requisicao, timeout=120, context=contexto) as resposta:
            with tempfile.NamedTemporaryFile(dir=pasta, suffix=".download", delete=False) as saida:
                temporario = Path(saida.name)
                shutil.copyfileobj(resposta, saida)
            destino = pasta / (hash_arquivo(temporario) + ".csv")
            if destino.exists():
                temporario.unlink()
            else:
                temporario.rename(destino)
            meta = {
                "url": URL,
                "sha256": hash_arquivo(destino),
                "coletado_em": datetime.now(UTC).isoformat(),
                "last_modified": resposta.headers.get("Last-Modified"),
                "etag": resposta.headers.get("ETag"),
            }
            (pasta / (destino.stem + "-origem.json")).write_text(json.dumps(meta), encoding="utf-8")
            return destino
    except HTTPError as erro:
        raise ValueError(f"ANM respondeu HTTP {erro.code}; coleta não publicada") from erro


def descompactar(arquivo: Path, pasta: Path) -> Path:
    """RN-FON-13: o `.csv.gz` das Releases `anm-*` vira o CSV original, para o hash ser o da edição da ANM."""
    pasta.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=pasta, suffix=".download", delete=False) as saida:
        temporario = Path(saida.name)
        try:
            with gzip.open(arquivo, "rb") as entrada:
                shutil.copyfileobj(entrada, saida)
        except (OSError, EOFError) as erro:
            saida.close()
            temporario.unlink(missing_ok=True)
            raise ValueError("ANM: arquivo compactado ilegível") from erro
    return temporario


def converter(arquivo: Path, pasta_bruta: Path, origem: str = URL) -> Lote:
    """RN-CFE-11, RN-VPU-04/11: soma decimal sem deduplicar; só arredonda o grupo.

    RN-FON-13: `origem` é de onde os bytes vieram (a ANM ou a Release que arquivou a edição); aceita o
    CSV ou o `.csv.gz` da Release.
    """
    pasta_bruta.mkdir(parents=True, exist_ok=True)
    if arquivo.suffix == ".gz":
        descompactado = descompactar(arquivo, pasta_bruta)
        try:
            return converter(descompactado, pasta_bruta, origem)
        finally:
            descompactado.unlink(missing_ok=True)
    sha256 = hash_arquivo(arquivo)
    bruto = pasta_bruta / f"{sha256}.csv"
    if not bruto.exists():
        shutil.copyfile(arquivo, bruto)
    elif hash_arquivo(bruto) != sha256:
        raise ValueError("Arquivo bruto arquivado foi alterado")
    convertido = pasta_bruta / f"{sha256}.utf8.csv"
    # csv.reader confere também linhas curtas: Polars poderia completá-las com nulos.
    with (
        bruto.open(encoding="latin-1", newline="") as entrada,
        convertido.open("w", encoding="utf-8", newline="") as saida,
    ):
        leitor = csv.reader(entrada, strict=True)
        escritor = csv.writer(saida)
        if tuple(next(leitor, [])) != CABECALHO:
            raise ValueError("ANM: colunas alteradas ou arquivo vazio")
        escritor.writerow(CABECALHO)
        for numero, linha in enumerate(leitor, 2):
            if len(linha) != len(CABECALHO):
                raise ValueError(f"ANM: quantidade de colunas inválida na linha {numero}")
            escritor.writerow(linha)
    try:
        tabela = pl.scan_csv(convertido, schema={c: pl.String for c in CABECALHO})
        incorretas = (
            tabela.filter(
                pl.col("Ano").is_null()
                | pl.col("Mês").is_null()
                | ~pl.col("Ano").str.contains(r"^\d{4}$")
                | ~pl.col("Mês").str.contains(r"^(0?[1-9]|1[0-2])$")
                | pl.col("ValorRecolhido").is_null()
                | ~pl.col("ValorRecolhido").str.contains(r"^-?\d+(?:\.\d{3})*(?:,\d{1,4})?$")
            )
            .select(pl.len())
            .collect()
            .item()
        )
        if incorretas:
            raise ValueError("ANM: ano, mês ou valor inválido/nulo")
        tabela = tabela.with_columns(
            pl.col("Ano").cast(pl.Int64),
            pl.col("Mês").cast(pl.Int64),
            pl.col("ValorRecolhido")
            .str.replace_all(".", "", literal=True)
            .str.replace(",", ".", literal=True)
            .cast(pl.Decimal(38, 4))
            .alias("dinheiro"),
        )
        nacional = (
            tabela.group_by("Ano", "Mês")
            .agg(pl.len().alias("registros"), pl.col("dinheiro").sum().alias("total"))
            .collect()
        )
        recorte = tabela.filter(
            pl.col("CodigoMunicipio").is_in(list(MUNICIPIOS)) & (pl.col("Ano") >= 2003)
        ).collect()
        if recorte.filter(pl.col("UF") != "PA").height:
            raise ValueError("Código municipal da RI com UF incompatível")
        duplicatas = recorte.height - recorte.unique(subset=list(CABECALHO)).height
        mensal = (
            recorte.group_by("CodigoMunicipio", "Ano", "Mês")
            .agg(pl.col("dinheiro").sum().alias("valor"))
            .sort("CodigoMunicipio", "Ano", "Mês")
        )
        agora = datetime.now(UTC).isoformat()
        observacoes: list[Observacao] = []
        for codigo, ano, mes, soma in mensal.iter_rows():
            if not isinstance(soma, Decimal) or not isinstance(codigo, str):
                raise TypeError("Tipo monetário/municipal inesperado no Polars")
            valor = soma.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
            observacoes.append(
                Observacao(
                    indicador="cfem_arrecadada",
                    municipio_id=codigo,
                    municipio_nome=MUNICIPIOS[codigo],
                    nivel_territorial="município",
                    ano=int(ano),
                    mes=int(mes),
                    valor=valor,
                    unidade="BRL nominal",
                    natureza_valor="zero real" if valor == 0 else "informado",
                    estado_validacao="provisório",
                    fonte="ANM, CFEM_Arrecadacao.csv",
                    edicao_fonte=sha256,
                    atualizado_em=agora,
                    versao_tratamento="1.0.0",
                )
            )
        totais: dict[str, Decimal] = {}
        registros_mensais: dict[str, int] = {}
        for ano, mes, quantidade, total in nacional.iter_rows():
            if not isinstance(total, Decimal):
                raise TypeError("Total nacional sem tipo decimal")
            totais[str(ano)] = totais.get(str(ano), Decimal(0)) + total
            registros_mensais[f"{ano}:{mes}"] = int(quantidade)
        registros_municipais = {
            f"{codigo}:{ano}": int(quantidade)
            for codigo, ano, quantidade in recorte.group_by("CodigoMunicipio", "Ano").len().iter_rows()
        }
        return Lote(
            tuple(observacoes),
            bruto,
            sha256,
            agora,
            origem,
            sum(registros_mensais.values()),
            recorte.height,
            duplicatas,
            registros_municipais,
            registros_mensais,
            {a: str(v.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)) for a, v in totais.items()},
            {"municipios": list(MUNICIPIOS), "ano_inicio": 2003, "UF": "PA"},
        )
    except pl.exceptions.PolarsError as erro:
        raise ValueError("ANM: falha explícita de leitura/conversão tabular") from erro
