# ADR-007 — Onde mora o produto e a relação com a `obcefem_api`

**Status:** aceito pelo mantenedor em 11/11/2026
**Data:** 11/11/2026
**Área:** Infraestrutura e processo
**Depende de:** nenhum

## Contexto

O projeto tem as regras de negócio, um protótipo de laboratório em `scripts/` e nenhum backend de produção. Existe a `obcefem_api` (repositório `victorsantiago/obcefem_api`), que já está publicada e serve a CFEM. Antes de escolher linguagem, armazenamento ou hospedagem, é preciso saber em que repositório o produto será escrito.

Restrições que pesam:

- A entrega é por uma API própria, e o CSV aberto sai da mesma camada (RN-ENT-02, RN-ENT-03).
- O comportamento da `obcefem_api` deve ser mantido nos itens D2 a D11 de [divergencias-entre-repositorios.md](../regras-de-negocio/divergencias-entre-repositorios.md) (decisão do mantenedor de 08/11/2026).
- A `obcefem_api` cobre só a CFEM e ainda não cumpre a homologação (RN-VPU-10) nem o formato híbrido de resposta (RN-MOD-03, exceção de 08/11/2026).
- Equipe de 1 a 2 pessoas em Python; primeira versão no ar até maio de 2027; `obcefem_api` e `obcefem` são da mesma equipe, mantidos pelo professor (restrições do mantenedor de 11/11/2026).
- Medição de 11/11/2026: a `obcefem_api` tem cerca de 2.000 linhas de aplicação (`app/` e `scripts/`) e 600 de testes, 34 commits de um só autor direto na `main`, sem branches nem PRs. A conta do mantenedor tem permissão de escrita neste repositório e só de leitura na `obcefem_api`.

A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md), criada como ADR-006 (proposta), chega à mesma direção na seção 4.1 (serviço novo neste repositório) e deixava a confirmação para o mantenedor. Este ADR registra essa confirmação; o nome da pasta continua fora.

## Alternativas consideradas

1. **Evoluir a `obcefem_api`.** O produto passaria a ser aquele repositório, e população, despesa e commodities entrariam lá. Aproveita o que já está publicado e não duplica a lógica da CFEM. Recusada porque o mantenedor não tem escrita lá, o repositório não segue o fluxo de branch e PR do `AGENTS.md`, as regras de negócio ficariam longe do código e as camadas e a validação teriam de ser encaixadas enquanto a `main` segue sendo alterada. Voltar atrás seria caro, com o código novo misturado ao do painel.
2. **Construir neste repositório, absorvendo a `obcefem_api` aos poucos.** O backend nasce aqui, fora de `scripts/`; a `obcefem_api` segue no ar até o backend novo cobrir o que ela faz. Mantém regras, ADRs e código juntos, com o fluxo de PR e o CI já existentes. Custa portar a lógica da CFEM e conviver com duas APIs por um tempo, com risco de as duas divergirem nesse intervalo.
3. **Repositório novo.** Tem os custos da opção 2 e ainda separa o código das regras, sem ganho para uma equipe de duas pessoas. Recusada.

## Decisão

O backend de produção do Observatório CFEM será construído neste repositório (`observatorio-cfem`), fora de `scripts/`. A `obcefem_api` continua no ar servindo a CFEM até o backend novo cobrir o que ela faz; aí ela é substituída.

Motivo: é a opção em que o trabalho pode começar sem depender de permissão em outro repositório, não mexe no que está no ar e deixa cada regra ao lado do código que a cumpre.

Fica de fora: o nome da pasta do produto, a linguagem, a data da troca e o destino do painel (`front/`) da `obcefem_api`.

## Consequências

- Destrava a decisão 2 (linguagem e ambiente de execução) e a decisão 3 (armazenamento das camadas) do [mapa](README.md).
- A lógica da CFEM da `obcefem_api` terá de ser portada de propósito, com os testes dela servindo de conferência; até lá existem duas APIs.
- Mudanças feitas na `obcefem_api` durante a transição precisam ser combinadas com o professor, para as duas não divergirem.
- `scripts/` continua sendo laboratório: o produto não mora lá nem importa de lá.
- Rever se o professor preferir concentrar o produto no repositório dele e der acesso de escrita. Voltar atrás custa pouco enquanto a troca não acontecer, porque nada no ar é tocado.
