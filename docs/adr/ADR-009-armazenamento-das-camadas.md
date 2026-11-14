# ADR-009 — Armazenamento das camadas (bruto, qualidade, publicado)

**Status:** aceito pelo mantenedor em 13/11/2026
**Data:** 13/11/2026
**Área:** Dados e coleta
**Depende de:** ADR-007, ADR-008

## Contexto

Com o produto neste repositório (ADR-007) e em Python com `uv` (ADR-008), falta decidir onde e em que forma ficam as três camadas de dados: o bruto baixado das fontes, o resultado da validação (qualidade) e o que é publicado para a API, o CSV e o assistente. É a decisão 3 do mapa e faz parte do item PB-01 do [Product Backlog](../produto/backlog.md).

Restrições que pesam:

- A camada publicada só troca quando o lote novo passa na validação; se falhar, fica o último dado bom (RN-VPU-01, RN-VPU-03).
- Front-end, exportações e assistente leem só a camada publicada (RN-ENT-01).
- Cada execução de coleta gera um relatório de qualidade (RN-VPU-06).
- O dado bruto não é versionado: o arquivo de arrecadação da ANM tem 325 MB (`AGENTS.md`), e as versões dos arquivos da ANM já são arquivadas em Releases (RN-TMP-18).
- Equipe de 1 a 2 pessoas que dominam Python; as escolhas devem funcionar em plano gratuito e poder migrar sem retrabalho grande (restrições do mantenedor de 11/11/2026).
- O protótipo em `scripts/` usa arquivos locais por camada (ADR-005); a `obcefem_api` publica parquet pré-processado, de 8 MB (README da `obcefem_api`, lido em 11/11/2026, não conferido de novo em 13/11/2026); o código em `backend/` do PR #23 lê um arquivo da pasta publicada.
- A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md), seção 4.2, propõe um pacote publicado imutável incorporado ao artefato de implantação.

## Alternativas consideradas

1. **Arquivos por camada.** O bruto fica fora do Git (Releases ou pasta local), a qualidade são relatórios em arquivo e o publicado é um pacote imutável de arquivos que acompanha a implantação. Vantagem: é o que o protótipo e a `obcefem_api` já fazem, não exige serviço nem conta nova, e a troca do pacote inteiro atende ao "último dado bom". Custo: não há consulta SQL, os filtros são feitos em memória e cada atualização de dado exige nova implantação.
2. **Banco embutido em arquivo único (DuckDB ou SQLite).** As camadas viram tabelas num arquivo que acompanha a implantação. Vantagem: SQL e agregações. Recusada por ora: é uma ferramenta a mais para aprender e testar, e o arquivo binário é ruim de revisar.
3. **Banco gerenciado (PostgreSQL em nuvem).** Vantagem: atualiza o dado sem nova implantação e serviria a dados enviados por usuários. Recusada por ora: exige conta e segredo novos, depende de plano gratuito de terceiros (limites não conferidos em 13/11/2026), a troca atômica da camada publicada teria de ser construída, e voltar atrás é caro.

## Decisão

As camadas são guardadas em arquivos. O bruto fica fora do Git (Releases ou pasta local); a qualidade são relatórios em arquivo; o publicado é um pacote imutável de arquivos que vai junto com a implantação. Não há banco embutido nem gerenciado.

Motivo: é a opção mais simples que cumpre as regras e a que o protótipo e a `obcefem_api` já usam, sem serviço novo.

Fica de fora: o formato dos arquivos (JSON, parquet ou outro), quem produz o pacote e como ele chega à implantação (decisões 5 e 6), a estrutura de pastas (decisão 8) e o armazenamento de dados enviados por usuários, previsto em itens do backlog que ainda não têm regra.

## Consequências

- Destrava a decisão 4 (framework e contrato da API) e a 5 (execução e agendamento das coletas) e, com as decisões 1 e 2, permite criar a estrutura inicial do código.
- Atualizar um dado publicado exige gerar um pacote novo e implantar de novo; a frequência possível depende das decisões 5 e 6.
- Consultas e filtros são feitos em memória sobre os arquivos; rever se o volume publicado deixar de caber na memória ou no limite da plataforma de hospedagem.
- Rever também se o projeto passar a guardar dados enviados por usuários: arquivos que acompanham a implantação não servem para escrita durante o uso.
- Voltar atrás custa pouco: os arquivos podem ser carregados num banco, e a leitura fica isolada numa única parte do código.
