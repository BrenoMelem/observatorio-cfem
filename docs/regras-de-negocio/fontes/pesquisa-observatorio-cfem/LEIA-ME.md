# Pesquisa de viabilidade — Observatório CFEM

Este diretório contém o relatório técnico preliminar para o observatório da CFEM em Canaã dos Carajás e Parauapebas.

- `relatorio.tex`: relatório no formato SBC, com resumo executivo, arquitetura de ingestão, matriz indicador–fonte–modo de consumo–cadência–limitação, proposta de contrato para o front-end, controles de qualidade/LGPD/licença e plano de trabalho.
- `fontes.bib`: referências consultadas pelo artigo.
- `sbc-template.sty` e `sbc.bst`: dependências copiadas do template fornecido no ZIP.
- `modelosparapublicaodeartigos/`: cópia dos arquivos-fonte do template SBC recebidos, preservada como referência.
- `pacote-latex/`: projeto compilável com `document.tex` e todas as dependências; o pacote ZIP correspondente está em `output/pdf/fontes-latex-observatorio-cfem.zip`.
- `../../../../output/pdf/relatorio-observatorio-cfem.pdf`: versão pronta para leitura.

## Conclusões principais

1. A maior parte do escopo é publicável com dados públicos, mas as séries têm periodicidades e conceitos distintos; não é realista prometer atualização em tempo real.
2. A estratégia preferida é API oficial quando documentada; caso contrário, arquivo aberto ou exportação permitida, com versão/checksum e revisão. PDFs e indicadores derivados exigem auditoria; áreas sob autenticação não devem ser raspadas ou contornadas.
3. As melhores bases iniciais para prova de ingestão são ANM/CFEM, IBGE, SICONFI, MapBiomas, SEEG e arquivos agregados do MTE. O site deve consultar a API própria do observatório, não as fontes diretamente.
4. Há gates antes de prometer certos indicadores: acesso/licença e conceito de pobreza do CadÚnico; discriminação de homicídio por arma de fogo na série solicitada; disponibilidade IDEB por município/ano; licença de redistribuição de FAPESPA/IDSC; universo do ranking CLP; e composição geográfica oficial da RI Carajás.
5. Os três repositórios GitHub não foram inspecionados neste ambiente, por indisponibilidade de leitura remota. O relatório não atribui a eles tecnologia ou estrutura.

Se o compilador disser que não encontra `sbc-template.sty`, isso ocorre quando somente `document.tex` foi enviado. Envie o ZIP completo ou mantenha `sbc-template.sty`, `sbc.bst` e `fontes.bib` na mesma pasta do `.tex`. O compilador integrado do Codex está indisponível neste ambiente; o PDF entregue foi gerado a partir do conteúdo do relatório e inspecionado visualmente. Para compilar o projeto LaTeX original, use o pacote completo.
