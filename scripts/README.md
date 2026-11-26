# Scripts

O código do laboratório mora aqui, em Python, gerenciado com [uv](https://docs.astral.sh/uv/). **São scripts de teste e laboratório**: não são a implementação do sistema, que fica em `backend/` (ver `AGENTS.md`). A saída vai para `output/` e `tmp/`, que não são versionados.

## Preparar o ambiente

```bash
uv sync                      # cria .venv com as dependências do pyproject.toml
uv run pytest                # roda os testes (scripts/testes)
uv run ruff check scripts    # lint
```

Os scripts rodam como módulo, a partir da raiz do repositório: `uv run python -m scripts.<pasta>.<script> --help`.

## Mapa

| Pasta | Script | O que faz |
| --- | --- | --- |
| `cfem/` | `preparar.py`, `meses_por_municipio.py` (meses com linha por município, RN-CFE-23) | Lê `CFEM_Arrecadacao.csv` da ANM e gera a CFEM arrecadada mensal e anual provisória (RN-CFE-04 a 07, RN-CFE-11) |
| | `analisar_duplicatas.py` | Relatório das linhas duplicadas da arrecadação, sem identificadores pessoais (RN-VPU-11) |
| | `validar_arquivo_anm.py` | Confere a cobertura municipal de um CSV da ANM (arrecadação, distribuição ou autuação) |
| | `distribuicao_municipal.py` | Agrega a distribuição da ANM por município, ano, mês e modalidade (RN-CFE-11) |
| | `reconciliar_distribuicao.py` | Reconcilia a distribuição da ANM com a notícia mensal da ANM (RN-VPU-07) |
| | `arquivar_anm.py`, `arquivar_documentos.py`, `comparar_versoes_anm.py`, `anm_arquivos.py` (módulo comum dos três arquivos) | Arquivo das versões da ANM em Releases, com manifesto e relatório de diferenças (RN-TMP-18; ver `docs/guias/arquivo-anm.md`) |
| | `referencias_anm.py` | Captura as tabelas oficiais da ANM; gerou a primeira versão das referências da validação em 25/11/2026 (RN-VPU-07, RN-CFE-12). O produto usa `observatorio.referencias` |
| | `checar_totais_regras.py` | Confere os totais de status das regras contra o `README.md` de `docs/regras-de-negocio/` |
| `populacao/` | `atualizar.py` | População estimada do IBGE (SIDRA 6579/9324), com validação e reconciliação |
| `financas/` | `dca_lote.py`, `conferir_fonte_cfem.py` (fonte 1708 × DCA × ANM, RN-CFE-24), `codigos_dca.py` (códigos da DCA por ano, RN-ENT-12) | DCA Anexo I-E do SICONFI em lote validado, sem homologar |
| | `dca_csv.py` | DCA Anexo I-E em CSV simples por função |
| | `dca_anexos.py` | DCA Anexos I-C (receitas, cota-parte do ICMS) e I-D (despesas, investimento) em CSV longo, 12 municípios, 2013 a 2025 (RN-ENT-12) |
| | `msc_despesa_fonte.py` | MSC orçamentária por fonte de recursos (`1708`) |
| `commodities/` | `pink_sheet.py`, `fred.py` | Preço de ferro e cobre: Pink Sheet do World Bank (fonte principal, sem chave), com o ferro em duas séries, contrato anual 1985–2005 e spot mensal desde dez/2008 (RN-TMP-13 e 14, corrigido em 21/11/2026); FRED (reserva da spot e do cobre, exige `FRED_API_KEY` no ambiente) |
| `emissoes/` | `seeg.py` | Emissões do SEEG: lê a planilha municipal (centenas de MB, fora do Git) e extrai o recorte dos 12 municípios com os metadados |
| `sondas/` | `ibge_sidra.py`, `ipeadata.py`, `inspecionar_ipeadata.py`, `worldbank_commodities.py`, `tcmpa.py` (conflito B4), `ibge_bairros.py` (conflito B5), `basedosdados_colunas.py` (colunas do catálogo da Base dos Dados, RN-MOD-16), `pib_per_capita_ri.py` (razão regional, RN-MOD-18), `siconfi_entregas.py` (status das entregas da DCA, RN-TMP-04), `siconfi_rreo_dca.py` e `siconfi_msc_dca_paga.py` (conferência da despesa por função com o RREO e a MSC, RN-FNT-04) | Provas de que a fonte responde e como (laboratório) |
| `servidor/` | `servidor.py` | API local do protótipo; lê só a camada publicada (`docs/api/openapi.yaml`) |
| `notebook/` | `construir_notebook.py` | Gera o notebook de laboratório (`laboratorio_fontes_observatorio_cfem.ipynb`) |
| `comum/` | `municipios.py`, `arquivos.py` | Os 12 municípios, os campos do esquema comum e utilitários de arquivo |
| `testes/` | `test_*.py` | Testes (pytest) |

Variáveis de ambiente: `OBS_DATA_DIR` (padrão `output/observatorio`), `PORT` do servidor (padrão 3000) e `FRED_API_KEY`. Chaves nunca entram no repositório.

## Nomes antigos

Os documentos de fonte (`docs/regras-de-negocio/fontes/`) e as regras citam os scripts pelos nomes de antes de 08/11/2026. A equivalência:

| Antes | Agora |
| --- | --- |
| `scripts/validate_anm_cfem.py` | `scripts/cfem/validar_arquivo_anm.py` |
| `scripts/build_cfem_distribution_municipal.py` | `scripts/cfem/distribuicao_municipal.py` |
| `scripts/reconcile_anm_distribution.py` | `scripts/cfem/reconciliar_distribuicao.py` |
| `scripts/coletar_despesa_siconfi.py` | `scripts/financas/dca_csv.py` |
| `scripts/coletar_msc_despesa_fonte.py` | `scripts/financas/msc_despesa_fonte.py` |
| `scripts/probe_ibge_sidra.ps1` | `scripts/sondas/ibge_sidra.py` |
| `scripts/probe_ipeadata.py` | `scripts/sondas/ipeadata.py` |
| `scripts/inspect_ipeadata_response.py` | `scripts/sondas/inspecionar_ipeadata.py` |
| `scripts/probe_worldbank_commodities.py` | `scripts/sondas/worldbank_commodities.py` |
| `scripts/build_notebook_cfem.py` | `scripts/notebook/construir_notebook.py` |
| `notebooks/laboratorio_fontes_observatorio_cfem.ipynb` | `scripts/notebook/laboratorio_fontes_observatorio_cfem.ipynb` |
| `scripts/preparar-cfem.mjs` + `src/cfem.mjs` | `scripts/cfem/preparar.py` |
| `scripts/analisar-duplicatas-cfem.mjs` | `scripts/cfem/analisar_duplicatas.py` |
| `scripts/checar-totais-regras.mjs` | `scripts/cfem/checar_totais_regras.py` |
| `scripts/atualizar-populacao.mjs` + `src/populacao.mjs` | `scripts/populacao/atualizar.py` |
| `scripts/atualizar-despesa-siconfi.mjs` + `src/despesa-siconfi.mjs` | `scripts/financas/dca_lote.py` |
| `scripts/atualizar-commodities-fred.mjs` + `src/commodities-fred.mjs` | `scripts/commodities/fred.py` |
| `scripts/servir.mjs` + `src/servidor.mjs` | `scripts/servidor/servidor.py` |
| `test/*.test.mjs` | `scripts/testes/test_*.py` |

O código em Node foi portado para Python em 08/11/2026. A conferência foi feita com os mesmos testes e comparando a saída de `cfem/preparar.py` com a do script antigo num CSV de exemplo (arquivos idênticos). O Node não é mais necessário.
