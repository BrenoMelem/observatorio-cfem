"""CLI de coleta: fonte → validação → publicação (RN-VPU-01/03/06).

Uso: python -m observatorio.coleta cfem --arquivo CSV --referencias referencias.json
O arquivo pode ser o `.csv.gz` de uma Release `anm-*`; nesse caso, `--origem` registra a URL dele.
Sem referência independente, gera relatório de reprovação e preserva publicação.
"""

import argparse
import gzip
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from observatorio import config
from observatorio.fontes.cfem_arrecadacao import baixar, converter, hash_arquivo
from observatorio.modelo.pacote import DescricaoPacote
from observatorio.publicacao.pacote import publicar
from observatorio.validacao.cfem import Referencia, ReferenciaNacional, validar


def _hash_captura(pasta: Path, base: str) -> str | None:
    """SHA-256 da captura: do HTML original em `.html.gz` (corpo HTTP) ou do `.md` (extração antiga)."""
    comprimido = pasta / f"{base}.html.gz"
    if comprimido.is_file():
        try:
            return hashlib.sha256(gzip.decompress(comprimido.read_bytes())).hexdigest()
        except (OSError, EOFError) as erro:
            raise ValueError(f"Captura compactada ilegível: {comprimido.name}") from erro
    extracao = pasta / f"{base}.md"
    return hash_arquivo(extracao) if extracao.is_file() else None


def conferir_evidencias(
    referencias: list[Referencia], nacionais: list[ReferenciaNacional], pasta: Path
) -> None:
    """RN-VPU-07 e RN-CFE-12: confere a captura arquivada de cada referência antes de homologar."""
    esperados: dict[str, str] = {}
    for base, sha256 in [(f"anm-pa-{r.ano}", r.sha256) for r in referencias] + [
        (f"anm-brasil-{r.ano}", r.sha256) for r in nacionais
    ]:
        if base in esperados and esperados[base] != sha256:
            raise ValueError(f"SHA-256 conflitante para {base}")
        esperados[base] = sha256
    for base, esperado in esperados.items():
        if _hash_captura(pasta, base) != esperado:
            raise ValueError(f"Captura ausente ou SHA-256 divergente: {base}")


def executar(
    arquivo: Path | None,
    referencias: Path | None,
    consumo: Path | None = None,
    referencias_nacionais: Path | None = None,
    evidencias: Path | None = None,
    origem: str | None = None,
) -> dict[str, object]:
    """RN-VPU-06: relatório e pendência local em toda execução, inclusive falha de layout."""
    configuracao = config.carregar()
    qualidade = configuracao.dados_dir / "qualidade"
    qualidade.mkdir(parents=True, exist_ok=True)
    execucao = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    relatorio: dict[str, object] = {"execucao": execucao, "situacao": "reprovado"}
    try:
        if origem is not None and arquivo is None:
            raise ValueError(
                "--origem descreve um --arquivo local; sem --arquivo a origem é a ANM (RN-FON-13)"
            )
        entrada = arquivo or baixar(configuracao.dados_dir / "bruto" / "cfem", configuracao.certificado_anm)
        pasta_bruta = configuracao.dados_dir / "bruto" / "cfem"
        lote = converter(entrada, pasta_bruta, origem) if origem else converter(entrada, pasta_bruta)
        refs = (
            []
            if referencias is None
            else [Referencia.model_validate(r) for r in json.loads(referencias.read_text(encoding="utf-8"))]
        )
        if refs and referencias_nacionais is None:
            raise ValueError(
                "Referências nacionais obrigatórias para lote com referências municipais (RN-CFE-12)"
            )
        refs_nacionais = (
            []
            if referencias_nacionais is None
            else [
                ReferenciaNacional.model_validate(r)
                for r in json.loads(referencias_nacionais.read_text(encoding="utf-8"))
            ]
        )
        if refs and evidencias is None:
            raise ValueError("Pasta de capturas obrigatória para referências municipais (RN-VPU-07)")
        if evidencias is not None:
            conferir_evidencias(refs, refs_nacionais, evidencias)
        anterior = None
        ponteiro = configuracao.publicado_dir / "pacote.json"
        if ponteiro.exists():
            pacote = DescricaoPacote.model_validate_json(ponteiro.read_bytes())
            caminho = configuracao.publicado_dir / "versoes" / pacote.versao / "qualidade-cfem.json"
            if caminho.exists():
                anterior = json.loads(caminho.read_bytes())
        resultado = validar(lote, refs, anterior, refs_nacionais)
        relatorio.update(resultado.relatorio)
        if resultado.aprovado:
            versao = publicar(resultado, configuracao.publicado_dir, configuracao.manifesto, consumo)
            relatorio["versao_pacote"] = versao
        else:
            relatorio["pendencia"] = "Revisar erros; publicação anterior preservada (RN-VPU-03)"
    except PermissionError as erro:
        relatorio.update(
            situacao="reprovado",
            erros=[
                (
                    f"Sem permissão de escrita em {erro.filename}. A pasta pode pertencer a outro usuário, por "
                    "exemplo o root, se o Docker a criou ao montá-la; devolva-a ao seu usuário ou aponte "
                    "OBS_PUBLICADO_DIR e OBS_DATA_DIR para outra pasta (docs/guias/pipeline-cfem.md)."
                )
            ],
            pendencia="Coleta falhou; publicação anterior preservada (RN-VPU-03)",
        )
    except (OSError, ValueError) as erro:
        relatorio.update(
            situacao="reprovado",
            erros=[str(erro)],
            pendencia="Coleta falhou; publicação anterior preservada (RN-VPU-03)",
        )
    finally:
        caminho_relatorio = qualidade / f"cfem-{execucao}.json"
        caminho_relatorio.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "situacao": relatorio["situacao"],
        "relatorio": str(caminho_relatorio),
        "linhas": relatorio.get("linhas_lidas"),
        "duplicatas": relatorio.get("duplicatas"),
        "versao_pacote": relatorio.get("versao_pacote"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonte", choices=["cfem"])
    parser.add_argument("--arquivo", type=Path, help="CSV ou .csv.gz local; omitido: GET na ANM")
    parser.add_argument(
        "--origem", help="De onde veio o --arquivo, por exemplo a URL do arquivo na Release anm-* (RN-FON-13)"
    )
    parser.add_argument("--referencias", type=Path, help="Valores de publicação oficial independente")
    parser.add_argument(
        "--referencias-nacionais", type=Path, help="Totais nacionais oficiais por ano fechado"
    )
    parser.add_argument("--evidencias", type=Path, help="Capturas Markdown da ANM com SHA-256 declarado")
    parser.add_argument("--consumo-assistente", type=Path, help="Controle a incorporar na nova versão")
    args = parser.parse_args()
    resumo = executar(
        args.arquivo,
        args.referencias,
        args.consumo_assistente,
        args.referencias_nacionais,
        args.evidencias,
        args.origem,
    )
    print(json.dumps(resumo, ensure_ascii=False))
    return 0 if resumo["situacao"] == "aprovado" else 1


if __name__ == "__main__":
    sys.exit(main())
