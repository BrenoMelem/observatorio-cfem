# Observatório CFEM

Projeto de pesquisa e desenvolvimento de um observatório de dados públicos sobre a Compensação Financeira pela Exploração de Recursos Minerais (CFEM), com foco inicial em Canaã dos Carajás e Parauapebas, no Pará.

## Escopo atual

O repositório reúne a pesquisa de viabilidade, o mapeamento de fontes e indicadores, validações exploratórias das fontes públicas e um notebook de laboratório. A pesquisa diferencia arrecadação da CFEM, distribuição aos entes beneficiários e autuações, que são medidas distintas.

O sistema do observatório ainda está em fase de pesquisa e planejamento. Os documentos registram limitações, pontos que precisam de validação e próximos passos antes de assumir cobertura ou atualização de qualquer indicador.

## Estrutura

- `docs/pesquisa-observatorio-cfem/`: relatório de viabilidade, fontes, bibliografia e pacote LaTeX.
- `notebooks/`: laboratório exploratório de fontes do observatório.
- `scripts/`: scripts de validação, reconciliação e consulta exploratória.

## Começar

Abra `notebooks/laboratorio_fontes_observatorio_cfem.ipynb` em Jupyter ou Google Colab. Os scripts Python informam suas dependências nos próprios arquivos ou usam bibliotecas comuns de análise de dados; consulte cada cabeçalho antes de executar.

Os scripts que consultam serviços externos fazem requisições às fontes indicadas no código. Para bases que exigem autenticação, use os meios oficiais e não inclua credenciais, tokens ou dados identificáveis neste repositório.

## Fontes e proveniência

As fontes públicas, seus formatos, limitações e referências estão documentados em `docs/pesquisa-observatorio-cfem/`. Dados brutos baixados, resultados de execução e imagens de sessão não são versionados. Gere esses artefatos localmente e confirme a licença e a proveniência antes de redistribuir dados derivados.

## Situação

Pesquisa de viabilidade e validação de fontes. A definição final de requisitos, arquitetura, licenças de redistribuição e plano de implementação deve ser aprovada antes da construção do produto.
