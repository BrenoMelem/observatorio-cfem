# ADR-012 — Testes, lint e integração contínua

**Status:** aceito pelo mantenedor em 17/11/2026
**Data:** 17/11/2026
**Área:** Infraestrutura e processo
**Depende de:** ADR-007, ADR-008

## Contexto

É a decisão 7 do [mapa](README.md), parte do item PB-01 do [Product Backlog](../produto/backlog.md) e base do PB-02 (repositório, integração contínua e ambientes, vence em 30/11/2026) e do PB-41 (testes funcionais automatizados). No mapa original, a decisão 7 incluía a publicação e dependia da hospedagem (decisão 6). Em 17/11/2026 o mantenedor manteve a hospedagem adiada e aceitou dividir a decisão: este ADR trata só de testes, lint e CI, e a implantação passa para a decisão 6.

Restrições que pesam:

- Equipe de 1 a 2 pessoas que dominam Python; as escolhas devem funcionar em plano gratuito (restrições do mantenedor de 11/11/2026).
- O backend de produção é Python com `uv`, na pasta provisória `backend/` (ADR-007, ADR-008); o laboratório em `scripts/` não vai para produção e o produto não importa dele.
- As coletas já rodam no GitHub Actions (ADR-011, `.github/workflows/arquivar-anm.yml`). O repositório é público, e os executores padrão do GitHub Actions são gratuitos em repositório público (https://docs.github.com/en/billing/concepts/product-billing/github-actions, consultado em 17/11/2026).
- O `AGENTS.md` pede `uv run pytest` antes de commitar. Os testes de `scripts/` incluem a conferência dos totais das regras de negócio (`scripts/testes/test_totais_regras.py`).

Situação medida em 17/11/2026, na `develop`:

- `backend/`: `pytest` com 5 testes passando; `ruff check` sem apontamentos; `ruff format --check` aponta 6 arquivos a reformatar.
- Raiz (`scripts/`): `pytest` com 46 testes passando; `ruff check scripts` aponta 70 problemas (52 corrigíveis automaticamente).
- Não há workflow que rode testes ou lint em PR.

## Alternativas consideradas

Todas rodam no GitHub Actions, a cada PR para a `develop` e a `main`.

1. **Mínimo.** No `backend/`: `ruff check`, `ruff format --check` e `pytest`; em `scripts/`: só `pytest`. Vantagem: só ferramentas que a equipe já usa. Custo: erros de tipo só aparecem se um teste passar pelo caminho.
2. **Mínimo mais checagem de tipos no `backend/`.** Vantagem: pega cedo erros de formato na resposta híbrida da API (ADR-010). Custo: anotações de tipo e mais uma ferramenta para manter. Duas ferramentas comparadas:
   - **mypy:** pacote Python, instalado pelo `uv`; o modo padrão confere só o que está anotado, o que permite começar sem reescrever o código.
   - **pyright:** o mesmo motor do Pylance do VS Code, mais rápido; o pacote do PyPI baixa o Node na primeira execução e é mais rígido por padrão. Não escolhido por acrescentar o Node ao CI e ao ambiente de quem desenvolve.
3. **Mínimo mais lint em `scripts/`.** Vantagem: laboratório limpo. Custo: corrigir uma vez os 70 problemas apontados.

Outros provedores de CI não foram considerados: o GitHub Actions já é usado no projeto e é gratuito aqui.

## Decisão

O mantenedor escolheu as três alternativas juntas, com o mypy. A cada PR para a `develop` e a `main`, o GitHub Actions roda:

- no `backend/`: `ruff check`, `ruff format --check`, `pytest` e `mypy` no modo padrão (sem `--strict`);
- em `scripts/`: `pytest` e `ruff check`.

Motivo: protege o produto (tipos e formatação) e a documentação (totais das regras), usando ferramentas Python instaladas pelo `uv` e sem custo em repositório público. O mypy foi preferido ao pyright por ser Python puro, mais documentado e tolerante no modo padrão.

Fica de fora: a implantação e os ambientes (decisão 6), a cobertura mínima de testes, o modo `--strict` do mypy, a checagem de tipos em `scripts/` e a proteção de branch. Este ADR recomenda, sem decidir, que o mantenedor exija o CI verde para o merge nas configurações do GitHub.

## Consequências

- Destrava a decisão 8 (organização do repositório) e a parte de CI do PB-02.
- O PR que criar o workflow precisa, antes, reformatar os 6 arquivos do `backend/`, corrigir os 70 apontamentos de `scripts/` e acrescentar o mypy às dependências de desenvolvimento do `backend/` (`uv add --dev`), resolvendo o que ele apontar.
- Se a pasta `backend/` mudar de nome na decisão 8, o workflow muda junto.
- Rever se o repositório deixar de ser público (o uso de minutos passa a ter limite) ou se o código do `backend/` crescer a ponto de justificar o modo `--strict`.
- Voltar atrás custa pouco: é um arquivo de workflow e algumas linhas de configuração.

## Nota de 17/11/2026

O [ADR-013](ADR-013-organizacao-do-repositorio.md) acrescenta ao CI do `backend/` a conferência da regra de dependência entre os subpacotes, com o `import-linter`. O restante deste ADR não muda.
