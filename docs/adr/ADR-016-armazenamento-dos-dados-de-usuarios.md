# ADR-016 — Armazenamento dos dados enviados por usuários

**Status:** aceito pelo mantenedor em 19/11/2026
**Data:** 19/11/2026
**Área:** Dados e coleta
**Depende de:** ADR-009, ADR-013, ADR-015

## Contexto

É a decisão 11 do [mapa](README.md), acrescentada em 19/11/2026. O ADR-009 escolheu arquivos para as camadas do observatório e deixou de fora os dados enviados por usuários, porque arquivos que acompanham a implantação não servem para escrita durante o uso. O ADR-013 registrou a mesma lacuna.

O [Product Backlog](../produto/backlog.md) prevê que a plataforma receba e guarde dados de usuários: perfis de acesso (PB-04, vence em 31/12/2026), gestão de conteúdo (PB-19), canal de escuta (PB-24), comentários com moderação (PB-25), consultas públicas (PB-26), acompanhamento das demandas (PB-28) e cadastro e moderação no marketplace (PB-37 a PB-39).

Restrições que pesam:

- Nenhuma regra de negócio trata desses dados; os itens acima estão "sem regra" no backlog. As regras descrevem a coleta de fontes públicas e a leitura da camada publicada (RN-ENT-01, RN-ENT-02).
- A camada publicada é um pacote imutável de arquivos parquet (ADR-009, ADR-014); a escrita não pode passar por ela.
- O ambiente é provisório, em Docker com `docker compose`; a produção provável é a AWS, sem serviço escolhido (ADR-015).
- Equipe de 1 a 2 pessoas que dominam Python e já usam Docker; as escolhas devem funcionar sem custo e migrar sem retrabalho grande (restrições do mantenedor de 11/11/2026 e 19/11/2026).
- Contas, e-mails e relatos são dados pessoais. A decisão de 07/11/2026 que tirou privacidade dos requisitos tratou dos dados das fontes; para os dados de usuários não há regra, e o conflito B1 (LGPD, PB-45) está em aberto na seção 6 de [pendencias.md](../regras-de-negocio/pendencias.md). Este ADR decide onde guardar, não o que pode ser guardado.

## Alternativas consideradas

1. **PostgreSQL no `docker compose` agora e Postgres gerenciado da AWS em produção.** Banco relacional com escrita concorrente e relações entre registros (comentário, autor, moderação, iniciativa). Custo: mais um serviço no compose, migrações de esquema e backup a cargo da equipe. A oferta e o preço do Postgres gerenciado da AWS não foram conferidos, por falta de acesso à conta (ADR-015).
2. **SQLite num volume Docker.** O mais simples, sem servidor. Recusada: uma escrita por vez, exige disco persistente em produção e provavelmente forçaria a migração para outro banco antes do marketplace.
3. **Serviço externo com login e banco (Supabase, Firebase ou similar).** Traz o login pronto. Recusada: fornecedor fora do destino AWS, dados pessoais com terceiros enquanto o B1 está em aberto, e limites de plano gratuito não conferidos.
4. **Adiar.** Recusada pelo mantenedor; o PB-04 vence em 31/12/2026.

O banco gerenciado já tinha sido considerado no ADR-009 para as camadas do observatório e recusado; aquela recusa continua valendo para elas.

## Decisão

O mantenedor escolheu a alternativa 1. Fica fixado:

- Os dados enviados por usuários (contas e perfis, relatos, comentários, consultas, cadastros do marketplace) ficam num banco PostgreSQL.
- No ambiente provisório, o banco é um serviço do `docker compose` do ADR-015. Em produção, a intenção é um Postgres gerenciado da AWS, escolhido junto com o serviço de produção.
- A conexão vem por variável de ambiente, e a senha fica no `.env` fora do Git (ADR-015).
- Os dados do observatório continuam no pacote publicado em parquet (ADR-009, ADR-014) e não vão para o banco.

Motivo: encaixa no Docker que a equipe já usa e no destino AWS, e evita a migração que o SQLite forçaria quando chegarem o marketplace e os comentários.

Fica de fora: o método de login; a biblioteca de acesso ao banco e a ferramenta de migração de esquema; o esquema das tabelas; o backup (PB-47); o que pode ser guardado de dado pessoal e por quanto tempo (conflito B1, em aberto).

## Consequências

- Destrava a modelagem do PB-04 e, depois, a dos itens de escrita (PB-19, PB-24 a PB-26, PB-28, PB-37 a PB-39).
- A regra de dependência do ADR-013 precisa acomodar a escrita: o PR que implementar o primeiro desses itens define o subpacote dos dados de usuários e atualiza o contrato do `import-linter`, mantendo `api` sem acesso a `fontes`, `validacao` e `publicacao`.
- O `docker compose` e o `.env.example` previstos no ADR-015 passam a incluir o Postgres e a variável de conexão.
- A equipe passa a operar migrações de esquema e backup; o backup entra no PB-47.
- A implementação de qualquer item que guarde dado pessoal deve esperar a decisão do B1 sobre o que guardar e por quanto tempo.
- Rever se o serviço de produção da AWS não oferecer Postgres gerenciado viável, ou na revisão de 31/03/2027 do ADR-015.
- Voltar atrás custa pouco enquanto não houver dados de usuários gravados; depois, exige migrar os dados.
