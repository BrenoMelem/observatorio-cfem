"""Generate a reproducible, instructional Colab notebook for CFEM source probes."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "laboratorio_fontes_observatorio_cfem.ipynb"
cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)})


def code(text):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.strip().splitlines(keepends=True)})


md("""
# Laboratório de consumo de dados — Observatório CFEM / RI Carajás

**Objetivo.** Aprender a chamar fontes públicas, conferir a estrutura e provar se existe dado para os municípios. Criado a partir do notebook do Daniel e dos documentos do projeto em 15/10/2026. Os resultados só são atuais depois de você executar as células.

**Como usar.** Abra no Colab, execute uma célula de cada vez com o botão ▶ ou `Shift+Enter`, leia a saída e avance. `OK` significa apenas que a prova descrita naquela linha passou. Um portal HTTP 200, um metadado ou um `import` não comprovam série municipal. Não coloque chaves nem JSON de service account no notebook.

**Referências do projeto.** `docs/pesquisa-observatorio-cfem/analise-consumo-dados-por-topico.md` e `tmp/Observatorio-RI-Carajas-Registro-de-Decisoes-Daniel.txt`. Fonte primária e Base dos Dados devem aparecer separadas na proveniência.
""")

md("""## 1. Preparar a bancada

Esta célula não consulta rede. Ela fixa o território e cria o registro dos testes. O código IBGE tem sete dígitos e deve continuar como texto, para evitar perda de zeros em outros estados.""")
code('''import csv, io, os, json, re, unicodedata
from datetime import datetime, timezone
import requests
import pandas as pd

MUNICIPIOS = {
    "1501576": "Bom Jesus do Tocantins", "1501758": "Brejo Grande do Araguaia",
    "1502152": "Canaã dos Carajás", "1502772": "Curionópolis",
    "1502954": "Eldorado do Carajás", "1504208": "Marabá",
    "1505494": "Palestina do Pará", "1505536": "Parauapebas",
    "1505635": "Piçarra", "1507151": "São Domingos do Araguaia",
    "1507458": "São Geraldo do Araguaia", "1507508": "São João do Araguaia"
}
S = requests.Session()
S.headers.update({"User-Agent": "Observatorio-CFEM-pesquisa/0.1"})
resultados = []
def registrar(fonte, prova, estado, evidencia, proximo=""):
    item = {"fonte": fonte, "prova": prova, "estado": estado,
            "evidencia": str(evidencia)[:500], "proximo_passo": proximo,
            "executado_em_utc": datetime.now(timezone.utc).isoformat()}
    resultados.append(item)
    print(f"[{estado}] {fonte} — {prova}: {item['evidencia']}")

def obter(url, **kwargs):
    resposta = S.get(url, timeout=(10, 35), **kwargs)
    resposta.raise_for_status()  # não suprimir erro de certificado TLS
    return resposta

def normalizar(s):
    return ''.join(c for c in unicodedata.normalize('NFD', str(s))
                   if unicodedata.category(c) != 'Mn').casefold()

print(f"Bancada pronta: {len(MUNICIPIOS)} municípios.")''')

md("""## 2. IBGE Localidades: conferir o de-para

**Hipótese:** os 12 códigos devolvem os nomes esperados. Veja o status e a lista de divergências. Esta prova valida o território, não uma série de indicador.""")
code('''divergencias = []
for codigo, esperado in MUNICIPIOS.items():
    try:
        dado = obter(f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo}").json()
        if normalizar(dado.get("nome")) != normalizar(esperado):
            divergencias.append((codigo, esperado, dado.get("nome")))
    except Exception as exc:
        divergencias.append((codigo, esperado, f"{type(exc).__name__}: {exc}"))
registrar("IBGE Localidades", "12 códigos e nomes", "OK" if not divergencias else "ATENCAO",
          "12/12 conferidos" if not divergencias else divergencias)
''')

md("""## 3. SIDRA: dado real de um indicador

O agregado 6579 é usado aqui como **sonda** de estimativa populacional. A resposta precisa conter linha para Canaã e valor numérico. Antes de integrar ao produto, fixem variável, unidade, período e diferença metodológica entre estimativa e Censo. Consulte [a documentação oficial](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3).""")
code('''try:
    meta = obter("https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados").json()
    periodos = obter("https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos").json()
    ultimo = str(max(int(p["id"]) for p in periodos if str(p.get("id", "")).isdigit()))
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/{ultimo}/variaveis/all?localidades=N6[1502152]"
    bruto = obter(url).json()
    series = [s for variavel in bruto for resultado in variavel.get("resultados", [])
              for s in resultado.get("series", [])]
    amostras = [(s.get("localidade", {}).get("id"), s.get("serie", {})) for s in series]
    validas = [(geo, valores) for geo, valores in amostras
               if str(geo) == "1502152" and any(re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", str(v or ""))
                                                   for v in valores.values())]
    registrar("IBGE SIDRA", "valor municipal no agregado 6579", "OK" if validas else "ATENCAO",
              {"periodo": ultimo, "variaveis": [v.get("id") for v in bruto], "amostra": validas[:1], "url": url},
              "Fixar variável e unidade no manifesto antes da ingestão")
except Exception as exc:
    registrar("IBGE SIDRA", "valor municipal no agregado 6579", "FALHA", f"{type(exc).__name__}: {exc}")''')

md("""## 4. SICONFI: DCA com linhas fiscais

Usamos um exercício fechado para evitar interpretar ausência de publicação como falha da API. `items` não vazio e campos fiscais são exigidos. A paginação e a seleção do estágio da despesa ainda precisam entrar no adaptador definitivo. [Documentação](https://apidatalake.tesouro.gov.br/docs/siconfi/).""")
code('''try:
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
    dados = obter(url, params={"id_ente": "1502152", "an_exercicio": 2024,
                                    "no_anexo": "DCA-Anexo I-E"}).json()
    linhas = dados.get("items", [])
    campos = set(linhas[0]) if linhas else set()
    passou = bool(linhas) and "conta" in campos
    registrar("SICONFI", "DCA 2024 Canaã", "OK" if passou else "ATENCAO",
              {"linhas_primeira_pagina": len(linhas), "campos": sorted(campos)[:20],
               "ha_proxima_pagina": dados.get("hasMore")},
              "Definir conta, estágio e paginação antes da série de despesa")
except Exception as exc:
    registrar("SICONFI", "DCA 2024 Canaã", "FALHA", f"{type(exc).__name__}: {exc}")''')

md("""## 5. ANM: estrutura dos três CSVs da CFEM

Lemos somente o cabeçalho e algumas linhas. A presença da coluna municipal comprova **estrutura**, ainda não comprova que os 12 municípios estão no arquivo inteiro. Arrecadação, distribuição e autuação são medidas diferentes. [Diretório oficial](https://dadosabertos.anm.gov.br/CFEM/).""")
code('''ARQUIVOS = {
    "arrecadacao": ("https://dadosabertos.anm.gov.br/CFEM/CFEM_Arrecadacao.csv", "CodigoMunicipio"),
    "distribuicao": ("https://dadosabertos.anm.gov.br/CFEM/CFEM_Distribuicao.csv", "CodigoEnte"),
    "autuacao": ("https://dadosabertos.anm.gov.br/CFEM/CFEM_Autuacao.csv", "Município"),
}
for nome, (url, coluna) in ARQUIVOS.items():
    try:
        with S.get(url, stream=True, timeout=(10, 35)) as r:
            r.raise_for_status()
            amostra = list(zip(range(6), r.iter_lines()))
        linhas = [x for _, x in amostra if x]
        try:
            cab = linhas[0].decode('utf-8-sig')
        except UnicodeDecodeError:
            cab = linhas[0].decode('latin-1')
        dialeto = csv.Sniffer().sniff(cab, delimiters=',;')
        colunas = next(csv.reader([cab], delimiter=dialeto.delimiter))
        encontrou = normalizar(coluna) in {normalizar(c.strip()) for c in colunas}
        registrar("ANM CFEM", f"cabeçalho {nome}", "OK" if encontrou else "ATENCAO",
                  {"separador": dialeto.delimiter, "colunas": colunas, "url": url},
                  "Baixar e filtrar o arquivo inteiro para confirmar os 12 municípios")
    except Exception as exc:
        registrar("ANM CFEM", f"cabeçalho {nome}", "FALHA", f"{type(exc).__name__}: {exc}")''')

md("""## 6. ANM AMB: VPM tem município?

Detectamos o delimitador real do cabeçalho. O notebook de referência forçava `;` e por isso leu o CSV inteiro como uma coluna. **Não conclua** que existe ou não município quando houver falha de download ou de leitura.""")
code('''for nome in ["Producao_Bruta.csv", "Producao_Beneficiada.csv"]:
    url = "https://dadosabertos.anm.gov.br/AMB/" + nome
    try:
        with S.get(url, stream=True, timeout=(10, 35)) as r:
            r.raise_for_status()
            cab_bytes = next(line for line in r.iter_lines() if line)
            try:
                cab = cab_bytes.decode('utf-8-sig')
            except UnicodeDecodeError:
                cab = cab_bytes.decode('latin-1')
        dialeto = csv.Sniffer().sniff(cab, delimiters=',;')
        colunas = [c.strip() for c in next(csv.reader([cab], delimiter=dialeto.delimiter))]
        municipais = [c for c in colunas if "munic" in normalizar(c)]
        registrar("ANM AMB", nome, "OK" if municipais else "ATENCAO",
                  {"separador": dialeto.delimiter, "colunas": colunas,
                   "colunas_municipais": municipais},
                  "Se só houver UF, tratar VPM como contexto estadual")
    except Exception as exc:
        registrar("ANM AMB", nome, "FALHA", f"{type(exc).__name__}: {exc}")''')

md("""## 7. Portais de apoio: disponibilidade não é capacidade de consumo

Este teste só mostra redirecionamento, código HTTP, tipo de conteúdo e URL final. `403` ou erro TLS pode depender do ambiente. Nunca usar `verify=False` para transformar esse erro em sucesso. Para cada portal, procure depois o **arquivo ou exportação específico**, seu ano, licença, colunas e recorte municipal.""")
code('''PORTAIS = {
 "FAPESPA": "https://www.fapespa.pa.gov.br/estatistica-municipal/",
 "Atlas da Violência": "https://www.ipea.gov.br/atlasviolencia/",
 "SEEG": "https://seeg.eco.br/dados/",
 "World Bank Pink Sheet": "https://www.worldbank.org/en/research/commodity-markets",
 "IDSC": "https://idsc.cidadessustentaveis.org.br/",
 "TSE Eleitorado": "https://dadosabertos.tse.jus.br/",
 "INEP Censo Escolar": "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-escolar",
 "DETRAN-PA Frota": "https://dashboard-frota.detran.pa.gov.br/",
}
for nome, url in PORTAIS.items():
    try:
        r = obter(url)
        registrar(nome, "portal acessível", "OK", {"http": r.status_code, "final": r.url,
                  "tipo": r.headers.get("Content-Type", "")}, "Localizar dataset/exportação e testar dados municipais")
    except Exception as exc:
        registrar(nome, "portal acessível", "ATENCAO", f"{type(exc).__name__}: {exc}",
                  "Conferir manualmente no navegador; não inferir ausência de dados")''')

md("""## 8. Base dos Dados / BigQuery — exercício guiado com controle de custo

A Base dos Dados é uma cópia tratada de fontes públicas no BigQuery, não a produtora original. Uma consulta requer **projeto Google Cloud com BigQuery habilitado e cobrança configurada**. Primeiro verifique o projeto e a estimativa de bytes; execute consultas pagas somente após conferir cotas e orçamento. Não faça upload de JSON de service account para o Colab ou Git. No Colab, use autenticação da própria conta. O projeto abaixo é apenas o nome visto no notebook de referência; troque se necessário. [Como consultar](https://basedosdados.org/), [BigQuery Python](https://cloud.google.com/python/docs/reference/bigquery/latest).

**Passos:** (1) confirme o ID do seu projeto; (2) execute a célula de login abaixo e autorize sua conta; (3) execute o `dry run`; (4) se a estimativa couber no orçamento, mude `EXECUTAR_CONSULTA` para `True` e execute de novo. O limite de cobrança por consulta está em 100 MiB. Nenhuma chave é impressa.""")
code('''GCP_PROJECT = "bigquery-511713"  # confirme no console antes de executar
EXECUTAR_CONSULTA = False
TABELAS = {
    "populacao": "basedosdados.br_ibge_populacao.municipio",
    "pib": "basedosdados.br_ibge_pib.municipio",
    "ideb": "basedosdados.br_inep_ideb.municipio",
}
print("Projeto escolhido:", GCP_PROJECT, "| execução de consulta:", EXECUTAR_CONSULTA)
''')
code('''# Esta célula abre uma autorização Google no Colab; execute manualmente.
from google.colab import auth
auth.authenticate_user()
from google.cloud import bigquery
client = bigquery.Client(project=GCP_PROJECT)
print("Autenticado. Projeto de cobrança:", client.project)''')
code('''from google.cloud import bigquery
MAX_BYTES = 100 * 1024 * 1024
codigos_sql = ",".join("'" + codigo + "'" for codigo in MUNICIPIOS)
sql = f"""SELECT ano, id_municipio, populacao
FROM `basedosdados.br_ibge_populacao.municipio`
WHERE id_municipio IN ({codigos_sql}) AND ano = 2024
LIMIT 20"""
try:
    cfg = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    ensaio = client.query(sql, job_config=cfg)
    bytes_estimados = ensaio.total_bytes_processed
    print("Bytes estimados:", bytes_estimados)
    if not EXECUTAR_CONSULTA:
        registrar("Base dos Dados", "população municipal", "PENDENTE",
                  f"dry run OK; {bytes_estimados} bytes estimados; consulta não executada",
                  "Revisar orçamento e alterar EXECUTAR_CONSULTA para True")
    elif bytes_estimados > MAX_BYTES:
        registrar("Base dos Dados", "população municipal", "ATENCAO",
                  f"{bytes_estimados} bytes acima do limite local de 100 MiB")
    else:
        cfg = bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES)
        df_bd = client.query(sql, job_config=cfg).to_dataframe()
        codigos = set(df_bd.get("id_municipio", pd.Series(dtype=str)).astype(str))
        registrar("Base dos Dados", "população municipal", "OK" if codigos else "ATENCAO",
                  {"linhas": len(df_bd), "municipios": sorted(codigos),
                   "anos": sorted(df_bd["ano"].unique().tolist()) if len(df_bd) else []},
                  "Comparar total e ano com IBGE primário")
        display(df_bd.head())
except NameError:
    registrar("Base dos Dados", "população municipal", "PENDENTE",
              "Execute antes a célula de autenticação")
except Exception as exc:
    registrar("Base dos Dados", "população municipal", "FALHA", f"{type(exc).__name__}: {exc}")''')

md("""### 8.1 Descobrir tabelas TSE e Censo Escolar sem adivinhar o `table_id`

Com o cliente autenticado, liste os datasets e tabelas no catálogo. Só depois escreva uma consulta municipal pequena. Os nomes abaixo são candidatos e podem mudar; registre `dataset.table` realmente encontrado e confira o esquema (`id_municipio`, `ano`, medida).""")
code('''for prefixo in ("br_tse", "br_inep_censo_escolar"):
    try:
        encontrados = [d.dataset_id for d in client.list_datasets("basedosdados")
                       if d.dataset_id.startswith(prefixo)]
        print(prefixo, "datasets:", encontrados)
        for ds in encontrados[:5]:
            print(ds, "tabelas:", [t.table_id for t in client.list_tables(f"basedosdados.{ds}")][:30])
    except NameError:
        print("Execute primeiro a autenticação BigQuery.")
        break
    except Exception as exc:
        print(prefixo, type(exc).__name__, str(exc)[:300])''')

md("""## 9. Google Earth Engine / MapBiomas

O “GE” citado pode ser o Google Earth Engine. Para uso, a conta e o projeto Cloud precisam estar registrados no Earth Engine; o formulário é feito no [cadastro oficial](https://earthengine.google.com/signup/). Escolha a modalidade de pesquisa/não comercial apenas se ela corresponder ao projeto e às regras atuais. O cadastro e a autenticação devem ser preenchidos pelo responsável pela conta; não cole credenciais aqui. Depois, configure `GEE_PROJECT` e execute **manualmente**. A existência de asset não comprova ainda a estatística municipal. Como caminho alternativo, use as [estatísticas municipais publicadas pelo MapBiomas](https://brasil.mapbiomas.org/downloads/).""")
code('''GEE_PROJECT = ""  # preencha com o ID do projeto autorizado
if not GEE_PROJECT:
    registrar("MapBiomas / GEE", "asset e bandas", "PENDENTE", "GEE_PROJECT não configurado",
              "Concluir cadastro oficial e autenticar no Earth Engine")
else:
    try:
        import ee
        ee.Authenticate()  # autorização interativa; não salvar token no notebook
        ee.Initialize(project=GEE_PROJECT)
        parent = "projects/mapbiomas-public/assets/brazil/lulc/collection11"
        assets = ee.data.listAssets({"parent": parent}).get("assets", [])
        registrar("MapBiomas / GEE", "lista de assets", "OK" if assets else "ATENCAO",
                  {"quantidade": len(assets), "amostra": [a.get("name") for a in assets[:5]]},
                  "Escolher imagem/ano/classe e calcular área dos municípios")
    except Exception as exc:
        registrar("MapBiomas / GEE", "lista de assets", "ATENCAO", f"{type(exc).__name__}: {exc}")''')

md("""## 10. Consolidar e exportar a evidência

Execute ao final. O CSV preserva estado, evidência e horário. Para entregar ao repositório, baixe-o pelo painel de arquivos do Colab; **não** suba tokens, chaves nem dados individuais. `PENDENTE` significa que o teste não rodou; `ATENCAO` é uma limitação ou falha contextual, não prova de ausência da fonte.""")
code('''resumo = pd.DataFrame(resultados)
display(resumo)
print(resumo.groupby("estado").size() if not resumo.empty else "Nenhum teste executado")
resumo.to_csv("resultado_testes_fontes_cfem.csv", index=False, encoding="utf-8-sig")
print("Arquivo: resultado_testes_fontes_cfem.csv")''')

OUT.parent.mkdir(parents=True, exist_ok=True)
notebook = {"cells": cells, "metadata": {"colab": {"name": OUT.name},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
print(OUT)
