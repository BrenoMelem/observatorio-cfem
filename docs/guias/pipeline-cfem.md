# Pipeline da CFEM: da coleta à API

Como rodar a fatia da arrecadação da CFEM de ponta a ponta: o arquivo bruto da ANM entra, a API
entrega as observações validadas. O padrão que cada fonte segue está em
[padrao-de-pipeline-de-fonte.md](padrao-de-pipeline-de-fonte.md); o que cada execução encontrou fica
em [registros/](../registros/). Este guia não traz resultados datados.

## A cadeia em uma linha

```
ANM (CSV) → Release anm-* → fontes/ → modelo/ → validacao/ → publicacao/ → api/ → Swagger, CSV, demo
```

| Etapa | O que faz | Onde está | O que produz |
| --- | --- | --- | --- |
| 1. Arquivamento | A cada 4 horas guarda o CSV da ANM numa Release, com o relatório de diferenças entre edições | `.github/workflows/arquivar-anm.yml`, [arquivo-anm.md](arquivo-anm.md) | Release `anm-AAAA-MM-DD-HHMM` com `arrecadacao.csv.gz` |
| 2. Fonte | Lê o CSV (latin-1, vírgula decimal), confere as colunas, recorta os 12 municípios e converte cada linha em observação do modelo comum, com URL, data e SHA-256 do bruto | `backend/src/observatorio/fontes/cfem_arrecadacao.py` | `Lote` de observações |
| 3. Modelo | Os 14 campos da observação (RN-MOD-03), dinheiro em `Decimal`, ausente nunca vira zero | `backend/src/observatorio/modelo/` | contrato entre as etapas |
| 4. Validação | Soma as repetições integrais e as registra (RN-VPU-11), compara cada município/mês com a tabela oficial da ANM com tolerância zero (RN-VPU-12) e o total nacional com limite de 1% (RN-CFE-12) | `backend/src/observatorio/validacao/cfem.py` | relatório de qualidade JSON e `aprovado` ou `reprovado` |
| 5. Publicação | Só com lote aprovado: grava parquet e manifestos numa versão imutável e troca o ponteiro `pacote.json` por último; reprovação conserva a versão anterior (RN-VPU-01, RN-VPU-03, ADR-014) | `backend/src/observatorio/publicacao/pacote.py` | `publicado/pacote.json` e `publicado/versoes/<hash>/` |
| 6. API | Lê só o pacote publicado (RN-ENT-01), confere os hashes e serve JSON, CSV e status | `backend/src/observatorio/api/` | rotas `/api/v1/...`, Swagger em `/docs` |

A etapa 1 já roda sozinha no GitHub Actions. As etapas 2 a 5 rodam juntas pela linha de comando
`observatorio.coleta`; ainda não há agendamento nem abertura de issue na falha (ADR-011).

## Rodar

Comandos a partir da raiz do repositório, em Bash. No PowerShell, troque `export NOME=valor` por
`$env:NOME = "valor"`.

### 1. Obter o arquivo da Release mais recente

O download direto da ANM costuma falhar na verificação TLS (a cadeia do servidor está incompleta; ver
`OBS_ANM_CA` abaixo). A Release arquivada é a entrada reproduzível:

```bash
TAG=$(gh release list --limit 1 --json tagName -q '.[0].tagName')
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh release download "$TAG" --pattern arrecadacao.csv.gz --dir tmp/anm --clobber
```

`tmp/` e `output/` não são versionados.

### 2. Coletar, validar e publicar

```bash
export OBS_DATA_DIR=output/observatorio
export OBS_PUBLICADO_DIR=output/observatorio/publicado
uv run --project backend python -m observatorio.coleta cfem   --arquivo tmp/anm/arrecadacao.csv.gz   --origem "https://github.com/$REPO/releases/download/$TAG/arrecadacao.csv.gz"   --referencias data/referencia-cfem-mensal-anm.json   --referencias-nacionais data/referencia-cfem-nacional-anm.json   --evidencias docs/registros/evidencias-anm-2026-11-23
```

A coleta lê o `.csv.gz` direto e calcula o SHA-256 do CSV descompactado, que identifica a edição da ANM
igual a um download direto. `--origem` registra no relatório de onde vieram os bytes (RN-FON-13); sem
ele, a origem registrada é a URL da ANM. Um CSV já descompactado também é aceito em `--arquivo`.

A saída é um resumo JSON com `situacao` (`aprovado` ou `reprovado`), a versão do pacote e o caminho
do relatório. O código de saída é 0 só quando o lote é aprovado. O relatório completo fica em
`$OBS_DATA_DIR/qualidade/cfem-<data>-<id>.json`.

Sem `--arquivo`, a coleta faz GET na ANM com User-Agent de navegador. Para isso, aponte
`OBS_ANM_CA` para o certificado intermediário versionado
(`scripts/cfem/certificados/sectigo-ov-r36.pem`); não desligue a verificação.

### 3. Subir a API

```bash
export OBS_CORS_ORIGENS=http://127.0.0.1:8765        # só se a demo for aberta
uv run --project backend uvicorn observatorio.api.main:app
```

| Endereço | O que mostra |
| --- | --- |
| `http://127.0.0.1:8000/saude` | `pronto`, `sem_publicacao` ou `publicacao_invalida` com o motivo |
| `http://127.0.0.1:8000/docs` | Swagger: as rotas, os filtros e os esquemas de resposta, com botão para testar |
| `http://127.0.0.1:8000/openapi.json` | a especificação OpenAPI gerada pela aplicação |
| `/api/v1/dimensoes/economica?periodicidade=anual` | CFEM anual (só anos com 12 meses validados) |
| `/api/v1/dimensoes/economica.csv` | o mesmo recorte em CSV, com fonte, método e limitações em cada linha |
| `/api/v1/indicadores/status` | situação de cada indicador do manifesto |

O contrato que o front consome é o Swagger gerado pela aplicação. A cópia versionada fica em
[../api/openapi-producao.yaml](../api/openapi-producao.yaml); `../api/openapi.yaml` é do protótipo
do laboratório e não descreve esta API. Um teste do backend falha quando a cópia diverge da API; depois
de mudar uma rota ou um esquema, regrave-a de dentro de `backend/` com
`uv run pytest tests/api/test_openapi.py --atualizar-openapi` e versione o arquivo junto.

### 4. Abrir a demo (opcional)

```bash
python -m http.server 8765 --directory backend/demo
```

Abra `http://127.0.0.1:8765/grafico-cfem.html` e informe o endereço da API. A demo é separada do
front oficial e serve para conferir a cadeia no navegador.

### Com Docker

O `docker compose` sobe a API com o pacote montado só para leitura a partir de `OBS_PUBLICADO_HOST`
(ver [backend/README.md](../../backend/README.md)). A coleta continua sendo rodada fora do contêiner.
Se o Docker criar a pasta de publicação antes da coleta, ela pode ficar com dono root e a coleta
falha com `Permission denied` em `.publicando`; crie a pasta antes de subir o contêiner.

## Variáveis de ambiente

Todas são lidas só em `backend/src/observatorio/config.py` (ADR-017).

| Variável | Padrão | Para quê |
| --- | --- | --- |
| `OBS_DATA_DIR` | `output/observatorio` | bruto e relatórios de qualidade |
| `OBS_PUBLICADO_DIR` | `output/observatorio/publicado` | pacote publicado, lido pela API |
| `OBS_MANIFESTO` | `data/indicadores.json` | manifesto de indicadores copiado para o pacote |
| `OBS_ANM_CA` | vazio | certificado intermediário para o GET direto na ANM |
| `OBS_CORS_ORIGENS` | vazio | origens aceitas pela API, separadas por vírgula |

## Limites conhecidos

- A referência mensal cobre só os anos já conciliados; a observação sem referência não é publicada.
  Ausência de publicação não significa arrecadação zero (RN-CFE-07, RN-CFE-09).
- A edição do CSV muda quando a ANM republica o arquivo; o SHA-256 do bruto fica no relatório e a
  Release identifica a edição.
- As pendências abertas e a recomendação para cada uma estão no registro mais recente da fatia em
  [registros/](../registros/).
