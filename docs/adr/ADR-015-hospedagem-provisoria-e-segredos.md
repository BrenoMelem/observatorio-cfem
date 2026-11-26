# ADR-015 — Hospedagem provisória em Docker local e segredos

**Status:** aceito pelo mantenedor em 19/11/2026
**Data:** 19/11/2026
**Área:** Infraestrutura e processo
**Depende de:** ADR-009, ADR-010, ADR-011, ADR-013, ADR-014

## Contexto

É a decisão 6 do [mapa](README.md) (hospedagem e segredos), adiada pelo mantenedor em 13/11/2026 e mantida adiada em 17/11/2026. Em 13/11/2026 foram apresentadas três opções (Vercel no plano Hobby, Render no serviço gratuito e Google Cloud Run); os fatos consultados estão na nota de 13/11/2026 do mapa.

Em 19/11/2026 o mantenedor informou:

- a hospedagem de produção provavelmente será a AWS, mas a equipe ainda não tem acesso e não há previsão de quando terá; a conta não é controlada pela equipe;
- até lá, o ambiente é a máquina de cada pessoa da equipe e, se for possível, uma máquina da universidade;
- a equipe já usa Docker.

Restrições que pesam:

- A API lê só o pacote publicado (RN-ENT-01), e a leitura fica isolada em `api/` (ADR-013). O caminho do pacote vem por variável de ambiente, como o `OBS_PUBLICADO_DIR` (ADR-013).
- O pacote publicado é imutável e troca por indicador só quando o lote passa na validação (RN-VPU-01, RN-VPU-03, ADR-009, ADR-014).
- As coletas rodam no GitHub Actions agendado (ADR-011); os segredos das fontes (chave do FRED, credencial do Google Cloud) precisam estar disponíveis ali (ADR-011, `AGENTS.md`).
- Nenhuma chave, token ou credencial vai para o repositório (`AGENTS.md`).
- Equipe de 1 a 2 pessoas que dominam Python; as escolhas devem funcionar sem custo e migrar sem retrabalho grande (restrições do mantenedor de 11/11/2026).
- O PB-02 pede ambientes de desenvolvimento e homologação até 30/11/2026; a implantação em produção (PB-46) vence em 31/07/2027; a primeira versão deve estar no ar até maio de 2027 ([backlog](../produto/backlog.md), restrição de 11/11/2026).
- As versões dos arquivos da ANM já são publicadas em Releases do GitHub pelo GitHub Actions (RN-TMP-18, [guia](../guias/arquivo-anm.md)).

## Alternativas consideradas

1. **Imagem Docker rodando localmente, com a AWS como destino provável.** A API ganha uma imagem e um `docker compose`; o pacote entra por volume. Vantagem: a equipe já usa Docker, a mesma imagem serve à máquina de cada pessoa, à da universidade e a um serviço de nuvem, e o ambiente fica reproduzível para a homologação. Custo: um Dockerfile e um arquivo de compose, sem dinheiro. Risco: os serviços da AWS que aceitam imagem Docker não foram conferidos na documentação oficial, por falta de acesso.
2. **Rodar localmente com `uv run`, sem Docker, e manter a hospedagem adiada.** Mais simples hoje, mas cada máquina fica configurada de um jeito, a homologação do PB-02 fica sem ambiente reproduzível e o empacotamento só seria resolvido na migração.
3. **Escolher já o serviço da AWS.** Descartada: sem acesso à conta, a escolha se apoiaria em preço, limites e permissões que não podem ser conferidos.
4. **Adiar de novo.** Descartada pelo mantenedor: o PB-02 continuaria travado.

Para levar o pacote gerado no GitHub Actions ao ambiente local ou à máquina da universidade, foram consideradas duas formas: publicá-lo como Release do GitHub, que cada ambiente baixa, ou cada ambiente rodar as coletas e gerar o próprio pacote. A segunda multiplica os segredos das fontes por máquina e permite que dois ambientes publiquem dados diferentes.

## Decisão

O mantenedor escolheu a alternativa 1, com o pacote distribuído por Release do GitHub. Fica fixado:

- **Ambiente provisório.** Até haver acesso à AWS, a API roda numa imagem Docker, com `docker compose`, na máquina de cada pessoa da equipe e, se for possível, numa máquina da universidade, que passa a ser o ambiente de homologação.
- **Pacote publicado.** O pacote é gerado no GitHub Actions (ADR-011) e publicado como Release do GitHub. Cada ambiente baixa a versão desejada e a monta na imagem por volume; o caminho continua vindo da variável de ambiente (ADR-013). A imagem não traz dados dentro.
- **Segredos.** Na máquina local, num arquivo `.env` fora do Git, com um `.env.example` versionado sem valores. Nas coletas, nos Secrets do GitHub.
- **Produção.** A AWS fica registrada como destino provável, sem escolha de serviço. O serviço será decidido num ADR novo quando houver acesso à conta.
- **Data de revisão.** Se não houver acesso à AWS até 31/03/2027, o mantenedor volta a decidir a hospedagem de produção, considerando a máquina da universidade e as opções levantadas em 13/11/2026.

Motivo: permite trabalhar e homologar já, sem conta de nuvem, com um empacotamento que a equipe conhece e que não precisa ser refeito quando a AWS chegar.

Fica de fora: o serviço da AWS e como o pacote chega até ele; o domínio e o certificado (PB-46); o monitoramento e o backup (PB-47); onde o assistente de IA roda (decisão 9); os nomes das variáveis de ambiente além do `OBS_PUBLICADO_DIR`; a forma de nomear as versões da Release do pacote.

## Consequências

- Destrava a subtarefa de ambientes do PB-02 e, como provisória, a de hospedagem do PB-01. A decisão 9 (onde o assistente roda) continua dependendo da hospedagem de produção, que este ADR não escolhe.
- O PR que aplicar este ADR cria o Dockerfile da API, o `docker compose`, o `.env.example` e o passo do GitHub Actions que publica o pacote como Release, e atualiza o `backend/README.md` com o modo de subir o ambiente.
- Nota de 26/11/2026: o Dockerfile, o `docker compose` e o `.env.example` existem desde 21/11/2026; o pacote sai como Release desde 25/11/2026, com os nomes `fonte-<fonte>-AAAA-MM-DD-HHMM` e `pacote-AAAA-MM-DD-HHMM` (ADR-011, nota de 25/11/2026).
- Enquanto o ambiente for local, ninguém de fora da equipe acessa a API, e o front-end só consome a API de quem a estiver rodando.
- A Release do pacote fica pública enquanto o repositório for público. O pacote contém só dados publicados, então isso não expõe nada novo; rever se o repositório deixar de ser público.
- Rever quando houver acesso à AWS (ADR novo) ou em 31/03/2027, o que vier primeiro.
- Voltar atrás custa pouco: a API continua sendo um programa Python que roda com `uv run`, e a imagem só o empacota.
