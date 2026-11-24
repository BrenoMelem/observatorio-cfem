# Plano de execução — 23/11/2026

Objetivo autorizado pelo mantenedor: fonte ANM → modelo → validação → pacote
imutável → API → demonstração para 26/11/2026; depois, assistente offline e guia.
Os dois ZIPs e as imagens da reunião são referências, não código de produção.

Decisões do mantenedor nesta sessão: somente dados validados no gráfico;
dinheiro como texto decimal na API; `consumo_assistente.json` no pacote;
orquestrador em `observatorio/coleta.py`. A proposta do assistente não promove
o status das regras RN-ENT-07/08. Commodities globais ficam fora desta fatia.

## Marcos e verificações

1. Modelo comum: portar Observacao para modelo, preservar nulidade e população,
   Decimal para CFEM; testes de dinheiro e compatibilidade antes da alteração.
2. Fonte: arquivar CSV e hash, converter latin-1 para UTF-8, conferir layout,
   somar em decimal e registrar duplicatas, cobertura e filtros. Testes de
   amostra real, layout, conversão e arredondamento.
3. Validação: reconciliar cada município/mês com referência identificada,
   tolerância zero; ausências nunca viram zero. Falhas conservam publicação.
   A referência derivada do mesmo CSV não prova, sozinha, RN-VPU-07: registrar
   separadamente conferência de implementação e homologação oficial.
4. Publicação: diretórios imutáveis por versão e ponteiro atômico pacote.json;
   leitor resolve uma versão por requisição, verifica hashes e esquema.
   Testes de corrupção, falha de montagem, conservação e concorrência.
5. CLI e API: qualidade por execução, consulta mensal e anual completa,
   CSV com metadados, saúde, CORS restrito. Testes HTTP e imports.
6. Demo HTML: apenas API, gráfico anual/mensal, valores e metadados acessíveis,
   estados de erro/lacuna, Plotly fixado. Verificação no navegador.
7. Assistente PROPOSTA: busca determinística, controle auditável, mock offline,
   citações, recusa e limites; avaliação sem credenciais.
8. Guia e registro: comandos reproduzíveis, evidências reais e lacunas;
   ruff, formato, mypy, import-linter e pytest do produto e laboratório;
   commits por marco e PR para develop, sem merge.

## Atenção na revisão

- Não homologar dados só porque aparecem no ZIP ou estão marcados reais no front.
- Não arredondar antes da agregação nem aceitar diferença de um centavo.
- Não trocar apenas arquivos soltos durante uma leitura concorrente.
- Não perder outros indicadores ou séries já publicadas.
- Não incorporar arquivos locais não versionados ao commit.

Alternativas descartadas: alterar o front oficial (fora da autorização), usar
o laboratório como runtime (ADR-007), substituir validação por dados fictícios
(RN-VPU-10). Implementação segue o plano fornecido e autorizado pelo usuário.
