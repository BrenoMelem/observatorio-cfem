# Documentação

O projeto ainda não tem produto: a documentação é a parte central do repositório. Esta página diz o que há em cada pasta e por onde começar.

## Por onde começar

| Quero... | Leia |
| --- | --- |
| Entender o projeto e o que o sistema deve garantir | [regras-de-negocio/README.md](regras-de-negocio/README.md) |
| Saber o que ainda não foi decidido | [regras-de-negocio/pendencias.md](regras-de-negocio/pendencias.md) |
| Ver como o protótipo e os outros repositórios se comparam com as regras | [regras-de-negocio/divergencias-entre-repositorios.md](regras-de-negocio/divergencias-entre-repositorios.md) |
| Rodar uma coleta ou o protótipo local | [guias/](guias/) e [../scripts/README.md](../scripts/README.md) |
| Arquivar as versões dos arquivos da ANM | [guias/arquivo-anm.md](guias/arquivo-anm.md) |
| Saber o que uma execução encontrou em certa data | [registros/](registros/) |
| Conferir uma decisão técnica ou ver as que faltam | [adr/README.md](adr/README.md) |
| Revisar a proposta da camada publicada por dimensão e do assistente (Fase 0) | [ADR-006 — PROPOSTA](adr/ADR-006-backend-publicado-assistente-proposta.md) |
| Ver as rotas do protótipo da API | [api/openapi.yaml](api/openapi.yaml) |

## Pastas

| Pasta | O que tem | Muda quando |
| --- | --- | --- |
| `regras-de-negocio/` | As regras (o quê e por quê, nunca o como), o glossário e as pendências. É a parte normativa | O mantenedor decide algo |
| `regras-de-negocio/fontes/` | Documentos de origem (decisões, blocos, plano, relatórios de laboratório, pesquisa). Material histórico: não se reescreve sem pedido explícito | Praticamente nunca |
| `guias/` | Como rodar cada coleta do protótipo (comandos, entradas, saídas). Sem resultados datados | O script muda |
| `registros/` | Resultados datados de execuções e leituras de teste. Cada arquivo é um retrato de uma data | Só se acrescenta |
| `adr/` | Decisões de arquitetura, uma por arquivo | Há uma decisão nova |
| `api/` | Esboço do contrato do protótipo local; não é contrato aprovado | A API do protótipo muda |

## Regras de escrita

- Português do Brasil, datas absolutas (por exemplo, 08/11/2026), nunca "ontem" ou "semana passada".
- Regra é norma; evidência é retrato. A evidência datada de uma regra fica numa seção "Notas de evidência" no fim do arquivo do tema, e não no corpo da regra.
- Guia diz como usar; o que uma execução encontrou vai para `registros/`.
- Nada de código, rotas ou escolha de stack em `regras-de-negocio/`. O formato das regras está no [README delas](regras-de-negocio/README.md).
