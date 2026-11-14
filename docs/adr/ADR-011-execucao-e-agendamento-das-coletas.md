# ADR-011 — Execução e agendamento das coletas

**Status:** aceito pelo mantenedor em 13/11/2026
**Data:** 13/11/2026
**Área:** Dados e coleta
**Depende de:** ADR-008, ADR-009

## Contexto

Com as camadas guardadas em arquivos e o pacote publicado acompanhando a implantação (ADR-009), falta decidir onde e quando rodam as coletas que geram esse pacote, e como uma falha vira issue. É a decisão 5 do mapa e faz parte do item PB-01 do [Product Backlog](../produto/backlog.md).

Restrições que pesam:

- Cada fonte tem agenda própria: mensal para CAGED, veículos, commodities e CFEM; anual para Censo, PIB, SICONFI, INEP, MapBiomas e SEEG (RN-TMP-02). O ano mais recente é descoberto em tempo de execução (RN-TMP-01).
- Se o lote falhar na validação, fica o último dado bom e abre-se uma issue (RN-VPU-01, RN-VPU-03); cada execução gera um relatório de qualidade (RN-VPU-06).
- A coleta fica fora do ciclo da requisição: a API só lê o pacote publicado (RN-ENT-01, ADR-009).
- O arquivamento das versões da ANM já roda no GitHub Actions a cada 4 horas (RN-TMP-18, `.github/workflows/arquivar-anm.yml`); a `obcefem_api` gera os dados dela por GitHub Actions todo dia (README da `obcefem_api`, lido em 11/11/2026).
- As escolhas devem funcionar em plano gratuito; equipe de 1 a 2 pessoas (restrições do mantenedor de 11/11/2026). O repositório é público (conferido em 13/11/2026).

## Alternativas consideradas

1. **GitHub Actions agendado, por fonte ou grupo de agenda.** Cada execução coleta, valida e, se passar, gera o pacote novo; se falhar, abre a issue. Vantagem: já é usado aqui e na `obcefem_api`, a issue nasce no mesmo lugar e os segredos ficam no GitHub. Custo: os limites de tempo e de disco do executor não foram conferidos em 13/11/2026; o arquivamento da ANM, com arquivos de centenas de MB, já cabe neles.
2. **Agendador dentro do servidor da API.** Recusada: exige servidor sempre ligado com disco durável, o que conflita com o pacote imutável do ADR-009 e com o plano gratuito.
3. **Agendador da plataforma de hospedagem.** Recusada: prende a coleta à hospedagem, ainda não decidida (decisão 6), e a abertura de issue exigiria um token à parte.

## Decisão

As coletas rodam em GitHub Actions agendado, por fonte ou grupo de agenda. A falha de uma coleta ou da validação abre uma issue.

Motivo: é o que a equipe já opera no arquivamento da ANM e na `obcefem_api`, e não cria dependência com a hospedagem.

Fica de fora: como o pacote novo chega à implantação (decisão 6) e quais fontes têm as versões brutas arquivadas em Release. Este último ponto segue as regras em vigor (RN-TMP-18, RN-FNT-05, RN-FNT-14, RN-FON-15: ANM, Pink Sheet e SEEG; IBGE, SICONFI e FRED não, por enquanto) e só muda por decisão sobre a regra.

## Consequências

- Destrava a decisão 6 (hospedagem e segredos).
- Os segredos das fontes (chave do FRED, credencial do Google Cloud) passam a ser necessários no GitHub; onde e como ficam é parte da decisão 6.
- Antes de implementar a primeira coleta de produção, conferir na documentação oficial os limites de tempo, disco e agendamento do GitHub Actions e anotar a data.
- Rever se uma coleta deixar de caber nos limites do executor ou se o repositório deixar de ser público.
- Voltar atrás custa pouco: os coletores são programas Python comuns, que rodam em qualquer agendador.
