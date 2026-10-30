# Regras de negócio do backend do Observatório CFEM

Documentação das regras de negócio do backend do Observatório CFEM, também chamado Observatório RI Carajás. Ela descreve **o que** o sistema deve garantir e **por quê**, e nunca **como** implementar. Data desta versão: 24/10/2026.

## O projeto

O observatório coleta indicadores de população, economia, mineração (CFEM), sociedade, meio ambiente e finanças públicas dos 12 municípios da Região de Integração Carajás (PA), com foco em Canaã dos Carajás (IBGE 1502152) e Parauapebas (IBGE 1505536). O sistema ainda está em fase de pesquisa e validação de fontes: o que existe são provas, scripts de validação e um primeiro importador da CFEM, não um backend implementado.

## As duas responsabilidades do backend

1. **Consumir as fontes externas:** coletar, tratar, validar e versionar os dados.
2. **Servir os dados tratados:** camada de dados publicada, consumida pelo front-end, por exportações CSV e por um assistente de IA. A forma de entrega (arquivos, API própria ou ambos) está em aberto; as regras valem para qualquer uma.

## Para quem é e como ler

O público são pessoas desenvolvedoras e agentes de IA que vão implementar adaptadores, validações, publicação e a API. Os dois devem poder usar a mesma documentação, por isso:

- cada regra tem um título próprio, com um identificador que nunca muda; uma regra removida vira "obsoleta" e não é apagada;
- as datas são absolutas;
- nenhuma informação está só em imagem;
- as tabelas são em Markdown.

Comece por este arquivo, passe ao [glossário](glossario.md) e leia o tema que interessa. Consulte [pendencias.md](pendencias.md) para saber o que ainda não foi decidido ou confirmado antes de implementar qualquer coisa.

## Formato de cada regra

O identificador de cada regra é `RN-<TEMA>-<NN>`: **RN** é "Regra de Negócio", `<TEMA>` é o prefixo de três letras do tema (tabela do [índice](#índice)) e `<NN>` é o número da regra dentro do tema. Por exemplo, `RN-CFE-06` é a sexta regra do tema CFEM.

```
### RN-<TEMA>-<NN>: título curto
- Status: DECIDIDA | PROPOSTA | EM ABERTO
- Regra: uma frase com "deve" ou "não deve"
- Motivo: por que a regra existe
- Exemplo: um caso concreto das fontes
- Exceções: quando houver
- Fonte: arquivo e seção
- Relacionadas: IDs de outras regras
```

## Legenda do status da regra

O status da regra descreve a regra nesta documentação. Ele é diferente da natureza do valor e do estado de validação, que descrevem um valor publicado (ver [modelo-de-dados.md](modelo-de-dados.md)).

| Status | Quando se aplica |
| --- | --- |
| **DECIDIDA** | A regra vem de DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10 com redação explícita, ou de decisão do mantenedor de 24/10/2026 (DECISÃO-MANTENEDOR) |
| **PROPOSTA** | Aguarda confirmação e consta em [pendencias.md](pendencias.md). A regra foi deduzida, ou vem só de CONSUMO, MAPA-TEMAS, PESQUISA, PLANO ou do código. Se a mesma regra aparece também em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10, ela é DECIDIDA e as duas fontes são citadas |
| **EM ABERTO** | Não há decisão, ou as fontes se contradizem. Cada item consta em [pendencias.md](pendencias.md) |

Quando duas fontes se contradizem, não se escolhe: as duas versões são registradas, com a data de cada uma, e o ponto fica EM ABERTO, salvo decisão do mantenedor.

## Fontes e siglas

| Sigla | Arquivo | Data | Papel |
| --- | --- | --- | --- |
| DECISÕES | [`registro-de-decisoes.md`](fontes/registro-de-decisoes.md) | 04/10/2026; última edição 20/10/2026; exportado em 24/10/2026 (revisão 72) | Decisões oficiais do projeto |
| BLOCOS | [`blocos-tematicos.md`](fontes/blocos-tematicos.md) | 04/10/2026; última edição 20/10/2026; exportado em 24/10/2026 (revisão 29) | Decisões: tabelas de indicadores por bloco e o Bloco 3 completo |
| LAB-19/10 | [`relatorio-laboratorio-fontes-2026-10-19.md`](fontes/relatorio-laboratorio-fontes-2026-10-19.md) | 19/10/2026 (execução de 17/10/2026; FRED reexecutado em 19/10/2026) | Evidência mais recente dos testes de fontes |
| VAL-15/10 | [`fontes/pesquisa-observatorio-cfem/relatorio-validacao-e-proximos-passos-2026-10-15.md`](fontes/pesquisa-observatorio-cfem/relatorio-validacao-e-proximos-passos-2026-10-15.md) | 15/10/2026 | Validação com arquivos integrais e sequência do backend |
| CONSUMO | [`fontes/pesquisa-observatorio-cfem/analise-consumo-dados-por-topico.md`](fontes/pesquisa-observatorio-cfem/analise-consumo-dados-por-topico.md) | consulta de 02/10/2026 | Classificação de acesso A/B/C/D e contrato de dados; referência histórica (gera só PROPOSTA) |
| MAPA-TEMAS | [`fontes/pesquisa-observatorio-cfem/mapa-simples-api-por-tema-oficial.md`](fontes/pesquisa-observatorio-cfem/mapa-simples-api-por-tema-oficial.md) | consulta de 02/10/2026 | Resumo de qual tema tem API; referência histórica (gera só PROPOSTA) |
| PESQUISA | [`fontes/pesquisa-observatorio-cfem/LEIA-ME.md`](fontes/pesquisa-observatorio-cfem/LEIA-ME.md) | sem data | Relatório de pesquisa e viabilidade; referência histórica (gera só PROPOSTA) |
| PLANO | [`plano-de-integracao-de-dados.md`](fontes/plano-de-integracao-de-dados.md) | 30/09/2026 | Plano original, referência histórica; várias partes foram atualizadas depois por DECISÕES e BLOCOS |
| NOTEBOOK | `notebooks/laboratorio_fontes_observatorio_cfem.ipynb` | out/2026 | Evidência (só gera PROPOSTA) |
| SCRIPTS | `scripts/` | out/2026 | Evidência: validadores, reconciliação e importador da CFEM (só gera PROPOSTA) |
| DECISÃO-MANTENEDOR | Decisão do mantenedor | 24/10/2026 | Respostas da Fase 1, registradas aqui até DECISÕES e BLOCOS serem atualizados |

Evidências em `output/` (JSONs e manifestos) não estão no Git por decisão do projeto. Os exemplos que dependem delas estão marcados como "transcrito do relatório, não conferido no JSON". Os que foram reproduzidos em 25/10/2026, rodando de novo os scripts do repositório sobre os arquivos da ANM baixados nesse dia e consultando a API do IBGE, estão marcados como "reproduzido em 25/10/2026". Os arquivos da ANM foram atualizados em 24/10/2026, depois da validação de 15/10/2026. `docs/api/openapi.yaml` e `adr/` não existem no repositório e não são fonte de regra.

Todas as fontes ficam em [fontes/](fontes/): os documentos de decisão e o plano original na raiz da pasta; os demais estão em [fontes/pesquisa-observatorio-cfem/](fontes/pesquisa-observatorio-cfem/). Nenhuma fonte é apagada: uma fonte obsoleta é marcada como tal, e só pode ser removida quando nenhuma regra a citar.

Os títulos de seção nas citações (por exemplo, "DECISÕES §Bloco 3") são os títulos dos documentos de origem.

## O que esta documentação não contém

Não há código, pseudocódigo, rotas HTTP, nomes de funções, escolha de bibliotecas nem de stack. Nomes de campos, códigos IBGE e identificadores já citados nas fontes aparecem porque fazem parte da regra. As decisões de arquitetura de DECISÕES que dizem respeito a como implementar (adaptadores, agendador, pastas de dados brutos e tratados, nomes de arquivos de configuração) ficaram de fora; entram apenas as garantias que elas protegem.

## Índice

| Arquivo | Prefixo | Conteúdo | Regras |
| --- | --- | --- | ---: |
| [territorio.md](territorio.md) | RN-TER | Os 12 municípios, códigos IBGE, agregação regional, municípios de comparação | 12 |
| [modelo-de-dados.md](modelo-de-dados.md) | RN-MOD | Observação, natureza do valor, estado de validação, proveniência, comparabilidade | 27 |
| [consumo-de-fontes.md](consumo-de-fontes.md) | RN-FON | Níveis A/B/C/D, procedência, acesso permitido e credenciais | 20 |
| [regras-por-fonte.md](regras-por-fonte.md) | RN-FNT | Ressalvas específicas de cada fonte | 21 |
| [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md) | RN-TMP | Ano de referência, agenda por fonte, períodos, mudanças de método | 17 |
| [validacao-e-publicacao.md](validacao-e-publicacao.md) | RN-VPU | Validação, lote bloqueado, reconciliação, homologação | 12 |
| [entrega-dos-dados.md](entrega-dos-dados.md) | RN-ENT | Camada publicada, CSV aberto, painel de status, assistente de IA | 10 |
| [mineracao-cfem.md](mineracao-cfem.md) | RN-CFE | Arrecadação, distribuição, autuação e VPM | 22 |
| [indicadores-derivados-e-compostos.md](indicadores-derivados-e-compostos.md) | RN-IND | Indicadores derivados e compostos congelados | 13 |
| [privacidade-e-licencas.md](privacidade-e-licencas.md) | RN-PRI | Dados pessoais, acesso restrito e reuso | 10 |
| [glossario.md](glossario.md) | | Termos e siglas | |
| [pendencias.md](pendencias.md) | | Tudo o que está EM ABERTO, as divergências entre fontes e as regras PROPOSTAS aguardando confirmação | |

Total: 164 regras, sendo 118 DECIDIDAS, 36 PROPOSTAS e 10 EM ABERTO.
