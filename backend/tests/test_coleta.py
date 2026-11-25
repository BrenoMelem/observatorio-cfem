"""RN-FON-13 e RN-VPU-03/06: a coleta registra a origem e nunca publica o que falhou."""

import json
from pathlib import Path

import pytest

from observatorio.coleta import executar


def test_origem_sem_arquivo_reprova_sem_baixar_e_sem_publicar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RN-FON-13: `--origem` só descreve um arquivo local; sem ele a coleta não inventa a proveniência."""
    monkeypatch.setenv("OBS_DATA_DIR", str(tmp_path / "dados"))
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path / "publicado"))

    resumo = executar(None, None, origem="https://github.com/exemplo/releases/download/anm-x/a.csv.gz")

    assert resumo["situacao"] == "reprovado"
    relatorio = json.loads(Path(str(resumo["relatorio"])).read_text(encoding="utf-8"))
    assert "--origem" in relatorio["erros"][0]
    assert not (tmp_path / "publicado").exists()


def test_falta_de_permissao_explica_a_causa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """RN-VPU-03/06: sem permissão de escrita, o relatório diz qual pasta e o que fazer, sem publicar."""
    monkeypatch.setenv("OBS_DATA_DIR", str(tmp_path / "dados"))
    monkeypatch.setenv("OBS_PUBLICADO_DIR", str(tmp_path / "publicado"))

    def sem_permissao(*_: object) -> None:
        raise PermissionError(13, "Permission denied", "/root/publicado/.publicando")

    monkeypatch.setattr("observatorio.coleta.converter", sem_permissao)

    resumo = executar(tmp_path / "arrecadacao.csv.gz", None)

    relatorio = json.loads(Path(str(resumo["relatorio"])).read_text(encoding="utf-8"))
    assert resumo["situacao"] == "reprovado"
    assert "/root/publicado/.publicando" in relatorio["erros"][0]
    assert "OBS_PUBLICADO_DIR" in relatorio["erros"][0]
