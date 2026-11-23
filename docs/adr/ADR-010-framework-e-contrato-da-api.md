# ADR-010 — Framework e contrato da API

**Status:** aceito pelo mantenedor em 13/11/2026
**Data:** 13/11/2026
**Área:** API e backend
**Depende de:** ADR-008, ADR-009

## Contexto

Com a linguagem (ADR-008) e o armazenamento das camadas (ADR-009) decididos, falta escolher o framework que serve a API de produção e a forma das rotas de dados. É a decisão 4 do mapa e faz parte do item PB-01 do [Product Backlog](../produto/backlog.md).

Restrições que pesam:

- A resposta da API é híbrida: o envelope da `obcefem_api` (`filtros`, `versao_dados`, `notas`) é mantido e `dados` passa a ser uma lista de observações no esquema comum, uma por valor; séries prontas para o painel podem acompanhar como campo extra opcional (RN-MOD-03, exceção de 08/11/2026).
- A entrega é por API própria, e o CSV aberto sai da mesma camada publicada (RN-ENT-02, RN-ENT-03).
- A API lê só a camada publicada (RN-ENT-01), guardada em arquivos (ADR-009).
- Equipe de 1 a 2 pessoas que dominam Python (restrição do mantenedor de 11/11/2026); a lógica da CFEM será portada da `obcefem_api`, que é FastAPI (ADR-007).
- Os repositórios `obcefem_api` e `obcefem` são do professor, que os modifica (restrição do mantenedor de 11/11/2026); a `obcefem_api` cobre só a CFEM.
- O código em `backend/` do PR #23 já usa FastAPI, com rotas por dimensão (`backend/pyproject.toml` e `backend/README.md`, lidos em 13/11/2026).
- A [análise da Fase 0](analise-fase-0-camada-publicada-e-assistente.md), seção 4.4, recomenda rotas novas de dimensão no serviço daqui.

## Alternativas consideradas

1. **FastAPI com rotas novas por dimensão.** As rotas da `obcefem_api` não são alteradas; as rotas novas já nascem no formato híbrido. Vantagem: é o framework da `obcefem_api` e do código do PR #23, gera o OpenAPI a partir do código e não quebra o painel atual. Custo: o site precisa ser integrado às rotas novas.
2. **FastAPI replicando as rotas da `obcefem_api`, com `dados` trocado por observações.** Vantagem: o site muda menos de endereço. Recusada: quebra quem espera o formato antigo de `dados`, e a `obcefem_api` só cobre a CFEM, de modo que população e despesa precisariam de rotas novas de qualquer forma.
3. **Outro framework (Flask ou Django).** Recusada: sem ganho identificado, obrigaria a reescrever o código do PR #23 e dificultaria o porte da CFEM.

## Decisão

A API de produção usa FastAPI, com rotas novas por dimensão no formato híbrido: o envelope da `obcefem_api` mais a lista de observações. As rotas da `obcefem_api` não são alteradas.

Motivo: reaproveita o framework que a equipe já opera e cumpre a exceção de 08/11/2026 da RN-MOD-03 sem mexer no repositório do professor.

Fica de fora: os caminhos exatos das rotas, a versão do OpenAPI e a representação de commodities e das médias PA/BR nas observações. Este último ponto está em aberto na análise da Fase 0 (seção 4.4) e toca regra de negócio (RN-MOD-19); não é resolvido por este ADR.

## Consequências

- Destrava a decisão 6 (hospedagem e segredos, junto com a 5) e a 9 (assistente de IA).
- Dá base ao framework e ao formato de resposta do código do PR #23, mas não aprova a Fase 1: essa aprovação continua pendente (ver o mapa).
- O site (`obcefem`) precisa ser integrado às rotas novas; enquanto isso não ocorrer, ele segue lendo a `obcefem_api`.
- Os caminhos das rotas viram contrato quando o site passar a usá-las; fixá-los fica para o OpenAPI de produção.
- Voltar atrás no framework custa reescrever a camada de entrada HTTP; voltar atrás no formato das rotas custa pouco enquanto o site não estiver integrado e fica caro depois.
