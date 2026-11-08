from scripts.cfem.checar_totais_regras import checar_totais


def test_detecta_divergencia_entre_regras_e_linha_total(tmp_path):
    (tmp_path / "tema.md").write_text("### RN-XXX-01\n- **Status:** DECIDIDA\n", encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text("Total: 1 regras, sendo 1 DECIDIDAS, 0 PROPOSTAS e 0 EM ABERTO.\n", encoding="utf-8")
    assert checar_totais(tmp_path)["confere"] is True
    readme.write_text("Total: 2 regras, sendo 2 DECIDIDAS, 0 PROPOSTAS e 0 EM ABERTO.\n", encoding="utf-8")
    assert checar_totais(tmp_path)["confere"] is False


def test_conta_regras_obsoletas(tmp_path):
    (tmp_path / "tema.md").write_text("- **Status:** DECIDIDA\n- **Status:** OBSOLETA\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "Total: 2 regras, sendo 1 DECIDIDAS, 0 PROPOSTAS, 0 EM ABERTO e 1 OBSOLETAS.\n", encoding="utf-8")
    assert checar_totais(tmp_path)["confere"] is True


def test_regras_reais_conferem_com_o_readme():
    assert checar_totais()["confere"] is True
