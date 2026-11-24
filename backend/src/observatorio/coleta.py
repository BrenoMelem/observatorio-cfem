"""CLI de coleta: fonte → validação → publicação (RN-VPU-01/03/06).

Uso: python -m observatorio.coleta cfem --arquivo CSV --referencias referencias.json
Sem referência independente, gera relatório de reprovação e preserva publicação.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from observatorio import config
from observatorio.fontes.cfem_arrecadacao import baixar, converter
from observatorio.modelo.pacote import DescricaoPacote
from observatorio.publicacao.pacote import publicar
from observatorio.validacao.cfem import Referencia, validar


def executar(
    arquivo: Path | None, referencias: Path | None, consumo: Path | None = None
) -> dict[str, object]:
    """RN-VPU-06: relatório e pendência local em toda execução, inclusive falha de layout."""
    configuracao = config.carregar()
    qualidade = configuracao.dados_dir / "qualidade"
    qualidade.mkdir(parents=True, exist_ok=True)
    execucao = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    relatorio: dict[str, object] = {"execucao": execucao, "situacao": "reprovado"}
    try:
        origem = arquivo or baixar(configuracao.dados_dir / "bruto" / "cfem", configuracao.certificado_anm)
        lote = converter(origem, configuracao.dados_dir / "bruto" / "cfem")
        refs = (
            []
            if referencias is None
            else [Referencia.model_validate(r) for r in json.loads(referencias.read_text(encoding="utf-8"))]
        )
        anterior = None
        ponteiro = configuracao.publicado_dir / "pacote.json"
        if ponteiro.exists():
            pacote = DescricaoPacote.model_validate_json(ponteiro.read_bytes())
            caminho = configuracao.publicado_dir / "versoes" / pacote.versao / "qualidade-cfem.json"
            if caminho.exists():
                anterior = json.loads(caminho.read_bytes())
        resultado = validar(lote, refs, anterior)
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
    parser.add_argument("--arquivo", type=Path, help="CSV real local; omitido: GET na ANM")
    parser.add_argument("--referencias", type=Path, help="Valores de publicação oficial independente")
    parser.add_argument("--consumo-assistente", type=Path, help="Controle a incorporar na nova versão")
    args = parser.parse_args()
    resumo = executar(args.arquivo, args.referencias, args.consumo_assistente)
    print(json.dumps(resumo, ensure_ascii=False))
    return 0 if resumo["situacao"] == "aprovado" else 1


if __name__ == "__main__":
    sys.exit(main())
