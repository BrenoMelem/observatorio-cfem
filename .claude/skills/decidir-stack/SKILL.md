---
name: decidir-stack
description: Analisa o Observatório CFEM (regras de negócio, protótipo em scripts/, ADRs, repositórios irmãos) e conduz o mantenedor, uma decisão técnica por vez, pela escolha da stack de produção e pela organização do desenvolvimento em API e backend, dados e coleta, infraestrutura e processo. Para cada decisão levanta o que as regras exigem, apresenta opções com prós, contras e uma sugestão, pede a escolha e registra um ADR em docs/adr/; depois das decisões, propõe e cria a estrutura inicial do código do produto. Use sempre que o usuário falar em stack, arquitetura, linguagem, framework, banco de dados, hospedagem, agendador, CI, ADR, "como vamos implementar", "por onde começar o desenvolvimento", "organizar o projeto", "estrutura do código", "sair do protótipo" ou "começar o produto", mesmo sem citar o nome da skill.
---

# Decidir a stack e organizar o desenvolvimento

O projeto tem as regras de negócio quase fechadas e um protótipo de laboratório, mas não tem produto. Esta skill faz a ponte: transforma o que as regras exigem em decisões técnicas registradas e, a partir delas, na estrutura inicial do código.

Quem decide é o mantenedor. A skill prepara cada decisão (levanta as restrições, compara opções, sugere) e registra o resultado. Ela não escolhe por ele: uma stack escolhida sem o mantenedor entender o motivo vira dívida, porque é ele quem vai manter o sistema.

O escopo são três áreas: **API e backend**, **dados e coleta**, **infraestrutura e processo**. O front-end fica de fora, salvo quando uma decisão dessas áreas depender dele (por exemplo, o formato de resposta que o site consome).

As regras do `AGENTS.md` valem integralmente: português do Brasil, datas absolutas (DD/MM/AAAA), branch nova a partir da `develop` com PR ao final, nenhuma credencial no repositório.

## Onde cada coisa mora

Essa separação é o que mantém a documentação confiável, então vale entender o motivo:

- `docs/regras-de-negocio/` diz **o quê e por quê**. Escolha de stack nunca entra ali. Se uma decisão técnica mexer numa regra, pare e veja "Quando a decisão esbarra numa regra".
- `docs/adr/` diz **como**, uma decisão por arquivo. É aqui que esta skill escreve. Um ADR cita as regras que o limitam, mas não é fonte de regra de negócio.
- `scripts/` é laboratório. Serve de **evidência** (o que já funcionou, o tamanho dos arquivos, as manhas de cada fonte), não de decisão: o protótipo estar em Python com `uv` não decide a linguagem de produção. O ADR-005 diz isso explicitamente.

## 1. Levantar o terreno

Faça isto no início de cada sessão; o projeto muda entre uma e outra.

Leia, nesta ordem:

1. `docs/adr/` inteiro (o que já foi decidido, proposto ou ficou provisório) e `docs/adr/README.md`, se existir: é o mapa das decisões mantido por esta skill.
2. `docs/regras-de-negocio/README.md` e `pendencias.md` (o que ainda não está decidido nas regras pode travar uma decisão técnica).
3. As regras que impõem requisito técnico. Não leia as 2 mil linhas de uma vez: procure por tema. Em geral pesam `entrega-dos-dados.md` (RN-ENT: quem consome e em que formato), `validacao-e-publicacao.md` (RN-VPU: camadas, trava do último dado bom), `temporalidade-e-atualizacao.md` (RN-TMP: frequência de coleta, versões arquivadas), `modelo-de-dados.md` (RN-MOD: esquema comum) e `regras-por-fonte.md` (RN-FNT: o que cada fonte exige).
4. `scripts/README.md`, `docs/guias/` e `docs/api/openapi.yaml` (o que o protótipo já provou).
5. `docs/regras-de-negocio/divergencias-entre-repositorios.md`: existem os repositórios `obcefem_api` (API e painel já publicados) e `obcefem` (site). A relação do produto com eles é uma decisão em si, e costuma ser a primeira.
6. A seção "Fontes externas" do `AGENTS.md` (limites conhecidos: arquivos de centenas de MB, fontes que exigem conta Google Cloud, chaves por variável de ambiente).

Do que leu, tire as **restrições**: frases curtas, cada uma com o identificador da regra ou o arquivo de onde veio. Por exemplo, "a camada publicada só troca quando o lote novo passa na validação (RN-VPU-03)". Restrição sem origem é opinião sua; marque-a como tal.

Há restrições que não estão em arquivo nenhum e só o mantenedor sabe: quantas pessoas vão desenvolver e o que elas dominam, orçamento de hospedagem, prazo, se há infraestrutura da universidade ou conta de nuvem disponível, quem opera o sistema depois. Pergunte o que faltar antes de comparar opções, de uma vez e em poucas perguntas. O que ele responder vai para a seção "Restrições do mantenedor" do `docs/adr/README.md`, com a data, para não ser perguntado de novo.

## 2. Montar o mapa de decisões

Liste as decisões que faltam, na ordem em que precisam ser tomadas, e grave em `docs/adr/README.md` (crie se não existir; modelo em `assets/README-adr-modelo.md`). O mapa é a parte de "organizar o desenvolvimento": mostra o que está decidido, o que vem a seguir e o que cada decisão destrava.

A ordem importa porque as decisões dependem umas das outras: escolher o framework antes da linguagem, ou a hospedagem antes de saber se há banco, obriga a refazer. Um ponto de partida, que deve ser ajustado ao que o levantamento mostrar:

1. Onde mora o produto e qual a relação com `obcefem_api` (evoluir aquele repositório, construir aqui, repositório novo).
2. Linguagem e ambiente de execução do backend.
3. Armazenamento das camadas (bruto, qualidade, publicado): arquivos, banco embutido, banco gerenciado.
4. Framework e contrato da API.
5. Execução e agendamento das coletas.
6. Hospedagem e segredos.
7. Qualidade e entrega: testes, lint, CI, publicação.
8. Organização do repositório e do fluxo de trabalho.

Junte decisões que só fazem sentido em conjunto e separe as que podem ser trocadas depois sem dor. Não invente decisão para preencher a lista: se o projeto não precisa de fila de mensagens, não há ADR sobre fila.

Mostre o mapa ao mantenedor antes de seguir e deixe que ele reordene, corte ou comece por onde quiser.

## 3. O ciclo de cada decisão

Uma decisão por vez. Só avance quando o ADR estiver registrado ou o mantenedor pedir para adiar. Várias escolhas de stack de uma vez cansam e saem no automático.

### Pesquisar

- Releia as restrições que tocam esta decisão e as decisões anteriores de que ela depende.
- Use o protótipo como medida: tamanho real dos arquivos, tempo de uma coleta, o que quebrou. Se um número decide a comparação e é barato medir, meça (saída fora do repositório).
- Fatos que mudam com o tempo (preço, limites de plano gratuito, tempo máximo de execução de uma plataforma, versão com suporte) não saem da memória: consulte a documentação oficial e anote a data da consulta. Uma recomendação apoiada num plano gratuito que não existe mais é pior que nenhuma.
- Considere de 2 a 4 opções reais, incluindo a mais simples que atende às regras e, quando houver, "continuar com o que o protótipo ou a `obcefem_api` já usa". Descarte logo as que violam uma restrição e diga qual.

### Apresentar

Em linguagem simples e curta; o mantenedor deve conseguir decidir sem abrir arquivo.

- **Decisão:** o que se está escolhendo, numa frase.
- **O que as regras e o contexto exigem:** as restrições que pesam aqui, com o identificador.
- **Opções:** para cada uma, o que é na prática, vantagem, custo (dinheiro, esforço, o que o time precisa aprender) e risco. Diga também o quanto custa voltar atrás.
- **Sugestão:** uma opção, com o motivo ligado às restrições, deixando claro que é sugestão. Na dúvida entre duas, prefira a mais simples e a mais conhecida por quem vai manter: num projeto pequeno, tecnologia sem graça que o time domina vence tecnologia melhor que ninguém opera.
- **O que isso destrava:** as próximas decisões e o trabalho que passa a ser possível.

Depois peça a escolha, com a ferramenta de perguntas quando as opções forem bem delimitadas. Se ele responder com dúvida ou condição ("a 2, mas dá para rodar de graça?"), isso não é decisão: responda, investigue se preciso, e pergunte de novo.

### Confirmar

Antes de gravar, reescreva em uma ou duas frases o que vai para o ADR (a escolha, o que ela fixa, o que fica de fora) e peça um "sim" inequívoco. "Acho que sim", "pode ser" e "faz sentido" não bastam. Não amplie: se ele escolheu o banco, não registre junto a biblioteca de acesso ao banco.

### Registrar

1. **O ADR** em `docs/adr/ADR-NNN-titulo-curto.md`, pelo modelo em `assets/adr-modelo.md`. O número é o seguinte ao maior existente; não reaproveite nem preencha buracos (a numeração começa no ADR-005 por herança). Status `aceito pelo mantenedor em DD/MM/AAAA`. As opções recusadas ficam no ADR com o motivo: é o que evita rediscutir a mesma coisa daqui a seis meses.
2. **O mapa** em `docs/adr/README.md`: marque a decisão como aceita, aponte para o ADR e revise a ordem das que restam.
3. **ADR anterior afetado:** não reescreva. Acrescente uma nota datada no fim dele (como a "Nota de 08/11/2026" do ADR-005) ou marque `substituído pelo ADR-NNN`.
4. **Textos que dizem "ainda não decidido"** sobre o ponto (`README.md`, `docs/README.md`, `AGENTS.md`): procure com `grep -rn` e atualize.

Se ele adiar, o ADR não é criado; a decisão continua no mapa como pendente, com o que faltou para decidir.

## Quando a decisão esbarra numa regra

Às vezes a comparação mostra que uma regra de negócio torna tudo caro, que duas regras pedem coisas incompatíveis ou que falta regra (por exemplo, nenhuma diz por quanto tempo guardar o dado bruto). Não contorne no ADR e não edite a regra por conta própria: diga ao mantenedor qual regra e por quê, e deixe que ele decida se quer tratá-la. Mudança em regra segue o formato de `docs/regras-de-negocio/` e a skill `documentar-pendencias`.

O mesmo vale para o documento DECISÕES, que tem decisões antigas de arquitetura: se o ADR novo contrariar uma delas, registre isso na seção "Contexto" do ADR e não altere o documento de origem.

## 4. Estrutura inicial do código

Só depois que as decisões de que a estrutura depende estiverem aceitas (no mínimo: onde mora o produto, linguagem, armazenamento). Estrutura criada antes disso é chute que alguém vai ter de desfazer.

1. **Proponha antes de criar.** Mostre a árvore de pastas com uma linha por pasta dizendo o que vai nela e qual ADR justifica, as ferramentas de qualidade e o que o CI roda. Peça confirmação.
2. **Crie o mínimo.** Pastas, configuração do projeto, lint, testes, CI e um teste de fumaça que prove que o esqueleto roda. Nada de lógica de negócio, coletor ou rota de verdade: isso é desenvolvimento, e cada parte entra depois, na sua própria branch. Um esqueleto cheio de código de exemplo passa a impressão de que algo já foi implementado.
3. **Separe do laboratório.** O produto não mora em `scripts/` e não importa de lá. O que valer a pena reaproveitar do protótipo será portado depois, de propósito.
4. **Organize pelas responsabilidades das regras** (consumir fontes; validar e publicar; servir), para que quem ler uma regra RN-FNT ou RN-ENT saiba onde ela vai ser implementada.
5. **Atualize os guias de navegação:** `README.md`, `docs/README.md` e a seção "Estrutura" do `AGENTS.md`, que hoje dizem que o produto não existe.
6. Rode os testes e o lint antes de dar por pronto, e relate o resultado como ele saiu.

Se o produto for morar em outro repositório, não crie nada lá sem o mantenedor pedir: entregue a proposta da árvore e registre no ADR.

## Ao encerrar a sessão

Diga em poucas linhas o que foi decidido (com o número do ADR), o que ficou adiado e por quê, e qual é a próxima decisão do mapa. Prepare a branch e o PR para a `develop` conforme o `AGENTS.md`; em geral um PR por decisão, ou um PR para a estrutura inicial.
