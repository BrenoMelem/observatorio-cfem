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
