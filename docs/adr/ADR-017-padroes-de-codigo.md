# ADR-017 — Padrões de código e manutenção

**Status:** aceito pelo mantenedor em 20/11/2026
**Data:** 20/11/2026
**Área:** API e backend
**Depende de:** ADR-008, ADR-010, ADR-012, ADR-013

## Contexto

É a decisão 12 do [mapa](README.md), acrescentada em 20/11/2026. O ADR-013 fixou onde cada coisa fica (os subpacotes `modelo`, `fontes`, `validacao`, `publicacao` e `api`, e quem importa quem), e o ADR-012 fixou as ferramentas que conferem o código (ruff, mypy no modo padrão e pytest). Nenhum dos dois diz como o código é escrito dentro dessas pastas.

Restrições que pesam:

- Duas pessoas no backend, que dominam Python (restrição do mantenedor de 19/11/2026). O código precisa poder ser assumido por outra equipe depois: o PB-48 do [backlog](../produto/backlog.md) prevê código documentado e transferência até 31/03/2028.
- O mantenedor quer que uma fonte que mude de formato ou seja trocada possa ser consertada mexendo no menor pedaço possível de código (pedido de 20/11/2026).
- A `api` lê só o pacote publicado, nunca a fonte externa (RN-ENT-01); a regra de dependência do ADR-013 já impede a `api` de importar `fontes`.
- Mudança de colunas ou de formato de uma fonte deve falhar o lote de forma explícita (RN-VPU-04).
- Chaves entram por variável de ambiente e nunca vão para o repositório (`AGENTS.md`); o caminho do pacote publicado já vem de `OBS_PUBLICADO_DIR` (ADR-013).
- O idioma do projeto é o português do Brasil, e as regras de negócio têm identificadores RN-* (`AGENTS.md`).
- Em 20/11/2026, `backend/app/` tem 235 linhas, em camadas (`controllers`, `services`, `repositories`, `dtos`), formato que veio da [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md) sem ADR que o escolhesse. Dois módulos (`repositories/publicacao.py` e `services/dimensoes.py`) acham a raiz do repositório com `Path(__file__).resolve().parents[3]`, que deixa de apontar para o lugar certo quando os arquivos mudam de pasta, como prevê o ADR-013. A `obcefem_api`, mantida pela mesma equipe, usa módulos planos por assunto, nomes em português e um único `config.py`.

## Alternativas consideradas

**Código das fontes**

1. **Contrato comum por fonte, com amostra real versionada.** Cada fonte é um módulo só em `fontes/`, que baixa o arquivo para a camada bruta e o converte em observações do modelo comum; o teste usa uma amostra pequena do arquivo real e a lista das colunas esperadas. Uma fonte que muda mexe só no seu módulo e na sua amostra; uma fonte trocada é um módulo novo com a mesma saída. Custo: guardar e renovar as amostras.
2. **O mesmo contrato, com testes só sobre dados inventados.** Recusada: o teste não mostraria o layout real da fonte, que é o que muda.
3. **Não fixar agora e decidir ao portar o primeiro coletor.** Recusada: cada coletor portado sem contrato tende a ganhar um formato próprio.

**Organização interna da `api/`**

1. **Manter as camadas atuais** (`controllers` para as rotas, `services` para a consulta, `repositories` para a leitura do pacote, `dtos` para o formato da resposta). Nada a refazer e o HTTP fica separado da lógica. Custo: uma funcionalidade fica espalhada em quatro pastas.
2. **Módulos planos por assunto, como na `obcefem_api`** (`rotas.py`, `consultas.py`, `leitura.py`, `esquemas.py`). Recusada: exige renomear cinco arquivos e os módulos tendem a crescer até virarem arquivos grandes.

Essa escolha não afeta a manutenção das fontes, que ficam em `fontes/` e não são importadas pela `api` (ADR-013).

**Convenções.** Foram apresentadas cinco: português no domínio, tipagem obrigatória, configuração num lugar só, rastreabilidade das regras e limite de complexidade no ruff (C901 e ordem de imports). As quatro primeiras foram adotadas; a quinta não foi escolhida.

## Decisão

O mantenedor escolheu, em 20/11/2026:

- **Contrato das fontes.** Cada fonte é um módulo só em `fontes/`, que faz duas coisas: baixa o arquivo para a camada bruta e o converte em observações do modelo comum de `modelo/`. Nenhuma fonte entrega formato próprio. Cada fonte tem um teste sobre uma amostra pequena do arquivo real, guardada no repositório, e a lista das colunas esperadas, de modo que uma mudança de layout falhe o teste e o lote (RN-VPU-04).
- **`api/` em camadas:** `controllers`, `services`, `repositories` e `dtos`, como já está.
- **Português no domínio.** Nomes do domínio em português (por exemplo, `municipio`, `ano_referencia`); termos do framework e da linguagem ficam como são.
- **Tipagem obrigatória** nas funções públicas, conferida pelo mypy no modo padrão (ADR-012).
- **Configuração num lugar só.** Um único módulo de configuração lê todas as variáveis de ambiente (caminhos das camadas, chaves, conexão com o banco), com os valores padrão; o resto do código importa dele. Nenhum código calcula caminho a partir da posição do próprio arquivo (`parents[n]`).
- **Rastreabilidade das regras.** O código que implementa uma regra cita o identificador dela (RN-xxx) na docstring, e um teste cita a mesma regra; quando a regra mudar, uma busca pelo identificador acha o código e o teste.

Motivo: uma fonte que muda ou é trocada passa a ser consertada no seu próprio módulo, sem tocar no restante; a configuração centralizada resolve a quebra na mudança de pasta do ADR-013; e a citação das regras acompanha a frequência com que elas têm mudado.

Fica de fora: limite de complexidade (C901) e ordem de imports no ruff, cobertura mínima de testes, mypy `--strict`, os nomes dos módulos de cada fonte, o formato das amostras e o estilo do front-end.

## Consequências

- Destrava a estrutura inicial do código: o PR que mover `app/` para `src/observatorio/api/` (ADR-013) cria o módulo de configuração e remove os dois `parents[3]`.
- Cada coletor portado do laboratório para `fontes/` traz junto a sua amostra e a lista de colunas; os coletores de `scripts/` não precisam mudar.
- As amostras versionadas devem ser pequenas (poucas linhas): os arquivos brutos continuam fora do repositório (`AGENTS.md`).
- A rastreabilidade não é conferida por ferramenta; depende da revisão dos PRs.
- Rever se a equipe crescer ou se o código do `backend/` justificar o limite de complexidade ou o modo `--strict`.
- Voltar atrás custa pouco enquanto o código for pequeno (235 linhas em 20/11/2026).
