"""CLI de coleta: fonte → validação → publicação (RN-VPU-01/03/06).

Uso: python -m observatorio.coleta cfem --arquivo CSV --referencias referencias.json
O arquivo pode ser o `.csv.gz` de uma Release `anm-*`; nesse caso, `--origem` registra a URL dele.
Sem referência independente, gera relatório de reprovação e preserva publicação.
"""

import argparse
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


def conferir_evidencias(
    referencias: list[Referencia], nacionais: list[ReferenciaNacional], pasta: Path
) -> None:
    """RN-VPU-07 e RN-CFE-12: confere a extração arquivada antes de homologar."""
    esperados: dict[str, str] = {}
    for referencia in referencias:
        nome = f"anm-pa-{referencia.ano}.md"
        if nome in esperados and esperados[nome] != referencia.sha256:
            raise ValueError(f"SHA-256 conflitante para {nome}")
        esperados[nome] = referencia.sha256
    for referencia_nacional in nacionais:
        nome = f"anm-brasil-{referencia_nacional.ano}.md"
        if nome in esperados and esperados[nome] != referencia_nacional.sha256:
            raise ValueError(f"SHA-256 conflitante para {nome}")
        esperados[nome] = referencia_nacional.sha256
    for nome, esperado in esperados.items():
        arquivo = pasta / nome
        if not arquivo.is_file() or hash_arquivo(arquivo) != esperado:
            raise ValueError(f"Captura ausente ou SHA-256 divergente: {nome}")


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
