# Arquivo das versões da ANM

Guarda cada versão dos arquivos de CFEM da ANM (arrecadação, distribuição e autuação) e registra o que mudou entre uma versão e a seguinte (regra RN-TMP-18). A ANM pode republicar um arquivo com conteúdo diferente, sem aviso e sem histórico; só a versão mais recente fica disponível. O `Last-Modified` da ANM não prova mudança; vale o SHA-256.

## Como funciona

O fluxo `.github/workflows/arquivar-anm.yml` roda todos os dias, às 09:00 UTC (06:00 em Brasília), e sob demanda (Actions > Arquivar arquivos da ANM > Run workflow). Agendamentos só rodam a partir da branch padrão do repositório.

1. Baixa a Release mais recente (`anm-AAAA-MM-DD`, com hora quando houver mais de uma no dia), se houver, como versão anterior.
2. Baixa os 3 arquivos da ANM e calcula tamanho, SHA-256, linhas e o total do recorte dos 12 municípios por ano.
3. Se nenhuma impressão digital mudou desde a última entrada do manifesto, termina sem fazer nada.
4. Se algo mudou, cria a Release com os arquivos brutos (`.csv.gz`) e o relatório `diferencas.md`, e grava a nova entrada no manifesto.
5. Arquiva os documentos avulsos listados em `scripts/cfem/documentos.json` (Releases `doc-AAAA-MM-DD`). O endereço dos PDFs mensais não é previsível, então a inclusão de um documento novo é manual (`nome`, `url`, `descricao`).

## Onde ficam as coisas

- **Arquivos brutos:** nas Releases deste repositório, não no Git.
- **Manifestos** (`manifesto.json` e `manifesto-documentos.json`): na branch de dados `arquivo-anm`, sem relação com a `main` nem com a `develop`. O fluxo grava nela; assim não há commit automático nas branches de trabalho.
- **Certificado:** a ANM não envia o certificado intermediário (Sectigo). `scripts/cfem/certificados/` o traz e a verificação TLS fica sempre ligada (ver o README da pasta).

## Rodar à mão

```bash
uv run python -m scripts.cfem.arquivar_anm --pasta ~/anm/novo --anterior ~/anm/anterior --manifesto ~/anm/manifesto.json
uv run python -m scripts.cfem.comparar_versoes_anm arrecadacao ANTIGO.csv NOVO.csv
```

## O que não é arquivado

APIs (SICONFI, IBGE/SIDRA, FRED), por decisão do mantenedor de 08/11/2026; a frota da Senatran (sem endereço confirmado, RN-FNT-12); o dicionário de dados da ANM (o servidor derrubava a conexão em 08/11/2026).

## Dados pessoais

Os arquivos brutos têm CPF/CNPJ e nome de titulares. Este repositório é público; por decisão do mantenedor de 07/11/2026 privacidade não é requisito do projeto. O relatório de diferenças e os manifestos não trazem identificadores.
