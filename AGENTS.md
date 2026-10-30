# Instruções para agentes de IA

Este arquivo orienta agentes de IA (Claude Code, Codex e similares) que trabalham neste repositório. Leia também o [README](README.md) e [docs/regras-de-negocio/README.md](docs/regras-de-negocio/README.md).

## O projeto

Observatório CFEM / RI Carajás: dados públicos sobre a Compensação Financeira pela Exploração de Recursos Minerais (CFEM) e indicadores dos 12 municípios da Região de Integração Carajás, no Pará. O produto ainda não existe: o repositório tem a pesquisa, a documentação de regras de negócio, um notebook de laboratório e scripts de teste.

O idioma do projeto é o português do Brasil. Use datas absolutas (por exemplo, 30/10/2026), nunca "ontem" ou "semana passada".

## Estrutura

- `docs/regras-de-negocio/`: as regras de negócio (o quê e por quê, nunca o como). É a parte central.
- `docs/regras-de-negocio/fontes/`: documentos de origem (decisões, blocos, plano, relatórios de laboratório e a pesquisa). São material histórico: não os reescreva sem pedido explícito.
- `notebooks/` e `scripts/`: **apenas testes e laboratório**. Não vão para produção. Não os trate como a implementação do sistema.
- `output/` e `tmp/` não são versionados (ver `.gitignore`).

## Regras de negócio: como escrever

Os arquivos de `docs/regras-de-negocio/` seguem um formato fixo. Antes de editar, leia o [README](docs/regras-de-negocio/README.md) e o [glossário](docs/regras-de-negocio/glossario.md).

- **Sem implementação:** nada de código, pseudocódigo, rotas HTTP, nomes de função, bibliotecas ou escolha de stack. Nomes de campo, códigos IBGE e identificadores citados nas fontes podem aparecer.
- **Não invente regra.** Cada regra cita arquivo e seção da fonte. O que for dedução é `PROPOSTA`; o que tiver fonte conflitante ou falta de decisão é `EM ABERTO`. Na dúvida, pergunte ao mantenedor.
- **Status:** `DECIDIDA` só vem de decisão do mantenedor ou dos documentos de decisão (DECISÕES, BLOCOS, LAB-19/10, VAL-15/10, DECISÃO-MANTENEDOR). Não promova uma regra sem essa base.
- **Identificador:** `RN-<TEMA>-<NN>` (RN = Regra de Negócio). Temas: TER, MOD, FON, FNT, TMP, VPU, ENT, CFE, IND, PRI. Siglas das fontes: use as da tabela do README.
- **Exemplos:** marque como "transcrito do relatório X, não conferido no JSON" ou "reproduzido em DD/MM/AAAA". Não apresente como verificado o que não foi.
- **Evidência nova** que não decide nada entra como nota na regra (a regra continua `EM ABERTO`); não a transforme em decisão.

### Ao mudar o status de uma regra

Atualize, na mesma alteração:
1. a regra no arquivo do tema;
2. `pendencias.md` (remova a linha da seção 1 e ajuste divergências e referências cruzadas);
3. o total no `README.md`;
4. os textos de outras regras que ainda dizem "em aberto" sobre o mesmo ponto.

Confira os totais antes de commitar:

```
cd docs/regras-de-negocio
grep -h "^- \*\*Status:\*\* DECIDIDA" *.md | wc -l
grep -h "^- \*\*Status:\*\* PROPOSTA" *.md | wc -l
grep -h "^- \*\*Status:\*\* EM ABERTO" *.md | wc -l
grep -n "Total:" README.md
```

O `README.md` tem um exemplo de regra com título `### RN-`, então a contagem de títulos fica 1 acima do número de regras.

## Segurança e dados

- Os arquivos brutos da ANM (`dadosabertos.anm.gov.br`) têm colunas de **CPF/CNPJ**. Nunca imprima, grave no repositório nem cole em respostas dados por linha deles; use só agregados.
- Nunca grave chave de API, token ou credencial no repositório. Chaves entram por variável de ambiente. Se o usuário colar uma chave na conversa, não a copie para arquivos e avise que ela deve ser trocada.
- Dados baixados vão para uma pasta fora do repositório ou para `output/`/`tmp/`. Não versione dados brutos.

## Fontes externas: o que já se sabe

- **ANM (CSV):** o servidor devolve 403 sem um User-Agent de navegador e em requisições HEAD; com GET e User-Agent responde 200. Os arquivos são latin-1, com vírgula decimal no campo de valor da distribuição.
- **SICONFI:** API pública do Tesouro Nacional, sem chave. A DCA (Anexo I-E) dá a despesa por função e subfunção, mas **não** tem a origem do recurso. A MSC orçamentária (classe 6) tem `fonte_recursos`, função e subfunção; a fonte 708 (1708 nos dados) é a CFEM transferida pela União, conforme a Portaria STN 710/2021. De 2014 em diante o anexo se chama `DCA-Anexo I-E`; em 2013 é `Anexo I-E`.
- **FRED:** exige chave por variável de ambiente; a série de ferro tem valores vazios (".") até 12/1991.
- **Base dos Dados e Earth Engine:** dependem de conta do Google Cloud. A conta de serviço e o projeto ainda não foram criados.
- **Senatran (frota):** o arquivo por município traz só o nome do município, sem código IBGE.

Os detalhes e as datas das verificações estão nas notas de evidência das regras em `docs/regras-de-negocio/`.

## Fluxo de trabalho

- Como versionar o trabalho (commit, branch, push, PR) é decisão do usuário. Pergunte e não presuma.
- Scripts novos vão em `scripts/`, com docstring que diga o que fazem e que são de teste. Prefira a biblioteca padrão do Python e deixe a saída fora do repositório.
- Decisões que contrariam os documentos de origem devem ser anotadas na regra (campo Exceções) e em `pendencias.md`, não apagadas das fontes.

## Pendências conhecidas do projeto

Os documentos DECISÕES, BLOCOS e PLANO ainda não foram atualizados com as decisões de 24 a 30/10/2026; algumas as contrariam (entrega por API, Earth Engine para o uso do solo). Até o mantenedor atualizá-los, as regras citam DECISÃO-MANTENEDOR como fonte. A lista viva está em [pendencias.md](docs/regras-de-negocio/pendencias.md).
