# Execução e limites da fatia CFEM — 24/11/2026

## Verificação complementar de 24/11/2026

A CLI foi reexecutada com `tmp/CFEM_Arrecadacao.csv`, as 669 referências
municipais, dez totais nacionais oficiais e as capturas Markdown versionadas
em `docs/registros/evidencias-anm-2026-11-23/`. A saída isolada ficou em
`output/pipeline-cfem-verificacao/`, fora do Git: 2.433.952 linhas lidas,
129 repetições no recorte, 669 reconciliações municipais, dez controles
nacionais e zero erros. O pacote local aprovado tem versão
`eeef52b33ad5d70914f51d829a2a2ec2ea964bb83a88a026dc4b8585f9bf8951`.
As diferenças nacionais dos dez anos selecionados ficaram abaixo de 1%,
entre 0,005% e 0,445%. Essa verificação não resolve as 15 divergências dos
oito anos excluídos nem autentica o corpo HTTP original da ANM.

CSV local da ANM: `tmp/CFEM_Arrecadacao.csv`, fora do Git. Leitura realizada
em 23/11/2026: 2.433.952 linhas, 10.827 linhas no recorte dos 12 municípios,
129 repetições integrais somadas e registradas. Hash e relatório completos
ficam em `output/pipeline-cfem/`, que não é versionado.

As referências em `data/referencia-cfem-mensal-anm.json` foram transcritas em
23/11/2026 das tabelas oficiais mensais da ANM por município/ano/PA, com URL,
data de consulta e hash do conteúdo recuperado. A conferência inicial encontrou
coincidência em todos os valores presentes de 2008, 2009, 2010, 2013, 2015,
2016, 2017, 2018, 2020 e 2025. Divergências em 2011, 2012, 2014, 2019,
2021, 2022, 2023 e 2024 excluíram esses anos por inteiro do arquivo de
referências desta execução. O detalhamento local está em
`output/pipeline-cfem/conferencia-oficial.json`. A ausência de referência
para outro ano não equivale a arrecadação zero.

Em 24/11/2026 a CLI executou com esse CSV e as 669 referências oficiais
selecionadas. Resultado `aprovado`, versão
`f2e8658640432b8c21b2bd3117f94eeb45541cebc09d912ff7ec99aa4ff46486`.
O relatório local está em `output/pipeline-cfem/qualidade/`; a API de teste
respondeu `/saude = pronto`, dimensão econômica e CSV com HTTP 200. O recorte
anual de 2025 devolveu Canaã R$ 1.248.202.989,59 e Parauapebas
R$ 1.102.944.678,86, iguais à tabela oficial. A publicação permanece apenas
na pasta local ignorada pelo Git, sem dados brutos no PR.

**Limites:** a referência cobre apenas as células que a ANM publicou na tabela
municipal. Os meses sem registro ficam como lacuna, sem inferência de zero.
Não foi comprovado nesta execução o controle nacional de escala de RN-CFE-12,
nem arquivado no Git um espelho integral das páginas oficiais. O arquivo de
referências deve ser revisado antes de uso operacional regular. A série
2003–2007 e 2026 não foi homologada neste recorte. O front oficial não foi
alterado; `backend/demo/grafico-cfem.html` é uma demonstração separada.

## Pendências e caminhos de solução

1. **Divergências de oito anos:** comparar os meses divergentes com edições
   históricas do CSV e consultar a ANM; versionar a correção sem reduzir a
   tolerância zero (RN-VPU-12).
2. **Controle nacional:** transcrever e versionar totais anuais oficiais da
   ANM com URL, data e hash; bloquear queda superior a 1% (RN-CFE-12).
3. **Ausências municipais:** solicitar confirmação oficial para distinguir
   falta da fonte de inexistência de arrecadação (RN-CFE-07/09).
4. **Automação da referência:** criar coletor e verificador para a tabela
   independente, com retenção da página e comparação entre edições.
5. **Assistente:** implementar busca determinística, controle somente leitura,
   mock com citações e casos de recusa em PR separado. O arquivo
   `consumo_assistente.json` do pacote, sozinho, não é serviço de IA.
6. **Integração com o site da equipe:** depende de autorização para editar o
   front oficial; a demo local permite revisar o contrato antes disso.
7. **Docker e navegador:** executar o ambiente com pacote montado, validar
   CORS e conferir o gráfico e a tabela visualmente antes da apresentação.

Nenhuma regra de negócio foi promovida de status nesta alteração.

## Verificações de 24/11/2026

- Backend: `ruff check`, `ruff format --check`, `mypy --strict` e
  `lint-imports` passaram; `pytest` passou com 34 testes. Há um aviso de
  depreciação do `TestClient` sobre `httpx`, sem falha de teste.
- Laboratório: `ruff check scripts` e `pytest` passaram com 61 testes.
- CLI real: pacote publicado em pasta local ignorada, `/saude = pronto`,
  dimensão econômica, status e CSV com HTTP 200. A agregação anual de 2025
  reproduziu os valores oficiais de Canaã e Parauapebas acima.
- Demo: `node --check` do JavaScript passou. `docker compose config --quiet`
  passou usando senha fictícia efêmera. `docker compose build api` não pôde
  executar porque o daemon Docker Desktop Linux não estava ativo. A inspeção
  visual do gráfico em navegador não foi realizada neste ambiente; a API e o
  JavaScript foram verificados separadamente, sem inferir aprovação visual.
