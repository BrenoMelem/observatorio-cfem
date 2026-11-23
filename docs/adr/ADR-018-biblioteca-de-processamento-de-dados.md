# ADR-018 — Biblioteca de processamento de dados

**Status:** aceito pelo mantenedor em 20/11/2026
**Data:** 20/11/2026
**Área:** Dados e coleta
**Depende de:** ADR-008, ADR-011, ADR-013, ADR-014, ADR-017

## Contexto

É a decisão 13 do [mapa](README.md), acrescentada em 20/11/2026. O ADR-008 deixou de fora "as bibliotecas de dados (pandas e outras)", e o ADR-014 deixou de fora "a biblioteca de leitura e escrita (pandas, como na `obcefem_api`, ou só pyarrow)". Cada coletor de `fontes/` e a leitura do pacote pela API dependem dessa escolha.

Restrições que pesam:

- As somas de dinheiro são feitas em precisão decimal e arredondadas só no fim (RN-CFE-11).
- Mudança de colunas ou de formato de uma fonte deve falhar o lote de forma explícita, nunca resultar em publicação silenciosa (RN-VPU-04).
- O CSV de arrecadação da ANM tem 325 MB e 2.434.196 linhas, em latin-1 e com vírgula decimal (`AGENTS.md`; arquivo da Release de 19/11/2026).
- As coletas rodam no GitHub Actions (ADR-011). O pacote publicado é parquet (ADR-014). O mypy roda em `--strict` no `backend/` (ADR-017).
- Duas pessoas no backend, que dominam Python (restrição do mantenedor de 19/11/2026). A `obcefem_api` usa pandas; o mantenedor pediu que a comparação não considerasse o custo de reescrever o código dela (20/11/2026).

Medição feita em 20/11/2026, fora do repositório, numa máquina da equipe (Intel Pentium 5405U, 4 núcleos, 7 GB de memória, sem AVX). A tarefa foi ler o CSV de arrecadação inteiro, converter `ValorRecolhido` para decimal e somar por código IBGE, ano e mês. Todas as formas chegaram aos mesmos 480.803 grupos e ao mesmo total dos 12 municípios, R$ 27.416.894.786,01:

| Biblioteca | Tempo | Memória máxima | Observação |
| --- | --- | --- | --- |
| pandas 3.1.1, leitor padrão | 27,4 s | 1,3 GB | coluna de valores como objetos `Decimal` do Python |
| pandas 3.1.1, leitor pyarrow | 17,0 s | 1,2 GB | idem |
| polars 2.1.0 (`polars[rtcompat]`) | 5,7 s | 1,6 GB | inclui converter o arquivo de latin-1 para UTF-8 em memória; tipo `Decimal(20, 2)` nativo |
| módulo `csv` do Python | 20,3 s | 0,16 GB | soma em `Decimal`, sem biblioteca |
| DuckDB | — | — | não roda: "instrução ilegal" no processador sem AVX |

Na mesma máquina, o pacote padrão do polars também parou com "instrução ilegal" (exige AVX, AVX2, FMA, BMI1 e BMI2); só o pacote de compatibilidade, instalado com o extra `rtcompat`, funcionou. No mypy `--strict`, uma função de soma escrita com pandas (com `pandas-stubs`) precisou de um ajuste de tipo no resultado do `groupby`; a mesma função com polars passou, embora as linhas lidas venham sem tipo (`Any`) em alguns pontos.

## Alternativas consideradas

1. **pandas, lendo CSV com o leitor pyarrow.** O que a equipe já domina e o que a `obcefem_api` usa; lê latin-1 direto e roda em qualquer processador. Recusada: a coluna de valores decimais fica como objetos do Python (tipo `object`), e a inferência de tipos pode mudar o tipo de uma coluna sem aviso, o que vai contra a RN-VPU-04.
2. **polars.** Tipos de coluna explícitos e rígidos (uma conversão que falha é erro), `Decimal` nativo, transformações como sequência de expressões e o melhor tempo medido. Custo: a equipe aprende a biblioteca; o polars só lê UTF-8, então arquivos em latin-1 são convertidos antes; em processador sem AVX exige o pacote de compatibilidade.
3. **Módulo `csv` do Python mais pyarrow só para o parquet.** Quase nenhuma memória e nenhuma dependência nova. Recusada: junções, filtros e agregações ficariam escritos à mão, com mais código para manter.
4. **DuckDB.** Descartada: não roda na máquina da equipe usada na medição. O banco embutido já tinha sido recusado como armazenamento no ADR-009.

## Decisão

O mantenedor escolheu o **polars**, em 20/11/2026, depois de comparar pandas e polars sem considerar o custo de reescrever a `obcefem_api`. Fica fixado:

- O polars é a biblioteca de processamento de dados do `backend/`: em `fontes/`, `validacao/` e `publicacao/`, e na leitura do pacote parquet pela API.
- As somas de dinheiro usam o tipo `Decimal` do polars (RN-CFE-11).
- Arquivos de fonte em latin-1, como os da ANM, são convertidos para UTF-8 antes da leitura.
- A dependência é declarada com o extra `rtcompat`, para que o projeto rode em máquinas sem AVX.

Motivo: os tipos rígidos e o decimal nativo protegem a qualidade do dado, que é o centro das regras de validação, e o código fica com menos formas de escrever a mesma coisa, o que ajuda quem assumir o projeto depois.

Fica de fora: a leitura preguiçosa (*lazy*) e em fluxo (*streaming*); a biblioteca de acesso ao Postgres (ADR-016); a forma de portar a lógica da CFEM da `obcefem_api`.

## Consequências

- Destrava o porte da primeira fonte para `fontes/`. A lógica da CFEM da `obcefem_api`, em pandas, passa a ser reescrita em polars, conferida pelos testes e pelos totais da `obcefem_api` quando eles se aplicarem.
- A equipe precisa aprender o polars; os coletores de laboratório em `scripts/` não mudam.
- A conversão de latin-1 em memória dobra o uso de memória nesse passo (1,6 GB no arquivo de arrecadação). Rever com leitura em fluxo se os arquivos crescerem ou se o ambiente de coleta tiver pouca memória.
- Não foi conferido se, numa máquina com AVX, o polars instalado com `rtcompat` usa o pacote rápido ou o de compatibilidade; conferir ao criar a estrutura.
- O ADR-014 previa o `pyarrow` como dependência da API; com o polars lendo o parquet, isso deixa de ser necessário.
- Voltar atrás custa caro depois que as fontes forem escritas, porque todo o código de transformação usa a API do polars. Enquanto `fontes/` estiver vazio, custa pouco.
