# ADR-007 — Linguagem e ambiente de execução do backend

**Status:** aceito pelo mantenedor em 11/11/2026
**Data:** 11/11/2026
**Área:** API e backend
**Depende de:** ADR-006

## Contexto

Com o produto morando neste repositório (ADR-006), falta escolher a linguagem do backend, a versão e a ferramenta que gerencia ambiente e dependências. O protótipo em `scripts/` estar em Python com `uv` não decidia isso (ADR-005, nota de 08/11/2026).

Restrições que pesam:

- Equipe de 1 a 2 pessoas que dominam Python; primeira versão no ar até maio de 2027 (restrições do mantenedor de 11/11/2026).
- A lógica da CFEM da `obcefem_api`, cerca de 2.000 linhas em Python com pandas, será portada para cá (ADR-006).
- O protótipo e o arquivamento da ANM já rodam em Python 3.12 com `uv` no GitHub Actions (`pyproject.toml`, `.github/workflows/arquivar-anm.yml`); a `obcefem_api` usa Python 3.12 no Docker.
- As escolhas devem funcionar em plano gratuito (restrição do mantenedor de 11/11/2026).

Fatos externos, consultados em 11/11/2026:

- Suporte das versões do Python (https://devguide.python.org/versions/): a 3.12 recebe só correções de segurança, até outubro de 2028; a 3.13, só de segurança, até outubro de 2029; a 3.14 recebe correções gerais, até outubro de 2030.
- A Vercel, onde a `obcefem_api` está publicada, aceita Python 3.12 (padrão), 3.13 e 3.14 e lê `pyproject.toml` com `uv.lock` (https://vercel.com/docs/functions/runtimes/python). Isso não decide a hospedagem (decisão 6 do mapa).

## Alternativas consideradas

1. **Python 3.12 com `uv`.** A mesma versão do protótipo, da `obcefem_api` e do padrão da Vercel. Não exige aprender nem instalar nada. Custo: a 3.12 já está em fase só de segurança e precisará de uma subida de versão antes de outubro de 2028.
2. **Python 3.14 com `uv`.** Dois anos a mais de suporte. Recusada por ora: o comportamento das bibliotecas da `obcefem_api` (pandas, pyarrow, cryptography) na 3.14 não foi verificado, e o porte da CFEM passaria a mudar o lugar e a versão ao mesmo tempo.
3. **TypeScript com Node.** Recusada: contraria a restrição de equipe e obrigaria a reescrever a lógica da CFEM em vez de portar.

## Decisão

O backend de produção será escrito em Python, com a versão 3.12 como mínima, e o ambiente e as dependências serão gerenciados com `uv` (`pyproject.toml` e `uv.lock` versionados).

Motivo: o porte da CFEM é o trabalho mais arriscado dos próximos meses, e manter a versão garante que qualquer diferença de resultado venha do porte, não do Python.

Fica de fora: o framework da API, as bibliotecas de dados (pandas e outras), o armazenamento e a hospedagem.

## Consequências

- Destrava a decisão 3 (armazenamento das camadas) e, com ela, a estrutura inicial do código.
- O produto e o laboratório usam a mesma linguagem, mas continuam separados: o produto não importa de `scripts/` (ADR-006). Como os dois convivem no mesmo `pyproject.toml` ou em projetos separados fica para a decisão 8.
- Uma subida de versão precisa acontecer antes de outubro de 2028; rever antes disso se uma dependência deixar de publicar para a 3.12.
- Voltar atrás na versão custa pouco (uma linha e a execução dos testes). Trocar de linguagem custaria reescrever tudo.
