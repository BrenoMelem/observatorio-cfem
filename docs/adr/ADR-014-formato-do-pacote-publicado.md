# ADR-014 — Formato do pacote publicado

**Status:** aceito pelo mantenedor em 17/11/2026
**Data:** 17/11/2026
**Área:** Dados e coleta
**Depende de:** ADR-009, ADR-013

## Contexto

O ADR-009 decidiu que a camada publicada é um pacote imutável de arquivos e deixou de fora o formato desses arquivos. O ADR-013 também o deixou de fora. É a decisão 10 do [mapa](README.md), acrescentada em 17/11/2026, e a base do item PB-03 (modelo do banco analítico, vence em 30/11/2026) do [Product Backlog](../produto/backlog.md). Não depende da hospedagem: onde o pacote fica na implantação continua com a decisão 6.

Restrições que pesam:

- Toda observação tem o mesmo esquema, com os 14 campos de RN-MOD-03 (RN-MOD-01, RN-MOD-02). `mes` é vazio nos indicadores anuais (RN-MOD-04), e um valor não divulgado nunca vira zero (RN-MOD-12): o formato precisa distinguir vazio de zero.
- A proveniência acompanha o dado (RN-MOD-21). O painel de status mostra, por indicador, a última atualização e o ano de referência (RN-ENT-04).
- Se a validação falhar, fica o último dado bom (RN-VPU-01, RN-VPU-03). Como cada fonte tem agenda própria (RN-TMP-02), isso precisa valer por indicador.
- Metodologia, limitações e licença ficam no manifesto único de indicadores, e não em cada linha (RN-MOD-03, RN-MOD-25); hoje o manifesto é `data/indicadores.json`. RN-MOD-25 deixa nome, formato e local do arquivo para a implementação.
- O CSV aberto sai da mesma camada e leva os metadados junto (RN-ENT-03, RN-ENT-05, esta PROPOSTA).
- A API filtra em memória (ADR-009) e pode rodar em plano gratuito com pouca memória (restrição do mantenedor de 11/11/2026).
- A `obcefem_api`, que a equipe já opera, usa pandas com parquet (README da `obcefem_api`, lido em 11/11/2026). O `backend/` atual lê `populacao.json`, uma lista de observações em JSON.

Medição feita em 17/11/2026 com observações sintéticas dos 14 campos de RN-MOD-03 (pyarrow 25.0.0, parquet com compressão zstd; saída fora do repositório):

| Linhas | JSON | JSON compactado (gzip) | Parquet | Leitura do JSON | Leitura do parquet |
| --- | --- | --- | --- | --- | --- |
| 20 mil | 7,0 MB | 0,3 MB | 0,18 MB | 0,10 s | 0,02 s |
| 200 mil | 69,8 MB | 2,8 MB | 1,66 MB | 1,00 s | 0,10 s |
| 1 milhão | 349 MB | 13,8 MB | 7,15 MB | não medido sem instrumentação | 0,44 s |

Com 200 mil linhas, a memória ocupada foi de cerca de 280 MB como objetos Python (JSON lido) e 29 MB como tabela Arrow (parquet lido). O `pyarrow` instalado ocupa 152 MB. O volume real do pacote não foi medido; uma estimativa grosseira o põe na casa de dezenas a poucas centenas de milhares de linhas, e a MSC mensal por fonte de recursos, função e subfunção pode aumentá-lo.

## Alternativas consideradas

1. **JSON** (lista de observações, como o `populacao.json`). Vantagem: é o que a API lê hoje, legível, sem dependência nova. Recusada: cerca de 350 bytes por observação, carga e memória dez vezes maiores que as do parquet na medição; e nenhum tipo garantido no arquivo. A legibilidade num diff pesa pouco, porque ninguém revisa a olho milhares de linhas de dados; o instrumento de revisão é o relatório de qualidade de cada lote (RN-VPU-06). A sugestão inicial foi JSON e foi revista depois da medição.
2. **Parquet.** Vantagem: compacto, com tipos no arquivo (nulos, inteiros e decimais garantidos na gravação), leitura rápida e pouca memória; é o formato que a equipe já opera na `obcefem_api`. Custo: o `pyarrow`, dependência de 152 MB; o arquivo é binário.
3. **CSV** (o mesmo arquivo do download). Recusada: perde os tipos, e vazio, zero e não divulgado se confundem (RN-MOD-12), além dos riscos de separador decimal e codificação.

Banco embutido (DuckDB, SQLite) foi recusado no ADR-009 e não foi reaberto.

## Decisão

O pacote publicado tem:

- **Um arquivo parquet por indicador** com as observações no esquema de RN-MOD-03. A publicação de um indicador troca só o arquivo dele, e só quando o lote passa na validação; os demais ficam como estão (RN-VPU-03 por indicador).
- **Um manifesto do pacote, `pacote.json`**, com a versão do pacote (hash do conteúdo), a data de geração e, para cada indicador, o arquivo, o hash do arquivo, o ano de referência e a data da última atualização. É dele que saem o painel de status (RN-ENT-04) e o `versao_dados` do envelope da API (RN-MOD-03, exceção de 08/11/2026).
- **O manifesto de indicadores (RN-MOD-25) em JSON**, copiado para dentro do pacote.
- **O CSV do download (RN-ENT-03) gerado a partir do parquet**, nunca usado como armazenamento.

Motivo: na medição, o parquet ocupou de 40 a 50 vezes menos disco e dez vezes menos memória que o JSON, garante os tipos que as regras exigem e é o formato que a equipe já usa na `obcefem_api`. Os manifestos ficam em JSON porque são pequenos e feitos para pessoas lerem.

Fica de fora: a biblioteca de leitura e escrita (pandas, como na `obcefem_api`, ou só pyarrow), os nomes dos arquivos, a lista exata de campos do `pacote.json`, a forma do relatório de qualidade e o lugar do pacote na implantação (decisão 6).

## Consequências

- Destrava o PB-03 e os subpacotes `modelo/` e `publicacao/` do ADR-013.
- O `pyarrow` passa a ser dependência da API; os 152 MB cabem no limite de 500 MB do pacote Python da Vercel, a opção mais restritiva levantada na decisão 6 (limite consultado em 13/11/2026, ver mapa). Ao decidir a hospedagem, conferir de novo.
- O leitor de `populacao.json` do `backend/` passa a ler `populacao.parquet` quando a publicação for implementada.
- Revisar o conteúdo de um indicador exige uma ferramenta (pandas, DuckDB ou um script), não um editor de texto.
- Rever se a dependência do `pyarrow` deixar de caber na hospedagem escolhida.
- Voltar atrás custa pouco: a leitura fica isolada em `api/` e a escrita em `publicacao/` (ADR-013), e converter parquet em outro formato é direto.

## Nota de 19/11/2026

O [ADR-015](ADR-015-hospedagem-provisoria-e-segredos.md) fixou a hospedagem provisória em Docker local, sem limite de tamanho de pacote Python como o da Vercel. A conferência do tamanho do `pyarrow` passa para o ADR do serviço da AWS.
