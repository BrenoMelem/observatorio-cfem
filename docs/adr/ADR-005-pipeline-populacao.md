# ADR-005 — Protótipo local do pipeline de população

**Status:** aceito pelo mantenedor para o protótipo local em 30/10/2026  
**Data:** 30/10/2026

## Contexto

RN-FNT-01, RN-VPU-01–07, RN-ENT-01–04 e RN-MOD-03 exigem coleta, validação, reconciliação, camada publicada e leitura por API própria. A stack de produção, banco e agendador ainda não foram decididos.

## Alternativas consideradas

1. Node.js padrão e arquivos locais separados por camada, com execução manual ou agendada externamente.
2. Python com biblioteca web e banco SQLite.
3. Serviço com banco gerenciado e orquestrador em nuvem.

## Decisão provisória

Usar Node.js padrão para a prova de arquitetura. A coleta consulta o SIDRA por município; respostas ficam em `output/observatorio/bruto/`, relatórios em `qualidade/` e somente observações homologadas em `publicado/`. A API lê apenas `publicado/`. Um arquivo de referência por ano registra a tabela independente do IBGE. A troca atômica do arquivo publicado preserva o último lote bom quando a coleta ou validação falha. O job pode ser repetido com segurança; agendamento fica para decisão posterior.

## Consequências

- Sem dependência externa e sem infraestrutura paga para validar o fluxo.
- O endpoint e o CSV são locais; hospedagem, autenticação, banco, backup e agenda precisam de decisão antes de produção.
- Cada nova edição anual precisa de uma referência independente; sem ela, a publicação falha explicitamente.
- A faixa plausível inicial de 1 a 5 milhões de pessoas por município é um controle de engenharia revisável, não uma regra estatística do IBGE.
