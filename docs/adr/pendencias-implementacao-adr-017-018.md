# Pendências de implementação dos ADR-017 e ADR-018

**Status:** proposta técnica para revisão do mantenedor; não altera os ADRs aceitos nem cria regra de negócio.
**Data:** 21/11/2026.

Este registro detalha dois pontos que os ADR-017 e ADR-018 deixaram para os PRs de implementação. As regras de negócio aplicáveis continuam em `docs/regras-de-negocio/`; em especial, RN-VPU-01, RN-VPU-03 e RN-VPU-04 governam a validação e a publicação.

## 1. Contrato entre fontes, validação e publicação

- `fontes/` contém um módulo por fonte. O módulo obtém o arquivo e seus metadados de origem, preserva o bruto e transforma seus registros em observações do esquema comum de `modelo/`. Ele não aprova o lote nem substitui dados publicados.
- `modelo/` define o contrato das observações. A primeira fonte implementada deve materializar os campos, tipos, nulidade e identificadores já decididos em RN-MOD e RN-TER. Um módulo de fonte entrega apenas observações conformes a esse contrato ou informa falha explícita.
- `validacao/` recebe as observações e os metadados do lote, aplica as regras de qualidade e produz o resultado da validação e o relatório do lote. Falhas de formato, campos inesperados ou ausentes e erros de conversão não se tornam valores nulos silenciosamente.
- `publicacao/` recebe somente lotes aprovados e monta o pacote imutável do ADR-014. Atualiza apenas os indicadores aprovados, com arquivo, hash e manifesto coerentes. Em caso de reprovação ou falha na montagem, preserva a versão publicada anterior.
- `api/` lê somente o pacote publicado, conforme ADR-013 e RN-ENT-01. Não importa `fontes/`, `validacao/` nem `publicacao/`.

**Conferência no PR da primeira fonte:** demonstrar uma entrada válida, uma mudança de layout rejeitada e um lote reprovado que conserva o último pacote aprovado. O contrato de imports do ADR-013 deve conferir a fronteira da API.

## 2. Tipagem no limite do Polars

- O mypy roda em `--strict` no `backend/`, como fixa o ADR-017. Uma lacuna nos tipos publicados por Polars não autoriza desligar o modo estrito para todo o pacote.
- Cada leitura declara o esquema esperado antes de entregar dados ao domínio. Conversões de código IBGE, data e dinheiro são explícitas; falhas são comunicadas à validação, sem coerção silenciosa para nulo.
- As operações de Polars permanecem encapsuladas nos módulos que leem e transformam tabelas. Na saída para `modelo/`, `validacao/` e `api/`, os valores têm tipos Python declarados e conferência em tempo de execução do esquema e da nulidade. Um valor `Any` não constitui o contrato entre camadas.
- Se os tipos fornecidos por uma dependência impedirem o mypy, a exceção fica restrita ao módulo e à verificação necessária, com justificativa junto da configuração. O PR mostra qual erro motivou a exceção e uma conferência em tempo de execução que cobre essa fronteira.
- A precisão decimal e o arredondamento seguem RN-CFE-11. A escolha de `Decimal` no Polars não substitui uma conferência dos totais e dos casos de arredondamento na primeira implementação de CFEM.

**Conferência no PR de implementação:** executar mypy `--strict` no backend, verificar no CI o esquema das observações produzidas e comparar a agregação monetária com casos conhecidos da regra. Registrar a versão de Polars no `uv.lock` e confirmar que o extra `rtcompat` funciona no ambiente de execução.

## Pontos ainda dependentes da primeira implementação

O formato concreto do modelo comum, a interface de retorno dos módulos de fonte e a forma do relatório de validação não estão fixados aqui. Devem ser definidos no PR que implementar a primeira fonte, respeitando os ADRs e as regras citadas. Esta nota não aprova a proposta de estrutura inicial registrada em `docs/adr/README.md`.
