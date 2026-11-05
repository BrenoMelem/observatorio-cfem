---
name: apresentar-decisoes
description: Prepara e organiza a apresentação (.pptx) das decisões tomadas no projeto Observatório CFEM desde a última reunião, para o professor e o grupo do projeto. Lê docs/reunioes.md, levanta o que foi decidido no período, separa decisão de evidência e de pendência, e monta poucos slides com o que mudou, o que contraria o plano anterior e o que precisa do professor. Use sempre que o usuário falar em reunião, apresentação, slides, pauta, "o que decidimos", "o que mudou desde a última reunião", "preparar para o professor" ou "atualizar o grupo", mesmo que não diga "apresentação". Use também depois da reunião, para registrá-la em docs/reunioes.md.
---

# Apresentar as decisões do projeto

Esta skill transforma o que foi decidido nas regras de negócio em uma apresentação curta. O público é o professor e o grupo, e o professor tem pouco tempo: por isso a apresentação mostra o que mudou e o que precisa dele, e deixa o detalhe para as notas dos slides. Ela serve para informar, não para decidir. Decidir uma regra é outro trabalho, da skill `decidir-regra`.

Leia o `AGENTS.md` da raiz se ainda não estiver no contexto. Ele define o que é decisão, evidência e pendência, e a regra de não fazer commit sem pedido.

## Passo 1: descobrir o período

Leia `docs/reunioes.md`.

- Se houver uma reunião já **realizada**, o período começa no dia seguinte à data da última e vai até hoje (ou até a data da reunião que está sendo preparada).
- Se só houver a reunião **planejada** (a primeira), use a coluna "Período coberto" dela.
- Se o arquivo não existir ou as datas estiverem ambíguas, pergunte "desde quando?". Não adivinhe: um período errado faz a apresentação repetir o que o grupo já viu ou esconder uma decisão.

## Passo 2: levantar o que aconteceu

Rode o script, que lê as regras e o histórico do Git:

```
python .claude/skills/apresentar-decisoes/scripts/coletar_decisoes.py --desde DD/MM/AAAA --ate DD/MM/AAAA
```

Para apresentar o estado de uma branch que ainda não está na `main` (por exemplo, a de outro mantenedor), crie um worktree dela em `tmp/` (`git worktree add --detach tmp/base-NOME origin/BRANCH`), rode o script com `--raiz tmp/base-NOME` e remova o worktree no fim (`git worktree remove --force`). O script lê só as regras, então o `.claude/` não precisa estar na branch.

Ele devolve os totais de regras antes e agora, as regras DECIDIDAS com uma DECISÃO-MANTENEDOR no período (agrupadas por tema), as regras com evidência nova mas sem decisão, e o que continua EM ABERTO. Use `--formato json` se quiser processar o resultado.

O script só lista. Para cada decisão que for aparecer num slide, **leia a regra** no arquivo do tema (campos Regra, Motivo e Exceções), porque o título sozinho engana. Os limites do script, para você compensar:

- A marca "contraria fonte anterior" vem de palavras no texto e pode deixar passar casos. Releia o campo Exceções das decisões de rota e de entrega (por exemplo, a entrega por API contraria DECISÕES e PLANO).
- Decisões que mudaram só um ponto de uma regra já decidida podem aparecer como "evidência sem decisão". Confira no `pendencias.md` e no `git log` do arquivo.
- A data 24/10/2026 reúne as respostas da primeira rodada de perguntas; são muitas decisões de uma vez, não um dia de trabalho.

## Passo 3: escolher o que entra

Para o professor, menos é mais. Ordene as decisões por quanto elas mudam o produto e leve ao slide só as que passam em algum destes critérios:

1. contrariam o que estava escrito antes (DECISÕES, BLOCOS, PLANO), porque ele precisa saber;
2. mudam o que o usuário vai ver ou os dados que serão publicados;
3. bloqueiam ou liberam algo (por exemplo, o total anual de 2025 bloqueado);
4. dependem de uma ação dele ou de terceiros.

As demais decisões não somem: viram um número ("mais N decisões de menor impacto, por tema") e ficam nas notas do slide.

Evidência não é decisão. Uma regra que ganhou dados novos mas segue EM ABERTO aparece como "o que apuramos", nunca como "decidimos".

## Passo 4: montar os slides

Use no máximo 10 slides. A estrutura abaixo é um ponto de partida; corte o que não se aplica ao período.

1. **Capa:** nome do projeto, o período coberto e a data da reunião.
2. **Em uma página:** os totais antes e agora (regras, decididas, em aberto) e três mensagens. O número de decisões do período vem do script.
3. **Decisões por tema (de 2 a 4 slides):** um tema por slide (por exemplo, entrega e fontes, CFEM, indicadores, modelo de dados). O título do slide diz a conclusão ("A entrega dos dados será por API própria"), e os marcadores dizem o que foi decidido, por quê e o que muda. No máximo 4 marcadores de cerca de 18 palavras.
4. **O que contraria o plano anterior:** só se houver. Mostre o que estava escrito, o que foi decidido e quem precisa atualizar o quê.
5. **O que precisa do professor:** cada pergunta em uma linha, com as opções e o que muda com cada uma. Reaproveite a classificação da skill `decidir-regra` (decisão dos mantenedores, do professor ou de fora do grupo). Se existir `docs/perguntas-pendentes.md`, leia-o. Sem isso, use as regras EM ABERTO que dependem do professor.
6. **Em aberto e dependências externas:** o que espera resposta de terceiros (ANM, licenças) e o que falta fazer (por exemplo, criar a conta do Google Cloud). Diga de quem depende cada item.
7. **Próximos passos:** 3 a 5 itens concretos, sem prazos inventados.

Nas notas de cada slide, coloque o detalhe: os IDs das regras (RN-XXX-NN), a data da decisão, o motivo completo e os números que sustentam o slide. O slide mostra a conclusão; as notas respondem à pergunta que o professor fizer.

### Como escrever

- Português do Brasil, com datas absolutas (DD/MM/AAAA, nunca "ontem" nem "semana passada").
- O público é de computação mas não de mineração: defina o termo na primeira vez (CFEM, MSC, proxy, valor real) ou use uma frase de apoio.
- Número no slide vem do script ou da regra. Não arredonde de modo que mude o sentido e não invente porcentagens.
- A fonte registra "DECISÃO-MANTENEDOR" sem dizer qual dos dois mantenedores. Escreva "o mantenedor decidiu" ou "decidimos", e não atribua a decisão a uma pessoa sem o `git log` mostrar quem registrou.
- Diga o que não foi verificado, quando a regra diz isso. Um slide que parece mais certo do que a regra é pior do que um slide cauteloso.
- Visual sóbrio e consistente: um título por slide, pouco texto, nada de tabela com mais de 5 linhas. Prefira o número grande ao parágrafo.

### Gerar o arquivo

Use a skill `anthropic-skills:pptx` para criar o `.pptx` com as notas dos slides. Salve em `output/apresentacoes/reuniao-AAAA-MM-DD.pptx` (a pasta `output/` não é versionada). Depois de gerar, abra ou inspecione o arquivo para conferir que o texto cabe nos slides e que as notas estão presentes, e só então diga que está pronto.

Notas de ambiente, para não perder tempo: o `pptxgenjs` pode não estar instalado (instale com `npm install pptxgenjs` numa pasta de rascunho em `tmp/` e rode o gerador com `NODE_PATH=<pasta>/node_modules`, senão o `apply_theme.js` não o acha), e o `validate.py` precisa de `defusedxml`, `lxml`, `python-pptx` e `Pillow` (sem `pip`, use `uv pip install --target <pasta>/pylibs ...` e `PYTHONPATH=<pasta>/pylibs`). Defina o layout da capa uma única vez: definir dois layouts com o mesmo nome faz os textos caírem fora dos espaços reservados.

Ao entregar, diga ao usuário o caminho do arquivo, quantos slides ficaram, o que ficou de fora e o que você não conseguiu verificar.

## Passo 5: depois da reunião

Pergunte ao usuário o que foi decidido, o que o professor respondeu e o que ficou combinado. Com a confirmação dele:

1. atualize a linha da reunião em `docs/reunioes.md` (situação "realizada", decisões e respostas);
2. se a reunião decidiu uma regra, não altere a regra aqui: encaminhe para a skill `decidir-regra`, citando a reunião como fonte;
3. se a reunião gerou uma pergunta para alguém, registre-a em `docs/perguntas-pendentes.md` (a `decidir-regra` explica o formato).

Não faça commit, branch nem push sem o usuário pedir. A decisão de como versionar é dele.
