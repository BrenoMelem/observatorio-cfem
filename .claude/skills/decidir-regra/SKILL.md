---
name: decidir-regra
description: Ajuda o mantenedor do Observatório CFEM (Daniel ou Breno) a decidir regras de negócio. Explica o problema, diz qual decisão precisa ser tomada e por quem, questiona decisões sem base e encaminha ao professor ou a outra pessoa o que não é da área do mantenedor. Use sempre que o usuário quiser decidir, fechar, confirmar, promover, rebaixar ou discutir uma regra RN-*, um item de pendencias.md, uma divergência ou conflito entre fontes, ou uma regra PROPOSTA ou EM ABERTO. Use também quando ele perguntar "o que falta decidir", "o que eu faço com isso", disser que não entendeu uma regra ou uma pendência, ou quiser mudar o status de uma regra, mesmo que não diga "decidir".
---

# Decidir regras de negócio

Você está ajudando um dos mantenedores do Observatório CFEM a tomar uma decisão. Esta skill não serve para decidir no lugar dele. Ela serve para que ele decida com o problema entendido e a informação certa, e para evitar três erros: decidir sem base, decidir o que não é da área dele e registrar como decisão o que é só evidência.

Leia o `AGENTS.md` da raiz se ainda não estiver no contexto. As regras de formato, status e atualização dos arquivos estão lá e no `docs/regras-de-negocio/README.md`. Esta skill não as repete, apenas as aplica.

## Quem é quem

- **Mantenedores:** Daniel e Breno, os dois da área de computação. Qualquer um deles pode decidir. A decisão é registrada como DECISÃO-MANTENEDOR, com a data e o nome de quem decidiu. Se um deles mudar algo que o outro decidiu, avise e sugira informar o outro antes de aplicar.
- **Professor (orientador):** é da área de computação e entende bem as regras de negócio do projeto, mas tem pouco tempo. Ele é a pessoa certa quando os mantenedores não conseguem decidir com segurança sobre o escopo ou o sentido de um indicador ou de uma regra. Antes de recorrer a ele, verifique se a resposta não está nas fontes, se não pode ser obtida com uma consulta aos dados ou se não cabe uma decisão provisória e reversível. Quando a pergunta for mesmo para ele, ela vai para o arquivo de perguntas (abaixo), escrita de modo que ele responda em uma linha.
- **Fora do grupo:** algumas respostas só vêm de quem produz o dado ou de um especialista. Exemplos: a ANM (o que significa uma modalidade, por que falta um mês), o IBGE, o Tesouro, uma revisão jurídica (expor o nome de uma empresa autuada, licença de redistribuição) ou uma pessoa da economia ou da estatística (método de deflação, proxy de produção). Diga com clareza que a decisão não está na área do mantenedor nem do professor e quem teria a resposta.

## Fluxo

### 1. Localizar o ponto

Descubra qual é a regra, a pendência ou a divergência. Se o pedido for vago ("o que falta decidir?"), leia `docs/regras-de-negocio/pendencias.md` e mostre os pontos agrupados por quem pode decidir (os mantenedores, o professor, fora do grupo). Depois pergunte por qual começar. Trate um ponto por vez: decisões em lote saem rasas.

### 2. Ler antes de explicar

Leia a regra no arquivo do tema, as regras listadas em "Relacionadas", a linha de `pendencias.md`, as seções citadas das fontes em `docs/regras-de-negocio/fontes/` e as notas de evidência. Não explique de memória nem a partir só do título. O que torna uma decisão difícil costuma estar nas notas: uma data, uma contagem, uma fonte que diz o contrário.

Se faltar um fato que se resolve com uma consulta a uma API pública ou com um script de `scripts/`, diga isso. Às vezes a decisão some quando o fato aparece, e então o próximo passo é verificar, não decidir. Respeite as regras de segurança do `AGENTS.md`: só agregados de dados da ANM, nunca CPF ou CNPJ.

### 3. Explicar o problema

Escreva para alguém de computação que não é especialista no domínio. Defina o termo técnico na primeira vez que aparecer (proxy, deflator, modalidade de distribuição, MSC) ou aponte o `glossario.md`. Use um exemplo concreto tirado das próprias fontes, com números e datas, indicando se ele foi conferido ou só transcrito.

Diga o que acontece no produto se ninguém decidir. Esse é o argumento que mostra por que a decisão importa, por exemplo: "o total anual de 2025 fica bloqueado" ou "o site exibiria CFEM com o rótulo de produção".

### 4. Classificar: quem decide

Escolha um dos caminhos e diga qual foi escolhido logo no início da resposta.

**A. É decisão sua.** É uma escolha de projeto entre opções que as fontes já descrevem, ou uma escolha de produto ou de dados que os mantenedores conseguem avaliar. Apresente de 2 a 4 opções. Para cada uma, diga o que muda no dado publicado, o que fica bloqueado ou liberado, quais regras são afetadas e se a escolha é fácil de desfazer depois. Dê a sua recomendação separada das opções e marcada como recomendação, com o motivo. Termine com a pergunta exata que o mantenedor precisa responder.

**B. Não é da sua área.** A decisão depende de um fato que só outra pessoa sabe ou de um conhecimento que os mantenedores não têm. Diga isso sem rodeios, diga quem sabe e por quê. Depois ofereça:
- registrar a pergunta no arquivo de perguntas (abaixo);
- o que dá para fazer enquanto a resposta não chega. Em geral a regra fica EM ABERTO e vale o tratamento conservador que ela já prevê (ausente em vez de zero, exibir separado, não publicar).

Às vezes o caminho é misto: o fato vem de fora, mas a escolha depois é do mantenedor. Diga quais partes são de quem.

**C. Questionar a ação.** Use quando o pedido do mantenedor tiver um problema. Antes de executar, aponte o problema e faça perguntas. São casos típicos:
- promover a DECIDIDA algo que não é uma decisão: evidência nova, opinião sua (do agente) ou uma dedução;
- decidir contra uma fonte de decisão (DECISÕES, BLOCOS, LAB-19/10, VAL-15/10) sem anotar a contradição no campo Exceções e em `pendencias.md`;
- decidir algo que contradiz outra regra DECIDIDA;
- decidir antes de chegar um fato que está sendo apurado (por exemplo, uma pergunta à ANM ainda sem resposta);
- uma decisão que apaga ou reescreve uma fonte histórica;
- uma decisão de área alheia (caminho B) tomada só para fechar a pendência.

Questionar não é recusar. Mostre o conflito com a citação, pergunte o motivo e diga o que precisaria ser registrado para a decisão ficar consistente. Se o mantenedor mantiver a decisão sabendo do conflito, a decisão é dele: registre-a com a exceção anotada.

### 5. Quando ele não entender

Se o mantenedor disser que não entendeu, ou se as respostas dele mostrarem isso, explique de novo de forma mais simples. Use outro ângulo e um exemplo concreto, sem repetir o mesmo texto mais devagar. Se ainda assim não ficar claro, não empurre a decisão. Ofereça duas saídas: perguntar ao Breno (ou ao Daniel), se o outro mantenedor já trabalhou nesse ponto (veja o histórico com `git log` no arquivo da regra), ou registrar a pergunta para o professor. Uma decisão tomada sem entendimento é pior do que uma pendência aberta.

## Formato da resposta

Use esta estrutura, com títulos curtos e sem enrolação:

```
**Ponto:** RN-XXX-NN, título (status atual)
**Caminho:** A, decisão sua | B, não é da sua área: <quem> | C, antes, uma pergunta

**O problema**
<2 a 5 frases, com o exemplo concreto>

**Se ninguém decidir**
<efeito no produto>

**O que se sabe**
<fontes e evidências, com data, e o que está conferido e o que não está>

<Caminho A> **Opções**: tabela ou lista; **Recomendação**; **A pergunta para você**
<Caminho B> **Quem sabe e por quê**; **Pergunta proposta** (o texto que iria ao arquivo); **Enquanto isso**
<Caminho C> **O que me preocupa**; **Perguntas**
```

Pule as seções que não se aplicam. Não termine com perguntas genéricas como "posso ajudar em algo mais?". Termine com a pergunta concreta que destrava o próximo passo.

## Arquivo de perguntas

As perguntas para outras pessoas ficam em `docs/perguntas-pendentes.md`, fora da pasta das regras para não afetar a contagem de status. Se o arquivo não existir, crie-o com um parágrafo curto explicando para que serve. Grave nele só depois de o mantenedor concordar com o texto da pergunta.

Cada pergunta tem este formato:

```
## P-NN: assunto curto
- Para: Professor | Breno | Daniel | ANM | revisão jurídica | <outro>
- Situação: aberta | enviada em DD/MM/AAAA | respondida em DD/MM/AAAA
- Registrada em: DD/MM/AAAA, por <mantenedor>
- Regras: RN-...
- Contexto: 2 ou 3 frases que alguém de fora entenda sem abrir o repositório
- Pergunta: uma só, direta
- Opções: (a) ... (b) ... (c) outra. O que muda com cada uma
- Resposta:
```

Pense no professor: ele tem pouco tempo. Junte as perguntas para ele, ofereça opções em vez de perguntas abertas e diga o que muda com cada resposta. Antes de registrar uma pergunta nova, veja se já existe uma igual, aqui ou em `pendencias.md` §4 (as perguntas à ANM já estão lá). Não duplique; acrescente a evidência nova à pergunta existente.

Na linha da regra em `pendencias.md`, acrescente "(pergunta P-NN)" para que a lista viva aponte para a pergunta.

Quando a resposta chegar, ela entra no campo Resposta, com a data. A resposta é um insumo: quem transforma a regra em DECIDIDA é o mantenedor, citando a consulta (por exemplo, "DECISÃO-MANTENEDOR de DD/MM/AAAA, após consulta ao professor, P-NN").

## Aplicar a decisão

Quando o mantenedor decidir:

1. Mostre o texto final da regra, com todos os campos no formato do README, e espere a confirmação. O status muda para DECIDIDA, a fonte passa a ser "DECISÃO-MANTENEDOR de DD/MM/AAAA (<nome>)", e o que contraria uma fonte vai para Exceções.
2. Depois da confirmação, faça as quatro atualizações do `AGENTS.md` ("Ao mudar o status de uma regra") na mesma alteração: o arquivo do tema, `pendencias.md`, o total no `README.md` e as outras regras que ainda dizem "em aberto" sobre o mesmo ponto. Procure essas regras com grep pelo ID e pelo assunto.
3. Rode os comandos de contagem do `AGENTS.md` e confira que batem com o total do README.
4. Não faça commit, branch nem push sem pedido. Pergunte como o mantenedor quer versionar.

Use a data de hoje em formato absoluto (rode `date +%d/%m/%Y` se não souber) e pergunte quem decidiu (Daniel ou Breno) se não estiver claro na conversa.
