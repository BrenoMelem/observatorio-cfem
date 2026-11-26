---
name: adicionar-fonte
description: Leva uma fonte de dados do Observatório CFEM (SICONFI, IBGE, ANM, Pink Sheet, SEEG etc.) do laboratório ou do zero até a publicação no produto (backend/), conduzindo o mantenedor, uma pendência por vez, pelas decisões que travam a publicação (referência independente, tolerância, período incompleto, ausências, repetições, arquivamento, agenda). Para cada pendência explica o problema, o que ela afeta, as opções com prós, contras e como cada uma seria implementada, pede a escolha, confirma e registra; depois implementa, executa de verdade, documenta e publica (branch, PR, workflow agendado). Use sempre que o usuário quiser adicionar, portar, implementar, colocar no pipeline ou publicar uma fonte ou um indicador, "levar X para o produto", "próxima fonte", "pipeline do SICONFI/IBGE/...", ou resolver o que falta para uma fonte ir para a API, mesmo sem citar o nome da skill.
---

# Adicionar uma fonte ao pipeline

O objetivo é que uma fonte saia de "existe no laboratório" (ou de "não existe") para "publicada na API, com coleta agendada", e que cada decisão do caminho seja do mantenedor, explicada e registrada. O código é a parte previsível. O que trava uma fonte são decisões: qual publicação independente a confere, o que fazer com período incompleto, se ausência é lacuna ou zero, quem revisa uma referência nova. Esta skill prepara cada decisão (problema, impacto, opções, como implementar), pede a escolha e só então implementa. Ela nunca decide pelo mantenedor.

Antes de começar, leia `AGENTS.md` (valem integralmente: português do Brasil, datas absolutas, não inventar regra, padrões do ADR-017, fluxo de branches), `docs/regras-de-negocio/README.md` e o `glossario.md`. A fatia da arrecadação da CFEM é o exemplo completo de uma fonte publicada; use-a como modelo, sem copiar o que é particular dela.

## Mapa do que já existe

O padrão de uma fonte (fonte → modelo → validação → publicação → API) e o mapa dos arquivos estão em `docs/guias/padrao-de-pipeline-de-fonte.md`; a fatia da CFEM de ponta a ponta, em `docs/guias/pipeline-cfem.md`; o contrato entre camadas, em `docs/adr/pendencias-implementacao-adr-017-018.md`; o laboratório, em `scripts/README.md`. Não repita caminhos aqui: leia esses guias e confira o código. Três pontos não estão nos guias:

- Manifesto de indicadores: `data/indicadores.json` (RN-MOD-25); dimensões da API: `DIMENSOES`, `MOTIVOS` e `LACUNAS` em `backend/src/observatorio/api/services/dimensoes.py`.
- Contrato da API para o front: `docs/api/openapi-producao.yaml`, regravado com `uv run pytest tests/api/test_openapi.py --atualizar-openapi` em `backend/`.
- Workflows de referência: `coletar-siconfi.yml` (coleta de uma fonte que publica o parcial `fonte-<fonte>-*`), `publicar-pacote.yml` (monta o pacote), `coletar-cfem.yml`, `arquivar-anm.yml` e `atualizar-referencias-anm.yml`.

**Peças já generalizadas pelo SICONFI** (25 e 26/11/2026; confira antes de planejar, porque podem ter mudado): `publicar()` aceita qualquer indicador do manifesto, `coleta.py` tem um subcomando por fonte (`cfem`, `siconfi`) e `montar`, e a API confere `Decimal(38, 2)` em todo indicador monetário. Uma fonte nova acrescenta o seu subcomando e entra na lista do `publicar-pacote.yml`.

## Fase 1: diagnóstico da fonte

Se o mantenedor não disse qual fonte ou qual recorte, pergunte. Ajuda listar candidatos com o que cada um destrava no `docs/produto/backlog.md` (prazo e prioridade) e na RN-ENT-12 (composição das dimensões). Uma fonte grande (SICONFI) costuma ter vários indicadores: proponha começar pelo recorte mais bem definido nas regras e deixe os outros para depois.

Leia, sem pular:

1. As regras da fonte: `grep -rn "<sigla ou nome da fonte>" docs/regras-de-negocio/*.md`, em especial RN-FNT, RN-FON, RN-TMP, as regras do tema (RN-CFE, RN-IND) e as **notas de evidência** no fim de cada arquivo.
2. `pendencias.md` (seções 1, 2, 4 e 6) e os conflitos com o backlog que tocam a fonte.
3. O código do laboratório da fonte e os testes dele em `scripts/testes/`.
4. A entrada da fonte no manifesto (`data/indicadores.json`): o campo `limitacoes` costuma dizer o que falta ("reconciliação independente pendente").
5. Registros anteriores em `docs/registros/` sobre a fonte.

Quando faltar informação (a fonte responde? cobre os 12 municípios? dois números batem?), não suponha: escreva um script de teste pequeno em `scripts/sondas/<fonte>.py` ou `scripts/<tema>/`, rode e use o resultado, como descreve a seção "Quando faltar informação" da skill `documentar-pendencias`. Dado baixado vai para `tmp/` ou `output/`.

**Piloto com dado real, ainda aqui.** Antes de fechar a lista de pendências, baixe um recorte real (2 ou 3 municípios, alguns anos) e rode a leitura e a conferência de ponta a ponta, mesmo com script provisório. Os casos que só o dado real mostra (linha sem a dimensão esperada, município ausente, total que não fecha) viram pendências já na ficha, em vez de reprovar a primeira coleta completa. Registre a taxa de cobertura do piloto (quanto passaria na conferência) e mostre-a ao mantenedor.

Entregue ao mantenedor uma **ficha da fonte**, curta:

- **O que já está decidido** (com o RN-xxx de cada ponto).
- **O que está pronto para portar** do laboratório e o que precisa ser escrito.
- **As pendências que travam a publicação**, na ordem em que vai tratá-las.

Para montar a lista de pendências, passe por este roteiro e inclua cada item que as regras não respondem:

| Pergunta | Regras | Por que trava |
| --- | --- | --- |
| Qual publicação **independente** confere a fonte? | RN-VPU-07 | Sem referência, nada é homologado; a fonte pode ser coletada, mas não publicada |
| Qual a tolerância da conferência? | RN-VPU-12 (zero centavos) | Uma tolerância percentual esconde erro em valor alto |
| Como tratar período incompleto e o período corrente? | RN-CFE-05, RN-CFE-06 (modelo) | Publicar mês ou ano incompleto mostra queda que não existe |
| Ausência é lacuna ou zero? Como distinguir? | RN-MOD-10, RN-MOD-12, RN-CFE-07 | Zero inventado é erro de conteúdo |
| Há linhas repetidas ou retificações? O que fazer com elas? | RN-VPU-11 | Somar ou descartar muda o total |
| O bruto vai para Release? | RN-TMP-18, ADR-011 | Sem arquivo, a coleta não é reproduzível quando a fonte muda |
| Qual a agenda de coleta? | RN-TMP-01, RN-TMP-02 | Define o workflow |
| Unidade, moeda, decimal, chave do município | RN-MOD, RN-TER, RN-CFE-11 | Contrato do modelo comum |
| Em qual dimensão e com qual identificador entra? | RN-ENT-12, RN-MOD-25 | Define o manifesto e a rota da API |

## Fase 2: uma pendência por vez

Trate **uma** pendência por vez; só avance quando a decisão estiver registrada ou o mantenedor pedir para adiar.

### Apresentar, sempre nesta estrutura

Linguagem simples e curta; o mantenedor precisa entender sem abrir os arquivos.

- **Pendência:** o tema e, numa frase, o que falta decidir.
- **O problema:** de onde ele vem (conflito entre fontes, falta de dado, dúvida), com fonte e data. Se você mediu algo, mostre os números.
- **O que afeta:** indicadores, itens do backlog com prazo, outras regras, e o que fica travado se adiar.
- **Opções (2 a 4).** Para cada uma: o que significa na prática; vantagem; custo ou risco; e **como seria implementada**: em qual camada (`fontes/`, `validacao/`, `publicacao/`, `api/`, workflow), o que muda no código, que teste prova, e se contraria alguma regra DECIDIDA. Marque uma como **sugestão**, com o motivo, deixando claro que é sugestão. Inclua "adiar" quando fizer sentido.

Peça a escolha com a ferramenta de perguntas (AskUserQuestion) quando as opções forem bem delimitadas. Cada pergunta deve se sustentar sozinha: o mantenedor pode ver só a caixa de diálogo.

- **Se uma opção escolhida contrariar uma regra DECIDIDA, pare e mostre o conflito** antes de implementar. Exemplo real: a RN-CFE-06 diz que meses de ano aberto saem "provisórios"; publicar como "validado" exigiria uma exceção registrada na regra.
- **Se uma descoberta mudar uma resposta já dada, diga e pergunte de novo.** Exemplo real: o mantenedor escolheu "incluir os meses fechados do ano corrente", mas o arquivo mostrou que julho a outubro, já fechados no calendário, tinham menos de 25% dos registros normais; foi preciso uma segunda pergunta.
- Escolha com condição ("a 1, mas antes me diga X") não é decisão: responda a condição e pergunte de novo.

### Cobertura baixa da conferência

Se a referência barrar uma parte grande do que a fonte traz (por exemplo, menos da metade dos itens publicáveis), isso é uma pendência própria, não um detalhe do relatório. Antes de publicar: meça a cobertura por ano e por município, investigue a causa das divergências mais frequentes (limite real da fonte ou casamento de linhas frágil no nosso código? teste uma amostra à mão), mostre os números ao mantenedor e pergunte se publica assim, se melhora o casamento ou se adia. Na seção "O que continua pendente" do registro, diga a cobertura e as causas ainda não investigadas.

### Escolhas de implementação sem regra por trás

Quando o código precisar de uma escolha que nenhuma regra nem o mantenedor decidiu (encadear workflows, grupo de concorrência, formato de captura), não a deixe só como aviso no PR: faça uma pergunta curta ao mantenedor (opções, sugestão, impacto) e registre a resposta. Se ele pedir para seguir sem decidir, marque no PR como "escolha a revisar".

### Confirmar e registrar

Antes de editar, reescreva em uma ou duas frases o que vai ser registrado e confirme ("Sim, registrar" / "Ajustar" / "Ainda não decidi"). "Acho que a 2", "faz sentido" ou uma pergunta não são decisão. Registre só o que foi confirmado.

Onde registrar depende do tipo de decisão:

- **Decisão de regra** (muda o quê e o porquê: status, exceção, período, tratamento de ausência): siga integralmente a seção "Registrar a decisão" da skill `documentar-pendencias` (a regra no arquivo do tema, `pendencias.md`, o total no `README.md` das regras, as outras regras que dizem "em aberto", a conferência dos totais). Nada de código nas regras.
- **Decisão de implementação** (como aplicar uma regra: onde mora o código, frequência do workflow, formato das capturas, fluxo de revisão): vai para o registro datado da fonte em `docs/registros/` (seção "Decisões do mantenedor nesta data") e, se mudar uma decisão técnica, uma nota datada no ADR correspondente.
- **Evidência nova que não decide nada:** nota de evidência sob a regra, com a data e o comando que a reproduz; a regra só ganha um ponteiro.

## Fase 3: implementar

Siga `docs/guias/padrao-de-pipeline-de-fonte.md` e o `AGENTS.md`. Em resumo:

- **`fontes/<fonte>.py`:** baixa e preserva o bruto, registra URL, data, SHA-256 e filtros (RN-FON-13, RN-FON-14), confere as colunas esperadas e falha de forma explícita em layout novo (RN-VPU-04). Dinheiro em `Decimal`; latin-1 convertido para UTF-8 antes do polars; ausente nunca vira zero. Não aprova nem publica.
- **Referência independente:** se ela for uma página ou arquivo oficial, guarde o corpo original (comprimido) e registre o SHA-256 do conteúdo, não do arquivo comprimido. Se a fonte da referência muda a cada requisição (HTML com estado, data no rodapé), compare os **valores extraídos** e só regrave a captura quando eles mudarem; senão toda execução parece mudança.
- **`validacao/`:** conferência com a referência, relatório completo do lote (RN-VPU-06). Um item que não pode ser publicado por motivo esperado (período incompleto, mês ainda sendo lançado) fica fora e vai para o relatório; não reprove o lote inteiro por isso sem decisão do mantenedor.
- **`publicacao/` e `coleta.py`:** generalize para o indicador novo em vez de duplicar o caminho da CFEM. A troca do ponteiro continua sendo o último passo; reprovação conserva a versão anterior (RN-VPU-03).
- **API:** acrescente o identificador ao manifesto e a `DIMENSOES`, ajuste `MOTIVOS`/`LACUNAS` e regrave o `openapi-producao.yaml`. `api/` nunca importa `fontes/`, `validacao/` nem `publicacao/` (conferido pelo `lint-imports`).
- **Testes:** cada fonte tem um teste com um **recorte pequeno do arquivo ou da página real** em `backend/tests/fixtures/` e a lista das colunas esperadas; cada regra implementada é citada (RN-xxx) na docstring do código e na do teste. Teste também o caminho de falha: layout alterado, lote reprovado que preserva o pacote anterior.

Conferências, de dentro de `backend/`: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run lint-imports`, `uv run pytest`. Da raiz, o laboratório: `uv run ruff check scripts` e `uv run pytest` (inclui a conferência dos totais das regras).

## Fase 4: executar de verdade

Rode a coleta com o dado real (da Release, quando houver), suba a API e confira as rotas, o CSV e o Swagger. Mostre ao mantenedor os números que importam (linhas, recorte, conferidos, fora da publicação e por quê) e compare com a referência oficial em pelo menos um caso que ele reconheça. Registre a execução em `docs/registros/<fonte>-AAAA-MM-DD.md`: entrada (origem, edição, SHA-256), comando, resultado, decisões da data, o que não foi verificado e o que continua pendente. `registros/` só recebe acréscimos: não reescreva retratos antigos.

## Fase 5: documentar e publicar

- **Documentação:** guia da fonte em `docs/guias/` (ou seção no guia do pipeline), `backend/README.md`, manifesto (`limitacoes` sem números que mudam a cada edição), `openapi-producao.yaml`, `AGENTS.md` se a situação do produto mudou, e o `scripts/README.md` se tocou no laboratório.
- **Workflow:** uma coleta agendada na agenda da fonte (RN-TMP-02), que só trabalha quando há edição nova, publica o pacote parcial aprovado numa Release `fonte-<fonte>-*` (ADR-015), chama `publicar-pacote.yml` por `workflow_call` e abre ou comenta uma issue na falha (ADR-011). Copie a estrutura de `coletar-siconfi.yml`. Antes do PR, valide a sintaxe (`actionlint`, se houver). O melhor teste, validado em 25/11/2026, é rodar de verdade numa **branch temporária** (peça autorização antes: cria Releases no repositório): crie `teste/<assunto>` a partir da branch do PR, acrescente `push: branches: ["teste/<assunto>"]` em `on:` dos workflows que quer exercitar (só nessa branch), faça push e acompanhe com `gh run list --branch` e `gh run view`. Um `push` roda o arquivo da própria branch, ao contrário de `schedule` e `workflow_dispatch`, que só valem na padrão; assim também o `workflow_call` entre arquivos roda de verdade. Depois confira o resultado (por exemplo, baixe a Release e leia o `pacote.json`), apague as Releases de teste com `gh release delete <tag> --cleanup-tag -y`, apague a branch remota e confirme que a Latest e as issues voltaram ao que eram (guarde a lista antes: `gh release list --json tagName,isLatest`). O `act` só é útil com o daemon do Docker ativo e, na simulação seca (`-n`), valida só a sintaxe e a ordem dos passos; rodar de verdade com ele usaria o `GH_TOKEN` e escreveria no repositório real. Release de workflow nunca deve ser `--latest=true`: a Latest é a da `anm-*`.
- **Tamanho do PR:** se a fonte exigir mudar peças comuns (modelo, publicação, `coleta.py`, API) e a mudança for grande, proponha um PR só para isso e outro para a fonte, empilhados (ver a regra de PRs separados ou empilhados). Recorte as fixtures ao mínimo que o teste precisa (poucos municípios e anos) e descreva no README da pasta como foram recortadas.
- **Git:** branch nova a partir da `develop`, commits por assunto (decisão de regra num commit próprio, como na `documentar-pendencias`), PR para a `develop` com resumo, decisões do mantenedor, como foi conferido e o que **não** foi verificado. Push, merge e PR para a `main` só quando o mantenedor pedir.

## Armadilhas já encontradas

- **Mês fechado no calendário não é mês completo na fonte.** A ANM lança registros com meses de atraso; use o critério de volume da RN-CFE-06 (ou um equivalente decidido para a fonte), não o calendário.
- **Release criada por workflow com o `GITHUB_TOKEN` não dispara outro workflow** (só `workflow_dispatch` e `repository_dispatch` são exceção). Encadeie por agenda ou por `workflow_call` (como `coletar-*.yml` → `publicar-pacote.yml`), não pelo evento da Release.
- **`schedule` e `workflow_dispatch` só valem a partir da `main`.** Antes do merge, teste o workflow de verdade numa branch temporária com gatilho `push` (ver a Fase 5) ou, sem autorização para isso, simule os passos localmente e diga isso no PR. Depois do merge, dispare a primeira execução à mão (com autorização) e acompanhe.
- **PR aberto por workflow não roda o CI sozinho:** alguém com acesso de escrita aprova na página do PR.
- **Shell padrão do Actions sem `pipefail`:** um `| tee` esconde a falha do comando; use `set -o pipefail`.
- **Servidor da ANM:** exige User-Agent de navegador, recusa HEAD e tem cadeia TLS incompleta (`OBS_ANM_CA=scripts/cfem/certificados/sectigo-ov-r36.pem`; nunca desligue a verificação).
- **Uma API em execução não recarrega o código.** Depois de mudar `api/` ou a validação de leitura do pacote, reinicie o processo (e reconstrua a imagem Docker), senão o pacote novo aparece como inválido (503).
- **Segunda fonte pode apagar a primeira.** Se a coleta de uma fonte parte do último pacote *dela*, o pacote novo perde os indicadores das outras. Decisão do mantenedor de 25/11/2026: cada fonte publica só o seu pacote parcial (Release `fonte-<fonte>-*`, partindo do parcial anterior dela) e o workflow `publicar-pacote.yml`, chamado por `workflow_call` ao fim de uma coleta aprovada, monta o pacote da API juntando o último parcial de cada fonte. Uma fonte nova copia `coletar-siconfi.yml` e entra na lista de fontes do `publicar-pacote.yml`.
- **Linha sem a dimensão esperada não é layout novo.** A MSC trouxe uma linha sem função no meio de milhares completas. Reprovar o lote inteiro por isso foi erro; o certo é tirar da publicação só a unidade afetada, com o motivo no relatório. Reserve a reprovação do lote para mudança de colunas (RN-VPU-04).
- **`git mv` fica no índice:** um `git add` de outros arquivos leva junto o que já estava preparado; confira `git status` antes de cada commit.

## Ao terminar

Resuma ao mantenedor: o que foi publicado (indicadores, período, quantos conferidos), as decisões registradas e onde, os commits e o PR, o que não foi verificado e as pendências que continuam abertas (inclusive as que dependem de outras pessoas). Se a fonte ensinou algo que esta skill não diz, proponha acrescentar à seção de armadilhas.
