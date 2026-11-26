# Documentação

O projeto ainda não tem produto: a documentação é a parte central do repositório. Esta página diz o que há em cada pasta e por onde começar.

## Por onde começar

| Quero... | Leia |
| --- | --- |
| Entender o projeto e o que o sistema deve garantir | [regras-de-negocio/README.md](regras-de-negocio/README.md) |
| Saber o que o produto deve entregar, com os prazos, e o que as regras já cobrem | [produto/backlog.md](produto/backlog.md) |
| Saber o que ainda não foi decidido | [regras-de-negocio/pendencias.md](regras-de-negocio/pendencias.md) |
| Ver como o protótipo e os outros repositórios se comparam com as regras | [regras-de-negocio/divergencias-entre-repositorios.md](regras-de-negocio/divergencias-entre-repositorios.md) |
| Rodar uma coleta ou o protótipo local | [guias/](guias/) e [../scripts/README.md](../scripts/README.md) |
| Estrutura do produto e como rodar a API (com `uv` ou Docker) | [../backend/README.md](../backend/README.md) |
| Arquivar as versões dos arquivos da ANM | [guias/arquivo-anm.md](guias/arquivo-anm.md) |
| Saber o que uma execução encontrou em certa data | [registros/](registros/) |
| Conferir uma decisão técnica ou ver as que faltam | [adr/README.md](adr/README.md) |
| Ler a análise da Fase 0 (rotas existentes, dimensões do site, propostas para a camada publicada e o assistente) | [adr/analise-fase-0-camada-publicada-e-assistente.md](adr/analise-fase-0-camada-publicada-e-assistente.md) |
| Rodar o pipeline da CFEM da coleta à API, com o Swagger | [guias/pipeline-cfem.md](guias/pipeline-cfem.md) |
| Rodar o pipeline da despesa por função do SICONFI | [guias/pipeline-siconfi.md](guias/pipeline-siconfi.md) |
| Ver o contrato da API do produto (para o front) | [api/openapi-producao.yaml](api/openapi-producao.yaml) |
| Ver as rotas do protótipo do laboratório | [api/openapi.yaml](api/openapi.yaml) |

## Pastas

| Pasta | O que tem | Muda quando |
| --- | --- | --- |
| `regras-de-negocio/` | As regras (o quê e por quê, nunca o como), o glossário e as pendências. É a parte normativa | O mantenedor decide algo |
| `regras-de-negocio/fontes/` | Documentos de origem (decisões, blocos, plano, relatórios de laboratório, pesquisa). Material histórico: não se reescreve sem pedido explícito | Praticamente nunca |
| `produto/` | O Product Backlog (retrato datado da ferramenta de gestão) e a correspondência de cada item com as regras e as decisões técnicas. Não é fonte de regra | Há uma exportação nova do backlog ou uma regra passa a cobrir um item |
| `guias/` | Como rodar cada coleta do protótipo (comandos, entradas, saídas). Sem resultados datados | O script muda |
| `registros/` | Resultados datados de execuções e leituras de teste. Cada arquivo é um retrato de uma data | Só se acrescenta |
| `adr/` | Decisões de arquitetura, uma por arquivo | Há uma decisão nova |
| `api/` | `openapi-producao.yaml`: cópia da especificação gerada pela API do produto. `openapi.yaml`: esboço do protótipo local do laboratório. Nenhum dos dois é contrato aprovado | A API muda |

## Regras de escrita

- Português do Brasil, datas absolutas (por exemplo, 08/11/2026), nunca "ontem" ou "semana passada".
- Regra é norma; evidência é retrato. A evidência datada de uma regra fica numa seção "Notas de evidência" no fim do arquivo do tema, e não no corpo da regra.
- Guia diz como usar; o que uma execução encontrou vai para `registros/`.
- Nada de código, rotas ou escolha de stack em `regras-de-negocio/`. O formato das regras está no [README delas](regras-de-negocio/README.md).
