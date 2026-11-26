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
| 4. Validação | Soma as repetições integrais e as registra (RN-VPU-11), compara cada município/mês com a tabela oficial da ANM com tolerância zero (RN-VPU-12) e o total nacional com limite de 1% (RN-CFE-12); no ano aberto, marca os meses como provisórios (RN-CFE-06) | `backend/src/observatorio/validacao/cfem.py` | relatório de qualidade JSON e `aprovado` ou `reprovado` |
| 5. Publicação | Só com lote aprovado: grava parquet e manifestos numa versão imutável e troca o ponteiro `pacote.json` por último; reprovação conserva a versão anterior (RN-VPU-01, RN-VPU-03, ADR-014) | `backend/src/observatorio/publicacao/pacote.py` | `publicado/pacote.json` e `publicado/versoes/<hash>/` |
| 6. API | Lê só o pacote publicado (RN-ENT-01), confere os hashes e serve JSON, CSV e status | `backend/src/observatorio/api/` | rotas `/api/v1/...`, Swagger em `/docs` |

As etapas 2 a 5 rodam juntas pela linha de comando `observatorio.coleta`. No GitHub Actions, a etapa 1
roda a cada 4 horas (`arquivar-anm.yml`) e as etapas 2 a 5 uma vez por dia (`coletar-cfem.yml`, abaixo).

## Rodar

Comandos a partir da raiz do repositório, em Bash. No PowerShell, troque `export NOME=valor` por
`$env:NOME = "valor"`.

### 1. Obter o arquivo da Release mais recente

O download direto da ANM costuma falhar na verificação TLS (a cadeia do servidor está incompleta; ver
`OBS_ANM_CA` abaixo). A Release arquivada é a entrada reproduzível:

```bash
TAG=$(gh release list --limit 100 --json tagName -q '[.[] | select(.tagName | startswith("anm-"))][0].tagName')
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh release download "$TAG" --pattern arrecadacao.csv.gz --dir tmp/anm --clobber
```

`tmp/` e `output/` não são versionados.

### 2. Coletar, validar e publicar

```bash
export OBS_DATA_DIR=output/observatorio
export OBS_PUBLICADO_DIR=output/observatorio/publicado
uv run --project backend python -m observatorio.coleta cfem \
  --arquivo tmp/anm/arrecadacao.csv.gz \
  --origem "https://github.com/$REPO/releases/download/$TAG/arrecadacao.csv.gz" \
  --referencias data/referencia-cfem-mensal-anm.json \
  --referencias-nacionais data/referencia-cfem-nacional-anm.json \
  --evidencias data/evidencias-anm
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

Abra `http://127.0.0.1:8765/grafico-cfem.html?api=http://127.0.0.1:8000`, trocando o valor de `api` pelo
endereço da API. Sem `?api=`, a demo usa o último endereço consultado naquele navegador ou o padrão
`http://127.0.0.1:8000`. A origem da demo precisa estar em `OBS_CORS_ORIGENS`. A demo é separada do
front oficial e serve para conferir a cadeia no navegador.

### Com Docker

O `docker compose` sobe a API com o pacote montado só para leitura a partir de `OBS_PUBLICADO_HOST`
(ver [backend/README.md](../../backend/README.md)). O contêiner roda com UID 1000, sem root, e não grava
no pacote; a coleta continua sendo rodada fora dele.

```bash
cp backend/.env.example .env      # defina POSTGRES_PASSWORD; ajuste OBS_API_PORTA e OBS_CORS_ORIGENS
docker compose up -d --build
```

`OBS_API_PORTA` escolhe a porta do computador (padrão 8000; use outra se ela estiver ocupada) e
`OBS_CORS_ORIGENS` libera a demo ou o front. Crie a pasta do pacote antes de subir o contêiner: se ela
não existir, o Docker a cria com dono root no Linux, e a coleta seguinte falha por falta de permissão
(o relatório diz qual pasta e o que fazer).

## Atualizar as referências oficiais

A validação compara a arrecadação com duas tabelas da ANM, independentes do CSV: a do Pará por município
e mês (`arrecadacao_cfem_muni.aspx`) e a do Brasil por estado, cujo rodapé dá o total nacional
(`arrecadacao_cfem_ano.aspx`). As páginas capturadas ficam em `data/evidencias-anm/`, com o HTML original
comprimido, e as referências em `data/referencia-cfem-mensal-anm.json` e
`data/referencia-cfem-nacional-anm.json`.

```bash
OBS_ANM_CA=scripts/cfem/certificados/sectigo-ov-r36.pem \
uv run --project backend python -m observatorio.referencias \
  --pasta data/evidencias-anm \
  --mensal data/referencia-cfem-mensal-anm.json \
  --nacional data/referencia-cfem-nacional-anm.json \
  --resumo tmp/resumo-referencias.md
```

- Captura cada ano de 2004 até o corrente. 2003 fica de fora, porque o arquivo da ANM não tem janeiro a
  abril no país inteiro.
- Um ano cujos valores não mudaram fica como está, com a captura, a data e o SHA-256 antigos. O HTML da
  ANM muda a cada requisição, e regravá-lo sem mudança de valor só geraria ruído.
- Um ano com mês novo, valor revisto ou célula removida ganha captura e referência novas, e o resumo lista
  cada diferença.
- No ano corrente entram só os meses já fechados, e o total nacional só existe para ano fechado.
- O SHA-256 de cada referência é o do HTML, e não o do `.html.gz`. Em cada linha, a soma dos meses tem de
  fechar com o total da tabela, senão a captura falha.

O workflow `.github/workflows/atualizar-referencias-anm.yml` roda isso no dia 5 de cada mês, às 09:00 UTC,
ou à mão. Quando algo muda, ele valida a arrecadação com a referência nova sem publicar e abre um PR para
a `develop` com as capturas, os JSON, o resumo e o resultado da validação. A referência nova só passa a
valer para a coleta diária depois do merge. Valor revisto pela ANM merece atenção na revisão. Falha na
captura abre a issue "Atualização das referências da ANM falhou". Um PR aberto por workflow não dispara o
CI sozinho: o GitHub pede que alguém com acesso de escrita aprove a execução na página do PR.

O script de laboratório `scripts/cfem/referencias_anm.py` gerou a primeira versão (registro de
25/11/2026) e continua disponível para experimentos.

## Ano aberto (RN-CFE-06)

No último ano do arquivo, enquanto os 12 meses não tiverem volume suficiente (ao menos 50% da mediana de
registros por mês dos anos anteriores, exceção de 08/11/2026 da RN-CFE-06), o ano está aberto:

- mês conferido ao centavo com a tabela oficial sai como **provisório**, sem total anual;
- mês abaixo do volume, que a ANM ainda está lançando, fica fora da publicação, listado em
  `aguardando_volume` no relatório, sem reprovar o lote;
- meses posteriores ao último mês com registro ainda não aconteceram e não contam como ausentes.

A demo desenha os meses provisórios com linha pontilhada.

## Coleta agendada no GitHub Actions

`.github/workflows/coletar-cfem.yml` (ADR-011) roda todo dia às 05:30 UTC, depois do arquivamento das
04:00, e também pode ser disparado à mão (`workflow_dispatch`, com a opção `forcar`):

1. Escolhe a Release `anm-*` mais recente. Se o último pacote parcial da CFEM (`fonte-cfem-*`; na falta dele, `pacote-cfem-*`) já cita essa edição, termina sem fazer nada.
2. Baixa `arrecadacao.csv.gz` dessa Release e o pacote parcial anterior da CFEM (`publicado.tar.gz` da última
   Release `fonte-cfem-*`; na falta dela, do antigo `pacote-cfem-*`), para a publicação conferir que a série não
   encolheu.
3. Roda a coleta com `--origem` apontando para a Release e guarda o relatório de qualidade como artefato
   `qualidade-cfem` da execução.
4. Lote aprovado: cria a Release `fonte-cfem-AAAA-MM-DD-HHMM` com o pacote parcial da CFEM (`publicado.tar.gz`)
   e `qualidade-cfem.json`, sem marcá-la como Latest, e chama `publicar-pacote.yml`, que junta o último parcial
   de cada fonte no pacote servido pela API (Release `pacote-AAAA-MM-DD-HHMM`, ADR-015; decisão de 25/11/2026).
   Como o pacote chega à hospedagem fica para o ADR do serviço da AWS.
5. Falha ou reprovação: abre a issue "Coleta da CFEM falhou" com os erros do relatório, ou comenta na que
   já estiver aberta. A publicação anterior continua valendo (RN-VPU-03).

Para servir um pacote da Release na máquina local:

```bash
gh release download <tag pacote-AAAA-MM-DD-HHMM> --pattern publicado.tar.gz --dir tmp
mkdir -p output/observatorio/publicado && tar -xzf tmp/publicado.tar.gz -C output/observatorio/publicado
```

O agendamento só vale depois que o arquivo chega à branch padrão do repositório (`main`): o GitHub
roda `schedule` e lista `workflow_dispatch` só a partir dela. Uma Release criada por um workflow com o
`GITHUB_TOKEN` não dispara outro workflow; por isso a coleta é agendada, e não ligada à Release do
arquivamento.

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

- Só é publicada a observação conferida ao centavo com a tabela oficial da ANM. 2003 fica de fora (o
  arquivo não tem janeiro a abril no país inteiro); no ano aberto, os meses saem provisórios e os que
  ainda estão sendo lançados ficam de fora (ver "Ano aberto").
  Ausência de publicação não significa arrecadação zero (RN-CFE-07, RN-CFE-09).
- A edição do CSV muda quando a ANM republica o arquivo; o SHA-256 do bruto fica no relatório e a
  Release identifica a edição.
- As pendências abertas e a recomendação para cada uma estão no registro mais recente da fatia em
  [registros/](../registros/).
