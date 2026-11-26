# ADR-013 — Organização do repositório e do código do produto

**Status:** aceito pelo mantenedor em 17/11/2026
**Data:** 17/11/2026
**Área:** Infraestrutura e processo
**Depende de:** ADR-007, ADR-008, ADR-009, ADR-010, ADR-011, ADR-012

## Contexto

É a decisão 8 do [mapa](README.md). O ADR-007 deixou de fora o nome da pasta do produto, e a aprovação da Fase 1 de 13/11/2026 adotou `backend/` como pasta provisória até esta decisão. O ADR-009 deixou de fora a estrutura de pastas das camadas.

Restrições que pesam:

- O produto mora neste repositório, fora de `scripts/`, e não importa de lá (ADR-007).
- O sistema tem três responsabilidades: consumir as fontes (RN-FNT, RN-FON), validar e publicar (RN-VPU-01, RN-VPU-03, RN-VPU-04, RN-VPU-06) e servir (RN-ENT). As três usam o mesmo esquema comum de observação (RN-MOD).
- A API lê só o pacote publicado e nunca a fonte externa (RN-ENT-01, ADR-009). A coleta roda no GitHub Actions, fora do ciclo da requisição (ADR-011). Logo, a coleta e a API são executadas em lugares diferentes.
- Equipe de 1 a 2 pessoas que dominam Python (restrição do mantenedor de 11/11/2026).
- O CI do ADR-012 roda sobre `backend/`.

Situação em 17/11/2026: `backend/` é um projeto `uv` próprio, com a API em `backend/app/` (`controllers/`, `services/`, `dtos/`, `repositories/`, 5 módulos e 5 testes), lendo o pacote publicado do caminho em `OBS_PUBLICADO_DIR` (padrão `output/observatorio/publicado/`, fora do Git). A raiz do repositório é o projeto do laboratório.

## Alternativas consideradas

1. **Um projeto em `backend/`, com um pacote dividido pelas responsabilidades das regras.** Vantagem: o esquema comum fica num lugar só, para quem grava e para quem lê; pouca mudança no que existe. Custo: a API herdaria as dependências da coleta, o que se resolve com dependências opcionais.
2. **Dois projetos num workspace do `uv`** (`backend/` com a API, `pipeline/` com coleta, validação e publicação, e um pacote comum com o esquema). Vantagem: dependências mínimas em cada lado. Recusada: três projetos para manter sincronizados e CI em duas frentes, cerimônia demais para uma equipe de 1 a 2 pessoas; o ganho principal é obtido na alternativa 1 com dependências opcionais.
3. **Produto na raiz** (`src/observatorio_cfem/`), com o laboratório num projeto próprio dentro de `scripts/`. Recusada: desloca o laboratório, o `AGENTS.md`, os guias e o ADR-012 sem ganho técnico.

Para conferir a regra de dependência foi considerado o `import-linter`, pacote Python que impõe restrições aos imports entre módulos (https://pypi.org/project/import-linter/, consultado em 17/11/2026: versão 2.16, de 06/11/2026, exige Python 3.11 ou superior).

## Decisão

O produto é um único projeto `uv` em `backend/`, nome que deixa de ser provisório, com o pacote `observatorio` em layout `src/`:

```text
backend/
  pyproject.toml, uv.lock
  src/observatorio/
    modelo/       esquema comum da observação, territórios e unidades (RN-MOD, RN-TER)
    fontes/       um módulo por fonte, que entrega o dado no modelo comum (RN-FNT, RN-FON)
    validacao/    regras de qualidade e relatório de cada lote (RN-VPU)
    publicacao/   montagem do pacote imutável e troca só quando o lote passa (RN-VPU-01, RN-VPU-03)
    api/          FastAPI: rotas, DTOs da resposta híbrida e leitura do pacote (ADR-010, RN-ENT)
  tests/          espelha as pastas do pacote
```

Fica fixado também:

- **Regra de dependência.** `modelo` não importa nenhum outro subpacote. `api` importa só `modelo` e a leitura do pacote publicado, nunca `fontes`, `validacao` ou `publicacao`. A regra é conferida no CI do ADR-012 com o `import-linter`.
- **Dependências opcionais.** O que só a coleta usa (por exemplo, clientes HTTP e leitores de planilha) fica num grupo opcional `coleta`. O GitHub Actions instala o projeto com esse grupo; a API roda sem ele.
- **O código atual de `backend/app/` passa para `backend/src/observatorio/api/`**, sem mudança de comportamento.
- **Dados fora do Git.** As camadas ficam em `output/observatorio/{bruto,qualidade,publicado}/` no ambiente local, com os caminhos por variável de ambiente, como já faz o `OBS_PUBLICADO_DIR`.
- **Fluxo de trabalho.** Segue o `AGENTS.md`: branch nova a partir da `develop` e PR para a `develop` (decisão do mantenedor de 07/11/2026). Este ADR não muda o fluxo.

Motivo: o projeto é um pipeline de dados com uma API fina na ponta. Dividir o pacote pelo caminho do dado põe cada regra num lugar previsível, e a regra de dependência transforma a RN-ENT-01 numa propriedade conferida do código. Um projeto só mantém o esquema comum sem duplicação, adequado a uma equipe de 1 a 2 pessoas.

Fica de fora: o formato do pacote publicado (manifesto, versão, hash, tipo de arquivo), o lugar do pacote na implantação (decisão 6), os nomes dos módulos de cada fonte e o arquivo de configuração do `import-linter`.

## Consequências

- Com as decisões 1 a 5, 7 e 8 aceitas, a estrutura inicial do código pode ser criada. A mudança vai em PR próprio, junto ou antes do PR do CI do ADR-012: mover `app/` para `src/observatorio/api/`, criar os subpacotes vazios, configurar o grupo `coleta` e o contrato do `import-linter`, e atualizar `backend/README.md`, `README.md` e `docs/README.md`.
- Nota de 26/11/2026: a estrutura foi criada em 21/11/2026 (PR #41), com o CI do ADR-012 em seguida; desde 24/11/2026 `fontes/`, `validacao/` e `publicacao/` têm código (CFEM, referências da ANM e SICONFI).
- O CI do ADR-012 passa a rodar também o `import-linter` no `backend/`.
- O porte de coletores do laboratório para `fontes/` é feito de propósito, um por vez, com os testes do laboratório como conferência; nada é importado de `scripts/`.
- Rever se a API e a coleta precisarem de versões incompatíveis de uma mesma dependência, ou se a equipe crescer: aí a separação em dois projetos (alternativa 2) é direta, porque os subpacotes já estão divididos.
- Rever a estrutura das camadas se o projeto passar a guardar dados enviados por usuários (lacuna registrada no ADR-009 e no backlog).
- Voltar atrás custa pouco enquanto o código for pequeno; com o `import-linter`, a fronteira entre os subpacotes não se degrada sem aviso.

## Nota de 19/11/2026

O [ADR-016](ADR-016-armazenamento-dos-dados-de-usuarios.md) decidiu guardar os dados enviados por usuários em PostgreSQL. O subpacote desses dados e o ajuste do contrato do `import-linter` ficam para o PR que implementar o primeiro item de escrita; `api` continua sem acesso a `fontes`, `validacao` e `publicacao`.

## Nota de 20/11/2026

O [ADR-017](ADR-017-padroes-de-codigo.md) fixa como o código é escrito dentro destes subpacotes: cada fonte é um módulo em `fontes/` com a mesma saída no modelo comum e um teste sobre amostra do arquivo real; a `api/` mantém as camadas `controllers`, `services`, `repositories` e `dtos`; um único módulo de configuração lê as variáveis de ambiente. A mudança de `app/` para `src/observatorio/api/` remove os cálculos de caminho com `parents[n]`. O restante deste ADR não muda.
