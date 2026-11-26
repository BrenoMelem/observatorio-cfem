# Pipeline do SICONFI: despesa por função, da coleta à API

Como rodar a despesa por função do SICONFI de ponta a ponta: a API do Tesouro entra, a API do observatório entrega as observações conferidas. O padrão que cada fonte segue está em [padrao-de-pipeline-de-fonte.md](padrao-de-pipeline-de-fonte.md); o que cada execução encontrou fica em [registros/](../registros/). Este guia não traz resultados datados.

## O que é publicado

Três indicadores, um por estágio da despesa: `despesa_funcao_empenhada`, `despesa_funcao_liquidada` e `despesa_funcao_paga` (RN-FNT-04). Cada observação é um município, um exercício e uma categoria:

| `categoria` | O que é | Exemplo de `categoria_nome` |
| --- | --- | --- |
| `total` | Despesas exceto intraorçamentárias | Despesas Exceto Intraorçamentárias |
| `FF` | Função | Educação (`12`) |
| `FF.SSS` | Subfunção | Ensino Fundamental (`12.361`) |
| `FF.demais` | Subfunções que a DCA agrupa | Demais Subfunções |

Os níveis estão na mesma série. Some só categorias do mesmo nível: função com subfunção conta duas vezes. Os campos `categoria` e `categoria_nome` são a exceção de 25/11/2026 da RN-MOD-03.

## A cadeia

```
API do SICONFI → fontes/siconfi.py → validacao/siconfi.py → publicacao/ → api/ → Swagger, CSV
```

| Etapa | O que faz | Onde está |
| --- | --- | --- |
| Fonte | Para os 12 municípios, de 2013 ao ano corrente (RN-TMP-01), baixa a DCA Anexo I-E, o RREO Anexo 2 do 6º bimestre, a MSC de dezembro e o extrato de entregas, lendo todas as páginas. Guarda cada resposta comprimida, com o SHA-256 do corpo, e um `indice.json` (RN-FON-13, RN-TMP-18). Confere as chaves de cada linha e falha em layout novo (RN-VPU-04). Converte a DCA em observações com `Decimal`; a edição de cada observação é o status e a data da entrega da DCA (RN-TMP-04) | `backend/src/observatorio/fontes/siconfi.py` |
| Validação | Fechamento: a soma das funções tem de bater com o total; senão o lote é reprovado (RN-FNT-04). Conferência ao centavo (RN-VPU-12) de cada município, exercício e estágio: empenhada e liquidada com o RREO, paga com a MSC (conta 6.2.2.1.3.04, sem a modalidade 91). Só sai o que coincide no total e em todas as linhas; o resto vai para `fora_da_publicacao` no relatório, com o motivo | `backend/src/observatorio/validacao/siconfi.py` |
| Publicação | Um parquet por indicador no pacote imutável, mantendo os indicadores das outras fontes; a série homologada não pode encolher, salvo no município e exercício cuja entrega mudou (RN-VPU-02, RN-TMP-04) | `backend/src/observatorio/publicacao/pacote.py` |
| API | Rotas por dimensão com o filtro `categoria`; o CSV traz as duas colunas de categoria | `backend/src/observatorio/api/` |

### Como o RREO é casado com a DCA

O RREO não traz código de função nem de subfunção, só o nome. A validação reconhece a função pelo nome (sem acento nem pontuação: "Infra-Estrutura Urbana" e "Infraestrutura Urbana" coincidem), e "FUxx - Administração Geral" é a subfunção xx.122. O RREO lista às vezes mais subfunções que a DCA: as que a DCA agrupa em "Demais Subfunções" são somadas e comparadas com a linha `FF.demais`. A MSC tem os códigos; "Demais" é a função menos as subfunções que a DCA lista.

## Rodar

Comandos a partir da raiz do repositório, em Bash. No PowerShell, troque `export NOME=valor` por `$env:NOME = "valor"`.

Para não perder a CFEM, parta do pacote publicado mais recente:

```bash
BASE=$(gh release list --limit 100 --json tagName -q '[.[] | select(.tagName | startswith("pacote-"))][0].tagName')
mkdir -p output/observatorio/publicado
gh release download "$BASE" --pattern publicado.tar.gz --dir tmp --clobber
tar -xzf tmp/publicado.tar.gz -C output/observatorio/publicado
```

Depois:

```bash
export OBS_DATA_DIR=output/observatorio
export OBS_PUBLICADO_DIR=output/observatorio/publicado
uv run --project backend python -m observatorio.coleta siconfi
```

A coleta faz cerca de 700 consultas à API e leva de 15 a 30 minutos. A saída é um resumo em JSON com a situação, o caminho do relatório, a pasta do bruto e a contagem da conferência por estágio. Com `--somente-se-mudou`, ela consulta só o extrato de entregas e para (`sem_mudanca`) se ele for igual ao do relatório publicado.

O relatório de qualidade fica em `output/observatorio/qualidade/siconfi-<execução>.json` e dentro do pacote como `qualidade-siconfi.json`. O bruto fica em `output/observatorio/bruto/siconfi/<execução>/`.

Para servir e consultar a API, siga a seção correspondente de [pipeline-cfem.md](pipeline-cfem.md) (a API em execução não recarrega o código nem o pacote validado de novo; reinicie depois de mudar `api/`). Exemplo:

```bash
curl "http://127.0.0.1:8090/api/v1/dimensoes/economica?municipio_id=1505536&categoria=12"
curl -o despesa.csv "http://127.0.0.1:8090/api/v1/dimensoes/economica.csv?categoria=total"
```

## Workflow

`.github/workflows/coletar-siconfi.yml` roda no dia 5 de cada mês (RN-TMP-02, exceção de 25/11/2026). Ele baixa o pacote parcial anterior do SICONFI (`fonte-siconfi-*`), roda a coleta com `--somente-se-mudou` e, se o lote for aprovado, cria a Release `fonte-siconfi-AAAA-MM-DD-HHMM` com o pacote parcial (`publicado.tar.gz`), `qualidade-siconfi.json` e `siconfi-bruto.tar.gz` (as respostas da API, com o SHA-256 de cada uma em `indice.json`). Falha abre ou comenta a issue "Coleta do SICONFI falhou". `workflow_dispatch` com `forcar` coleta mesmo sem entrega nova.

Depois, o workflow chama `publicar-pacote.yml` (`workflow_call`), o único que monta o pacote servido pela API: junta o último pacote parcial de cada fonte (`python -m observatorio.coleta montar --parcial PASTA ...`) e cria a Release `pacote-AAAA-MM-DD-HHMM`. Cada fonte parte só do parcial dela, então uma não apaga a outra, e a montagem só roda com um parcial aprovado. Se a montagem reprova, o pacote anterior continua valendo (RN-VPU-03) e abre a issue "Montagem do pacote falhou". Também pode ser disparado à mão.

## O que o relatório diz

| Campo | O que é |
| --- | --- |
| `conferencia` | Por estágio: município-anos com DCA, conferidos, sem referência e divergentes |
| `conferidos` | `município:ano:estágio` publicados |
| `fora_da_publicacao` | O que ficou de fora, com o motivo e até 20 linhas divergentes (`categoria: valor na DCA, valor na referência`) |
| `ausencias_municipais` | `município:ano` sem DCA na API (ausente, nunca zero) |
| `entregas` e `entregas_alteradas` | O extrato usado e o que mudou desde o pacote anterior (RN-TMP-04) |
| `linhas_intraorcamentarias_fora` | Linhas "Despesas Intraorçamentárias" da DCA, que não entram no indicador |
