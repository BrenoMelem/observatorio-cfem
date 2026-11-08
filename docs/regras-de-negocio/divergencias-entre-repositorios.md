# Divergências entre este repositório e os repositórios `obcefem_api` e `obcefem`

Comparação feita em 08/11/2026 entre as regras de negócio deste repositório e o que os outros dois repositórios do projeto fazem ou afirmam. Este documento **não muda o status de nenhuma regra**: as decisões abaixo são recomendações para o mantenedor. Onde há decisão a tomar, a coluna "Recomendação" diz o que fazer e o que ela afetaria. Legenda de status e siglas das fontes: [README](README.md).

## Os três repositórios

| Repositório | O que é | Última alteração lida |
| --- | --- | --- |
| `observatorio-cfem` (este) | Regras de negócio, pesquisa, notebook e scripts de laboratório. Não é produto | `develop` de 08/11/2026 |
| `obcefem_api` | Protótipo funcional: API em FastAPI e painel web (arrecadação e distribuição da CFEM de Parauapebas e Canaã dos Carajás contra a região, o Pará e o Brasil), com dados processados e atualização diária. Publicado na Vercel | commit `ef3ce2d` (gráfico Sankey) |
| `obcefem` | Site institucional estático: página inicial e quatro páginas de dimensão (econômica, social, ambiental, institucional). Os gráficos das dimensões são marcados como "dados reais" ou "dados fictícios (protótipo)"; os links "Disponível" apontam para o painel da `obcefem_api` | commit `142a6a4` (textos das dimensões) |

O código da `obcefem_api` é um protótipo e, como `notebooks/` e `scripts/` daqui, não define regra. Mas ele já toma decisões de negócio que ninguém registrou. O trabalho abaixo é separar o que concorda, o que diverge e o que ainda não tem regra.

## 1. Onde os repositórios concordam

| Ponto | Regra daqui | O que a `obcefem_api` faz |
| --- | --- | --- |
| Os 12 municípios | RN-TER-01 | Mesma lista de 12, com os mesmos nomes |
| Fonte da CFEM | RN-CFE-01 | Só os arquivos de dados abertos da ANM |
| Valor pronto da ANM | RN-CFE-21 | Usa `VALORRECOLHIDO` sem recalcular por base de cálculo × alíquota |
| Valores nominais | RN-MOD-26 | Sem correção monetária |
| Autuação não é dinheiro em caixa | RN-CFE-17 | Diz que é o valor do auto "como a ANM o publica", não valor pago |
| Ausência não vira zero | RN-CFE-07, RN-CFE-09 | Devolve `null` onde não há valor e avisa que São Domingos do Araguaia não tem registros |
| Último dado bom | RN-VPU-03 | A atualização diária não publica se um ano encerrado perder mais de 2% do valor, ou se a região perder registros; o site fica na versão anterior |
| Titular e CPF/CNPJ visíveis | RN-CFE-18 | Mostra o titular com CPF/CNPJ |
| Dado bruto fora do Git | AGENTS.md | Só os agregados em formato colunar ficam versionados |

## 2. Divergências que pedem decisão

### D1. Distribuição: estimada pela lei ou lida do arquivo da ANM (a mais importante)

- **Aqui:** a CFEM recebida vem do `CFEM_Distribuicao.csv`, por `CodigoEnte` (RN-CFE-03), e é indicador distinto da arrecadação (RN-CFE-02). RN-CFE-10 (EM ABERTO) pergunta quais modalidades compõem a recebida.
- **Na `obcefem_api`:** a distribuição é **calculada**: valor arrecadado × percentual legal (município produtor 60%, Estado 15%, afetados 15%, União 10% desde 2018; 65/23/12 até 2017). O README justifica assim: o arquivo de distribuição publicado em 01/11/2026 estaria incompleto (cota municipal de 2023 a 2025 em torno de 15% do arrecadado, quando seria 60%; cotas estaduais e de afetados só em 2019–2022; sem a parcela da União).
- **Choque com a evidência daqui:** a nota de 31/10/2026 em RN-CFE-10 mostra que `Produtor` bate com a receita da MSC (fonte 1708) em Canaã dos Carajás (0,03% a 0,04%) e em Parauapebas (0,14% a 0,38%), o que sugere que o arquivo está certo para esses dois e que a estimativa pela lei não representa o que o município recebeu. O "15%" do README não foi reproduzido aqui; pode vir de comparar arrecadação de um período com repasse de outro, ou do mês faltante.
- **Risco:** o painel mostra uma estimativa com o nome "cota municipal", ao lado de médias. Para o usuário final, isso é CFEM recebida. Fere a separação de RN-CFE-02.
- **Recomendação:** (a) a CFEM recebida do observatório continua sendo a do arquivo (RN-CFE-03 inalterada); (b) a estimativa pela lei pode existir apenas como **análise derivada** (RN-IND-05), rotulada "estimativa" e nunca no mesmo eixo da recebida; (c) criar uma regra PROPOSTA com os percentuais legais por período, citando a Lei 13.540/2017 e a nota da ANM, e conferir os percentuais na lei antes de promover (não foram conferidos nesta comparação); (d) reproduzir o "15%" antes de aceitar que o arquivo está incompleto.
- **DECIDIDO em 08/11/2026 (mantenedor):** seguir a `obcefem_api`. Os percentuais foram conferidos nas Leis 8.001/1990 (redação da Lei 9.993/2000) e 13.540/2017 e viraram RN-CFE-25; a estimativa é análise derivada e a recebida continua do arquivo (RN-CFE-26). Dúvidas que a lei levantou, em `pendencias.md`: o início da regra nova em 01/08/2017 (a API usa 2018) e o destino da cota dos afetados enquanto não houver decreto (art. 2º, § 3º).

### D2. Duplicatas na arrecadação

- **Aqui:** RN-VPU-11 (DECIDIDA): 129 linhas do recorte dos 12 municípios repetem todos os campos de outra; o lote fica bloqueado até revisão, sem apagar linhas.
- **Na `obcefem_api`:** as linhas são somadas sem verificar duplicidade. Os totais publicados incluem as 129 repetições (inclui Parauapebas em 2025/09 e Marabá em 2026/01–03).
- **Recomendação:** o que vale é RN-VPU-11. Antes de decidir o tratamento (RN-VPU-11, Exceções), quantificar o efeito em reais das 129 linhas nos totais do painel. Se for pequeno, o mantenedor pode decidir publicar com aviso; isso contraria a regra e exige anotá-la em Exceções e em `pendencias.md`.

### D3. Total anual com mês incompleto ou ausente

- **Aqui:** RN-CFE-05 e RN-CFE-06: o ano só fecha com os 12 meses no arquivo nacional; não se publica total anual com mês ausente; os meses presentes saem como "provisório". RN-CFE-07: município sem linha num mês existente é "ausente", causa "não confirmada".
- **Na `obcefem_api`:** soma o ano que existe e o rotula "(parcial)". Considera um mês do último ano "completo" quando tem pelo menos 50% da mediana de registros por mês dos anos anteriores (a trava do histórico usa 35%). Só avalia o **último** ano; meses ausentes no meio (julho de 2025, ou os 11 meses de Bom Jesus do Tocantins em 2025) entram como soma menor, sem aviso.
- **Diferença de critério:** a regra daqui olha se o mês tem alguma linha; a API olha o volume. As duas detectam coisas diferentes: a API pega mês recente incompleto (o portal publica o mês corrente aos poucos); a regra pega mês sumido.
- **Recomendação:** adotar RN-CFE-05/06/07 como regra, e registrar o critério de volume da API como regra **PROPOSTA** complementar (mês do último ano com volume abaixo de metade da mediana é "provisório"). Os limites 50% e 35% saem de um protótipo e não têm fonte; o mantenedor define se mantém.

### D4. Autuação: qual ano usar e o que fazer com autuação sem ano

- **Aqui:** RN-CFE-14: a série usa a data de lavratura (data de publicação do arquivo). RN-CFE-16: autuação sem ano de publicação vai para uma faixa "sem ano", visível, e o total inclui as duas partes; nenhum ano é inferido por outro campo.
- **Na `obcefem_api`:** o ano é o do **processo de cobrança** (extraído do número, por exemplo `950751/2026`), descartando códigos como 8888 e 9999. Guarda `ANOPUBLICACAO` mas não o usa. Linhas sem ano são removidas, sem faixa "sem ano".
- **Efeito:** o ano da cobrança pode diferir do ano de publicação, e as autuações sem ano ficam fora de qualquer total.
- **Recomendação:** o que vale é RN-CFE-14 e RN-CFE-16; a API deve ser alinhada. A inferência do ano a partir do número do processo é exatamente o que RN-CFE-16 proíbe. Se o mantenedor preferir o ano da cobrança, é uma decisão nova que contraria RN-CFE-14 e precisa constar em Exceções.

### D5. Identificação do município: nome ou código IBGE

- **Aqui:** RN-TER-03 (DECIDIDA): o código IBGE de 7 dígitos identifica o município; RN-TER-06 e RN-TER-07 só aceitam nome com tabela de equivalência e checagem de homônimos.
- **Na `obcefem_api`:** a chave é o nome normalizado (sem acento, caixa alta) com a UF. O código IBGE é lido mas não identifica nada. Isso vale também para as médias do Pará e do Brasil, em que a chave é `UF|NOME`.
- **Efeito:** dois municípios homônimos na mesma UF, ou mudança de grafia na ANM, quebram a comparação sem erro visível.
- **Recomendação:** manter RN-TER-03. A arrecadação traz `CodigoMunicipio`; usá-lo como chave. A autuação traz só o nome (RN-TER-06).

### D6. Comparação: média por município × municípios mineradores

- **Aqui:** RN-TER-09: comparar com N municípios mineradores (por padrão os de maior CFEM recebida); N, período e modalidade ainda sem decisão. RN-TER-02 e RN-MOD-18 (PROPOSTA): razão regional é soma sobre soma.
- **Na `obcefem_api`:** compara Parauapebas e Canaã com a **média por município** do Pará e do Brasil, com dois denominadores: municípios com registro no período (padrão) ou todos (144 no Pará, 5.570 no Brasil, valores fixos no código). Há opção de tirar as duas cidades da média.
- **Efeito:** a média sobre municípios com registro ignora os 5 mil e tantos municípios sem CFEM e dá um número muito maior que a média "de todos"; o painel mostra "quantas vezes" a cidade é maior, e esse múltiplo depende da escolha. Nenhuma regra daqui cobre média nacional.
- **Recomendação:** o mantenedor decide se a média nacional/estadual entra no produto além da comparação com mineradores. Se entrar, fixar numa regra: denominador (recomendo mostrar o padrão "com registro" e declarar isso no próprio gráfico), a retirada ou não das duas cidades, e que os totais de municípios venham de fonte versionada (RN-TMP-01 proíbe fixar o ano no código; o mesmo raciocínio vale para 144 e 5.570).

### D7. Esquema, metadados e estado de validação

- **Aqui:** RN-MOD-03 (campos em português: `municipio_id, municipio_nome, ano, mes, indicador, valor, unidade, fonte, atualizado_em`), RN-VPU-09 (cada ponto leva seus metadados), RN-VPU-10 (só dado homologado alimenta os gráficos), RN-ENT-04 (painel de status por indicador).
- **Na `obcefem_api`:** resposta própria (`filtros`, `versao_dados`, `notas`, `dados`), valores em reais como número, sem unidade, fonte e estado de validação por ponto. Há `/saude` com a versão e a data do processamento, o que cobre parte de RN-ENT-04. Nenhum dado passa por homologação: o que baixa e passa pela trava de 2% é publicado.
- **Recomendação:** tratar a API como protótipo. Para virar produto, o esquema comum e o estado por ponto (provisório/homologado) precisam existir; registrar isso como requisito já decidido, não como divergência a resolver.

### D8. Dados fictícios no site institucional

- **Aqui:** não há regra sobre dados fictícios. RN-VPU-10 diz que só dados homologados alimentam os gráficos.
- **No `obcefem`:** as quatro páginas de dimensão exibem gráficos com selo "dados fictícios (protótipo)" ao lado de outros com "dados reais". Os anos e valores dos fictícios (por exemplo, séries de 2003 a 2025 na dimensão econômica) parecem reais.
- **Recomendação:** criar uma regra PROPOSTA: dado de demonstração só pode aparecer rotulado de forma visível em cada gráfico, nunca em produção. Hoje o selo já faz isso; a regra impede que o selo seja retirado sem o dado ser substituído.

### D9. Agrupamento de substâncias

- **Aqui:** sem regra.
- **Na `obcefem_api`:** "MINÉRIO DE FERRO" e "FERRO" são somados como "FERRO" (retira o prefixo "MINÉRIO DE"); o usuário pode desligar o agrupamento.
- **Recomendação:** regra PROPOSTA. A regra do prefixo é dedução do código; confirmar com o mantenedor se outros prefixos (por exemplo "MINÉRIO DE COBRE", "BAUXITA REFRATÁRIA") entram, e ancorar em uma lista de equivalência versionada, como em RN-TER-06.

### D10. Foco em Parauapebas e Canaã dos Carajás

- **Aqui:** os 12 municípios são tratados como conjunto (RN-TER-01, RN-TER-02); nenhuma regra elege dois municípios como foco.
- **Na `obcefem_api`:** o painel inteiro gira em torno das duas cidades.
- **Recomendação:** decidir se o foco é uma regra do produto (e então RN-TER ganha uma regra de município em destaque) ou só uma configuração do protótipo. Se for configuração, nada a registrar.

### D11. Arquivo de arrecadação e início da série

- **Aqui:** RN-CFE-22: arquivo completo `CFEM_Arrecadacao.csv`, série desde 2003.
- **Na `obcefem_api`:** cinco arquivos por período (2002–2006, 2007–2011, 2012–2016, 2017–2021 e 2022–2026), e a série começa em **2002**. Os períodos encerrados são processados uma vez e só relidos a cada 7 dias.
- **Efeito:** o início diverge em um ano e a lógica de "arquivo completo" não bate com a de "arquivos por período". A API também afirma que a ANM regrava todos os arquivos todo dia, o que bate com o uso do hash de conteúdo para detectar mudança, mas não está em nenhuma regra daqui.
- **Recomendação:** conferir o início real (2002 ou 2003) no arquivo atual da ANM antes de alterar RN-CFE-22. A regra de detectar mudança pelo conteúdo (e não pela data do arquivo) é boa e pode virar regra PROPOSTA em [temporalidade-e-atualizacao.md](temporalidade-e-atualizacao.md).

## 3. Resumo das decisões pedidas

| # | Decisão | Recomendação em uma linha |
| --- | --- | --- |
| D1 | Estimativa pela lei no produto? | DECIDIDO (RN-CFE-25 e RN-CFE-26); dúvidas de 2017 e dos afetados em aberto |
| D2 | Duplicatas | RN-VPU-11 vale; medir o efeito em reais |
| D3 | Ano parcial | RN-CFE-05/06/07 valem; critério de volume vira PROPOSTA |
| D4 | Ano da autuação | RN-CFE-14 e 16 valem; a API deve ser alinhada |
| D5 | Chave do município | Código IBGE (RN-TER-03 inalterada) |
| D6 | Média PA/BR | Decidir se entra; se entrar, declarar denominador |
| D7 | Esquema e homologação | Requisito já decidido; protótipo não cumpre |
| D8 | Dados fictícios | Regra PROPOSTA: rótulo visível, só em protótipo |
| D9 | Agrupar substâncias | Regra PROPOSTA com lista de equivalência |
| D10 | Foco em duas cidades | Decidir se é regra ou configuração |
| D11 | Início da série | Conferir 2002 × 2003 no arquivo atual |

## 4. O que esta comparação não verificou

- Os percentuais legais da distribuição (65/23/12 e 60/15/15/10) foram lidos no código e no README da `obcefem_api`, não na lei.
- O "15%" da cota municipal no arquivo de distribuição não foi reproduzido.
- Os totais publicados pelo painel não foram conferidos contra o arquivo da ANM; o README diz que os testes da `obcefem_api` fazem essa conferência, mas eles não foram executados aqui.
- Não foram lidas a rotina de atualização do GitHub Actions nem as regras de temporalidade além de RN-TMP-01; a coincidência com RN-TMP-02 (agenda por fonte) fica a conferir.
- O conteúdo textual das quatro páginas do `obcefem` (afirmações sobre a lei, a CFEM e os afetados) não foi confrontado com as regras do glossário.
