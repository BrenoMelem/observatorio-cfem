---
name: documentar-pendencias
description: Conduz o mantenedor, uma pendência por vez, pelas pendências da documentação de regras de negócio do Observatório CFEM (docs/regras-de-negocio/pendencias.md). Para cada uma explica a pendência, o problema e o que ela afeta, lista as decisões possíveis, pede a escolha e registra a decisão nas regras, em pendencias.md e no README. Use sempre que o usuário quiser completar, fechar, destravar ou avançar a documentação inicial, resolver "pendências", "regras em aberto", "EM ABERTO", "próxima pendência", "o que falta decidir", ou disser "vamos documentar", mesmo sem citar o nome da skill.
---

# Documentar pendências, uma de cada vez

O objetivo é completar a documentação inicial do projeto levando o mantenedor a decidir cada ponto em aberto, sem sobrecarregá-lo. Quem decide é o mantenedor; esta skill prepara a decisão (explica, lista opções) e registra o resultado. Ela nunca decide por ele.

Antes de começar, leia `AGENTS.md` e `docs/regras-de-negocio/README.md` (formato das regras, siglas das fontes, legenda de status) e o `glossario.md`. As regras do AGENTS.md valem integralmente. As principais: sem implementação nas regras (nada de código, rotas, bibliotecas), não inventar regra, datas absolutas (DD/MM/AAAA), português do Brasil.

## Fila de pendências

Siga `docs/regras-de-negocio/pendencias.md` nesta ordem:

1. Seção 1: regras com status EM ABERTO.
2. Seção 2: itens em aberto dentro de regras DECIDIDAS.
3. Por último, as regras PROPOSTAS aguardando confirmação (procure com `grep "Status:\*\* PROPOSTA"`), e só se o mantenedor quiser seguir.

As divergências abertas da seção 3 (12, 16, 17) são tratadas junto da regra a que se ligam, não como pendência à parte.

Releia `pendencias.md` no início de cada sessão: a lista muda conforme as decisões são registradas, e uma pendência pode ter sido resolvida por outra. Se o mantenedor apontar uma pendência específica, comece por ela.

## O ciclo de cada pendência

Trate **uma** pendência por vez e só avance quando a decisão estiver registrada ou o mantenedor pedir para adiar. Muitas pendências de uma vez cansam e produzem decisões ruins.

### 1. Pesquisar

Leia a regra no arquivo do tema, as notas de evidência no fim do arquivo, as fontes que ela cita (em `docs/regras-de-negocio/fontes/`) e as regras ligadas (referências cruzadas, mesma divergência). Quando a pendência depender de fato externo (lei, API, portaria, disponibilidade de dado), consulte a web ou faça uma coleta pequena de verificação, anotando a data da consulta. Fato conferido hoje entra com a data de hoje; o que vier só de relatório diz "transcrito do relatório X, não conferido".

Aprendizados de uso:

- **Confira antes de propor opções.** Opções baseadas em premissa não testada saem erradas. Na série do ferro, o "jan/1980" do relatório eram linhas vazias, e só a leitura do dado mostrou isso. Se o dado é público, baixe e compare (por exemplo, o gráfico público do FRED em `fred.stlouisfed.org/graph/fredgraph.csv?id=<série>` dispensa chave; a página do World Bank lista os links do Pink Sheet). Salve os baixados na pasta temporária do job, fora do repositório.
- **Se o mantenedor citar outro repositório** (por exemplo `obcefem_api`), leia o código e o README dele antes de responder. Registre o que veio de lá como "transcrito do README, não conferido neste repositório", salvo se você mesmo reproduzir.
- **Evidência nova pode contradizer uma decisão antiga.** Diga isso de forma direta, mostre os números e proponha reabrir; a decisão antiga fica anotada em Exceções, nunca apagada.

### 2. Apresentar, sempre nesta estrutura

Escreva em linguagem simples, sem jargão desnecessário, e curto. O mantenedor precisa entender sem abrir os arquivos.

- **Pendência:** o identificador (por exemplo RN-CFE-10), o tema e, numa frase, o que falta decidir.
- **O problema:** por que isso está em aberto: o conflito entre fontes, a falta de dado ou a dúvida. Cite fonte e data.
- **O que isso afeta:** quais regras, indicadores, entregas ou outras pendências dependem dessa decisão, e o que acontece se ficar em aberto.
- **Decisões possíveis:** lista numerada de 2 a 4 opções. Para cada uma: o que significa na prática, vantagem, custo ou risco. Se houver opção melhor, marque uma como **sugestão** com o motivo, deixando claro que é sugestão e não decisão. Inclua "adiar" como opção quando fizer sentido, dizendo o que continua travado.

Depois peça a escolha. Use a ferramenta de perguntas (AskUserQuestion) quando as opções forem bem delimitadas; o mantenedor sempre pode responder com outra opção ou pedir mais contexto. Se ele responder com dúvida, esclareça e reapresente em vez de assumir.

- **Pediu explicação mais simples:** reexplique do zero, em frases curtas, com um exemplo do dia a dia ou com números, sem repetir o texto anterior. Depois reapresente a pergunta.
- **Escolheu uma opção, mas com condição** ("opção 1, mas antes me diga como X trata isso", "mas teria como automatizar?"): não é decisão. Responda a condição (investigue, se preciso), diga o que isso muda nas opções e pergunte de novo.
- **Número ou exemplo seu** (por exemplo "N = 10") deve vir marcado como exemplo seu e não como valor de fonte.

### 3. Confirmar a decisão

Antes de editar qualquer arquivo, confirme explicitamente. Já aconteceu de a skill registrar como decisão algo que o mantenedor não tinha deixado claro, e uma decisão registrada errada contamina regras, totais e o histórico. Respostas como "acho que a 2", "faz sentido", "pode ser", uma pergunta, um comentário sobre uma opção ou uma escolha parcial (só parte das perguntas respondidas) **não** são decisão.

Reescreva em uma ou duas frases o que vai ser registrado (a opção, os detalhes que ela fixa, o status resultante e as regras que mudam) e pergunte se ele decide isso. Use a ferramenta de perguntas com opções como "Sim, registrar", "Ajustar" e "Ainda não decidi". Só siga para o registro com um "sim" inequívoco. Se ele ajustar, reescreva e confirme de novo; se não decidiu, trate como adiamento ou volte às opções.

Também não amplie a decisão: registre só o que ele confirmou. Se a decisão deixar um detalhe solto (um valor, uma data, um recorte), pergunte em vez de preencher.

### 4. Registrar a decisão

Só depois da confirmação. Siga o AGENTS.md, na mesma alteração:

1. **A regra** no arquivo do tema: status `DECIDIDA` com a fonte `DECISÃO-MANTENEDOR` e a data absoluta (hoje), a decisão em si e o campo Exceções se ela contrariar um documento de origem. Se ele escolher adiar, mantenha o status e registre apenas o que for evidência nova em "Notas de evidência".
2. **`pendencias.md`:** remova a linha da seção 1 ou o ponto da seção 2, e ajuste divergências e referências cruzadas. Se a decisão resolver uma divergência (12, 16, 17), atualize a situação dela.
3. **`README.md`:** o total de regras por status.
4. **Outras regras** que ainda dizem "em aberto" sobre o mesmo ponto.
5. **Título e referências:** se a decisão muda o escopo da regra, ajuste o título (por exemplo, "só antes de 1980" passou a "de 1985 a 1991") e procure o texto antigo em todos os arquivos (`grep -rn`) para não deixar frases desatualizadas em tabelas de períodos e em outras regras.

Não reescreva os documentos em `fontes/`. Não escreva implementação nas regras. Se a escolha do mantenedor exigir um texto que você não sabe redigir sem inventar, pergunte.

Confira os totais antes de dar a pendência por encerrada:

```
cd docs/regras-de-negocio
grep -h "^- \*\*Status:\*\* DECIDIDA" *.md | wc -l
grep -h "^- \*\*Status:\*\* PROPOSTA" *.md | wc -l
grep -h "^- \*\*Status:\*\* EM ABERTO" *.md | wc -l
grep -n "Total:" README.md
```

O README tem um exemplo de regra com título `### RN-`, então a contagem de títulos fica 1 acima do número de regras.

### 5. Fechar e seguir

Faça o commit da decisão (seção Git, abaixo). Depois resuma em duas ou três linhas o que foi registrado, em quais arquivos e o hash do commit, informe quantas pendências restam nas seções 1 e 2 e apresente a próxima, repetindo o ciclo. Quando o mantenedor disser que quer parar, entregue o resumo das decisões da sessão.

## Git

Todo o trabalho vai numa branch nova criada a partir da `develop`, com um PR para a `develop` ao final (AGENTS.md). Antes da primeira edição, confira a branch atual: se for `develop`, `main` ou uma branch que não saiu da `develop`, avise e pergunte antes de editar.

**Um commit por decisão.** Cada vez que o mantenedor decidir algo e o registro estiver completo (regra, `pendencias.md`, README, regras ligadas, totais conferidos), faça um commit só com os arquivos dessa decisão. O mantenedor pediu isso para poder revisar e, se preciso, reverter cada decisão isoladamente; por isso não junte duas decisões no mesmo commit nem deixe a decisão sem commit ao passar para a próxima pendência.

- Adicione os arquivos pelo nome (`git add <arquivos>`), nunca `git add -A`: há arquivos não versionados no repositório que não fazem parte da decisão.
- Mensagem no padrão do repositório, em português: `docs(<ID da regra>): <o que foi decidido>`, por exemplo `docs(RN-MOD-24): decide a data-base do valor real (dez/2025)`. No corpo, uma ou duas linhas com a decisão, a data e a fonte DECISÃO-MANTENEDOR. Termine com a linha de coautoria indicada pela sessão, se houver.
- Se o mantenedor escolher adiar e só entrar nota de evidência, faça o commit também (`docs(<ID>): registra evidência, segue em aberto`). Se nada mudou nos arquivos, não há commit.
- Se o `uv run pytest` ou algum hook falhar, mostre o erro e pergunte; não contorne com `--no-verify`.

- **Confira a branch antes de cada commit** (`git branch --show-current`). Outra sessão ou o próprio mantenedor pode trocar a branch com o repositório em uso; já aconteceu de a sessão cair na `develop` no meio do trabalho. Se não estiver na branch de trabalho, volte a ela (sem perder nada) antes de editar e de commitar.
- **Alterações que já estavam no working tree antes da sessão** (de outra tarefa) não são suas. Avise e pergunte se entram; se for preciso commitá-las para manter os totais consistentes, faça um commit à parte, antes das decisões, e diga isso no relatório. Quando duas decisões mexem nas mesmas linhas, monte o estado de cada commit (aplicando só as mudanças daquela decisão sobre o commit anterior) e confira que o último estado é idêntico ao arquivo final.
- **Reabrir uma decisão já commitada:** faça um novo commit que a corrija (`docs(<ID>): revisa ...`), sem `--amend` nem reescrever histórico, salvo se o mantenedor pedir.
- **"Traga a develop para a branch":** `git fetch`, depois `git merge develop` na branch de trabalho (merge, não rebase, para não reescrever commits). Se houver conflito, mostre e pergunte.

Push e PR só quando o mantenedor pedir; ao final da sessão, ofereça. Nunca faça push direto na `develop` nem na `main`.
