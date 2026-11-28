# Padrão inicial para fontes — 24/11/2026

Este guia descreve o padrão das fontes do produto, aplicado à arrecadação da CFEM
([pipeline-cfem.md](pipeline-cfem.md)) à despesa por função do SICONFI
([pipeline-siconfi.md](pipeline-siconfi.md)), aos preços do Pink Sheet
([pipeline-pinksheet.md](pipeline-pinksheet.md)) e ao PIB municipal do IBGE
([pipeline-pib.md](pipeline-pib.md)). A regra de negócio permanece em
`docs/regras-de-negocio/`.

1. **Fonte:** um módulo em `backend/src/observatorio/fontes/` arquiva o bruto,
   registra URL, data, hash e filtros e devolve somente observações do modelo
   comum. Layout ou conversão inválidos geram erro explícito. A fonte não aprova
   nem publica. O teste contém poucas linhas reais, com identificadores
   anonimizados, e lista as colunas esperadas (RN-VPU-04).
2. **Modelo:** os 14 campos de RN-MOD-03 ficam em `modelo/observacao.py`.
   Dinheiro é `Decimal`; ausente não vira zero. Municípios e unidades usam as
   regras RN-TER e RN-MOD. A API serializa CFEM como texto decimal.
3. **Validação:** recebe `Lote` e referências oficiais independentes, gera
   `Resultado` e relatório por execução (RN-VPU-06/07/12). Só o recorte
   reconciliado ao centavo chega à publicação. Registra duplicatas sem
   descartá-las (RN-VPU-11), meses ausentes e motivo de bloqueio.
4. **Publicação:** recebe apenas resultado aprovado, escreve Parquet por
   indicador e manifestos numa versão imutável. A troca de `pacote.json` é o
   último passo. Falha mantém a versão anterior (RN-VPU-01/03, ADR-014). Cada
   fonte publica só o seu pacote parcial (Release `fonte-<fonte>-*`);
   `publicacao/montagem.py` (`observatorio.coleta montar`), rodado por
   `publicar-pacote.yml`, junta o último parcial de cada fonte no pacote servido
   (`pacote-*`).
5. **API:** lê uma única versão por requisição, verifica hashes e oferece
   observações mensais, anos completos, CSV e status. Acrescente o novo ID ao
   manifesto `data/indicadores.json` e ao mapa `DIMENSOES`.

Use nomes de domínio em português, `RN-xxx` na docstring e no teste, tipos em
todas as funções e configuração somente em `config.py` (ADR-017). Confira
`ruff`, `mypy --strict`, `lint-imports` e `pytest` no backend e os testes do
laboratório antes do PR. A pasta `scripts/` não entra no runtime do produto.

## Reflexões e pontos para decidir

- A referência da equipe (`obcefem_api`) soma em ponto flutuante; seu Parquet
  é útil para conferir a implementação, mas não homologa o indicador. A
  publicação independente da ANM precisa acompanhar cada recorte.
- Meses sem linha para um município permanecem ausentes. A causa segue
  não confirmada; não há preenchimento por zero.
- O controle de escala nacional de RN-CFE-12 está na validação, e a atualização
  das referências oficiais roda todo mês por `atualizar-referencias-anm.yml`, com
  PR para revisão humana (25/11/2026).
- O pacote de consumo do assistente foi reservado, mas o serviço e a política
  de seleção precisam de PR separado (RN-ENT-07/08, ainda proposta).
