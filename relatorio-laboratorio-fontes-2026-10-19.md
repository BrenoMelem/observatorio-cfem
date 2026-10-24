# Observatório CFEM: Laboratório de fontes de dados

Região de Integração Carajás (PA) · Relatório de evidências · 19 de outubro de 2026

> Convertido do PDF original em 24/10/2026. As figuras foram transcritas em texto.

Este relatório explica, em linguagem simples, o que foi efetivamente testado no Google Colab, o que os resultados permitem concluir e o que ainda falta para transformar conexões em indicadores publicados. A execução analisada ocorreu em 17 de outubro de 2026. A fonte de verdade dos estados e das contagens é a saída da tabela resumo do notebook executado "laboratorio_fontes_observatorio_cfem_v3 (1).ipynb".

## 1. Objetivo e contexto

O Observatório CFEM pretende reunir indicadores da Região de Integração Carajás, formada por 12 municípios do Pará, com atenção especial à mineração e à Compensação Financeira pela Exploração de Recursos Minerais (CFEM). A proposta inclui população, economia, sociedade, ambiente e finanças públicas. Antes de construir gráficos do produto final, era necessário saber se cada rota de coleta responde, se contém o recorte municipal necessário e quais credenciais ou tratamentos serão exigidos.

O laboratório fez provas pequenas e controladas: consultou uma API, leu cabeçalhos de CSV, verificou a existência de colunas, importou uma biblioteca ou abriu a página de um portal. Isso reduz o risco de desenhar um indicador sobre uma fonte que depois não pode ser consumida. Uma prova aprovada confirma apenas o que ela testou; não equivale a uma série histórica já coletada, validada e pronta para publicação.

## 2. Como interpretar os resultados

**OK** — a prova descrita naquela linha passou. Exemplo: a API devolveu os 12 nomes esperados ou um CSV apresentou a coluna necessária. Ainda podem faltar filtro, período, unidade, limpeza e validação.

**ATENÇÃO** — apareceu uma limitação real da fonte ou uma dependência/erro contextual. Não significa que o dado não exista. Exemplo: o VPM do AMB foi visto com UF, mas sem coluna municipal; no DETRAN-PA, a tentativa terminou em HTTP 502 após o reparo do certificado.

**PENDENTE** — a prova de dados não pôde avançar sem uma ação manual, como fornecer uma chave FRED ou configurar um projeto Google Cloud. É diferente de dizer que a chamada falhou.

**FALHA** — a chamada da própria prova falhou e foi registrada com esse estado. A tabela final não contém nenhuma linha FALHA. Há mensagens técnicas "NameError" dentro da evidência do BigQuery; elas integram uma linha ATENÇÃO, pois o projeto e o cliente não haviam sido configurados. Por isso, não devem ser contadas as seis fontes que falharam.

## 3. Painel consolidado

Unidade do gráfico: provas registradas na tabela resumo, não fontes distintas. Foram 24 provas para 18 fontes; algumas fontes aparecem em mais de uma prova. A contagem é: OK 16; ATENÇÃO 4; PENDENTE 4; FALHA 0.

**Figura 1 (transcrita). Distribuição das 24 provas por estado** — fonte: tabela resumo do notebook executado em 17/10/2026.

| Estado | Provas |
| --- | ---: |
| OK | 16 |
| ATENÇÃO | 4 |
| PENDENTE | 4 |
| FALHA | 0 |

### O que foi de fato consumido

A figura seguinte agrupa cada uma das 18 fontes responsáveis pela prova mais profunda desta execução. "Teste de portal" inclui sete páginas que abriram e o painel DETRAN-PA, que terminou em HTTP 502. Resposta de API indica retorno de registros ou valores; cabeçalho CSV confirma estrutura, não a série inteira. As três fontes bloqueadas por configuração são FRED, Base dos Dados e MapBiomas/GEE. Na execução de 19/10/2026, o FRED foi desbloqueado; restam Base dos Dados e MapBiomas/GEE.

**Figura 2 (transcrita). Até onde o teste chegou em cada fonte (18 fontes)** — classificação pela prova mais profunda de cada fonte; não representa volume de dados coletados.

| Nível alcançado | Fontes |
| --- | ---: |
| Teste de portal | 8 |
| Resposta de API | 4 |
| Cabeçalho de CSV | 2 |
| Biblioteca importada | 1 |
| Bloqueio de configuração | 3 |

**Tabela 1. Síntese por fonte.** Quando houver mais de uma prova, a coluna Estado preserva o conjunto de resultados e o texto explica a consequência prática.

| Fonte | O que foi testado | Estado final | O que significa na prática |
| --- | --- | --- | --- |
| IBGE Localidades | 12 códigos e nomes | OK | Território conferido: 12/12. |
| IBGE SIDRA | 8 agregados e valor no 6579 | OK (2 provas) | API responde; falta definir a série final. |
| SICONFI (DCA) | Anexo I-E, 2025 | OK | 337 linhas na 1ª página; faltam contas e paginação. |
| ANM CFEM | Cabeçalhos de 3 CSVs | OK (3 provas) | Estrutura legível; falta filtrar arquivos completos. |
| ANM AMB / VPM | 2 CSVs de produção | ATENÇÃO (2) | Há UF, mas não coluna municipal. |
| FRED | Chave e séries ferro/cobre | OK | Com chave (19/10): ferro e cobre de jan/1980 a jul/2026. |
| IPEADATA | Recorte ADMISNC | OK | Canaã e Parauapebas aparecem na série testada. |
| PySUS | Importação e versão | OK | Pacote disponível; microdados não coletados. |
| Base dos Dados / BigQuery | Projeto, dry run e população | 2 PENDENTE; 1 ATENÇÃO | Sem projeto; consulta real não ocorreu. |
| MapBiomas / GEE | Configuração e assets | PENDENTE | Sem projeto; asset não testado. |
| FAPESPA | Página do portal | OK | Portal abre; falta exportação municipal. |
| Atlas da Violência | Página do portal | OK | Portal abre; falta testar dados específicos. |
| SEEG | Página do portal | OK | Portal abre; falta testar planilha. |
| World Bank Pink Sheet | Página do portal | OK | Portal abre; preços não baixados. |
| IDSC | Página do portal | OK | Portal abre; faltam arquivos/indicadores. |
| TSE Eleitorado | Página de dados abertos | OK | Portal abre; falta dataset municipal. |
| INEP Censo Escolar | Página do Censo | OK | Portal abre; faltam arquivos municipais. |
| DETRAN-PA Frota | Painel de frota | ATENÇÃO | TLS reparado, mas servidor retornou HTTP 502. |

Leitura correta do painel: 16 provas OK não significam 16 bases completas. Sete desses OK são apenas páginas de portais acessíveis por HTTP; três são cabeçalhos de CSV da CFEM. As provas de consumo efetivo continuam restritas ao que cada linha declara.

## 4. Resultado por fonte

### IBGE Localidades e IBGE SIDRA

Localidades: os 12 códigos e nomes municipais foram conferidos (12/12, OK). Isso fixa o território da RI Carajás e evita somar municípios errados. SIDRA: os metadados de oito agregados candidatos responderam, e uma consulta ao agregado 6579 trouxe um valor municipal para Canaã dos Carajás no período 2026 (OK). O primeiro teste confirma a descoberta de tabelas; o segundo confirma uma resposta de dado. Antes de publicar a população, é preciso fixar variável, unidade, período e a distinção entre estimativa e Censo.

### SICONFI — Declaração de Contas Anuais (DCA)

A consulta ao Anexo I-E da DCA retornou 337 linhas na primeira página para o exercício 2025, com campos como conta, valor e código IBGE (OK). Isso mostra uma rota viável para as finanças municipais. Ainda não se escolheu quais contas e estágios contábeis compõem cada indicador, nem se percorreu toda a paginação. Portanto, 337 é o tamanho da primeira página do teste, não quantidade final de registros do observatório.

### ANM — CFEM: arrecadação, distribuição e autuação

Os três arquivos responderam com cabeçalhos legíveis (3 provas OK). Arrecadação usa CodigoMunicípio e representa CFEM gerada pela extração no município; distribuição usa Código Ente e representa o repasse recebido; autuação traz município por nome e representa cobrança da fiscalização, com separador de CSV ";". São medidas distintas e não podem ser somadas. O teste leu cabeçalho e amostra, sem baixar e filtrar os arquivos inteiros para os 12 municípios. A autuação também exige uma tabela de equivalência entre nomes e códigos IBGE.

### ANM — AMB e valor da produção mineral (VPM)

Os cabeçalhos de Producao_Bruta.csv e Producao_Beneficiada.csv foram lidos com o separador real ",". Ambos registraram ATENÇÃO: aparecem UF e substância, mas não uma coluna de município. Essa é uma limitação de granularidade para o VPM municipal. O VPM pode servir como contexto do Pará; não deve ser apresentado como valor específico de Canaã e Parauapebas. A CFEM municipal pode ser analisada separadamente, sem renomeá-la como VPM.

### FRED e World Bank Pink Sheet

Na execução de 17/10/2026, o FRED ficou PENDENTE porque FRED_API_KEY não estava configurada. Numa nova execução do mesmo notebook, em 19/10/2026, com a chave configurada, a API respondeu e as duas séries foram consultadas com sucesso (OK): minério de ferro (PIORECRUSDM) e cobre (PCOPPUSDM), ambas mensais, de janeiro de 1980 a julho de 2026. O World Bank Pink Sheet teve página acessível (OK), mas nenhum arquivo de preços foi baixado ou validado. A estratégia é usar a API do FRED para a série recorrente; como ela já começa em 1980, o Pink Sheet só seria necessário para anos anteriores.

Sobre a chave de acesso: a API do FRED é o serviço web do Federal Reserve Bank of St. Louis que permite a programas e aplicações buscar dados econômicos dos sites FRED e ALFRED. Pelos termos de uso, a chave é obrigatória para desenvolver programas com dados do FRED, cada aplicação deve ter uma chave própria e cada usuário de uma aplicação deve usar a sua própria chave. Para o observatório, isso significa: a chave é guardada como segredo (Colab ou GitHub), nunca escrita no código nem compartilhada, e quem rodar o notebook usa a própria chave, criada gratuitamente no site do FRED. A documentação de consulta de dados está em fred.stlouisfed.org/docs/api/fred/.

### IPEADATA e PySUS

IPEADATA: a série ADMISNC apresentou a coluna territorial TERCODIGO e registros para Canaã e Parauapebas (OK). Isso comprova o recorte municipal dessa série de admissões, mas não testa aqui todas as demais séries nem calcula o saldo de emprego. PySUS: a biblioteca foi importada, versão 2.11.7 (OK). A importação confirma que a ferramenta está disponível no ambiente; não comprova download, qualidade ou agregação de microdados do SUS.

### Base dos Dados / BigQuery e MapBiomas / Google Earth Engine

A Base dos Dados teve três registros: configuração do projeto PENDENTE, consulta de população PENDENTE e tentativa de verificação temporal ATENÇÃO. O projeto GCP_PROJECT estava vazio; por isso o cliente BigQuery não foi criado e as seis tentativas internas de dry run produziram NameError. Não houve consulta faturada nem confirmação da atualização das tabelas nesta execução. MapBiomas/GEE ficou PENDENTE porque GEE_PROJECT não estava definido; nenhum asset, banda, classe ou área municipal foi testado. A dependência é de configuração e autenticação, não prova ausência de dados.

### Portais de apoio

FAPESPA, Atlas da Violência, SEEG, World Bank Pink Sheet, IDSC, TSE Eleitorado e INEP Censo Escolar devolveram HTTP 200 (7 provas OK). Em todos esses casos, OK significa que a página abriu; ainda é preciso encontrar o arquivo ou a exportação concreta, conferir ano, licença, colunas e recorte municipal. DETRAN-PA Frota ficou em ATENÇÃO: a cadeia TLS do servidor veio incompleta; após montagem de um pacote de certificados, a segunda tentativa recebeu o HTTP 502. Não se conclui que dados de frota não existem. Para o produto, o plano anterior aponta a Senatran como fonte principal e o DETRAN-PA como alternativa a avaliar.

## 5. O processo de depuração: sintoma, causa e correção

### 5.1. Um CSV que parecia ter só uma coluna

Sintoma: no notebook de referência, o CSV do AMB parecia inteiro em uma única coluna, impedindo a procura por "município". Causa: o leitor usava ";" fixo, enquanto os arquivos testados empregam ",". Correção: detectar o delimitador no cabeçalho antes de interpretar as colunas. Resultado: os dois cabeçalhos passaram a ser lidos corretamente; só então foi possível observar a limitação real de terem UF, mas não município. Uma conclusão sobre cobertura territorial só é válida depois de validar a leitura do arquivo.

### 5.2. Uma chave que parecia ausente

Sintoma: o teste do FRED podia dizer "chave ausente" mesmo que o segredo estivesse salvo no Colab. Causa: o código antigo procurava FRED API_KEY na lista de nomes internos do módulo de segredos, em vez de tentar ler o segredo. Correção: consultar a chave diretamente e tratar a ausência com uma exceção controlada. Resultado desta execução: a leitura foi corrigida, mas a chave de fato não estava configurada; por isso o estado final permaneceu PENDENTE. Corrigir o código não substitui configurar a conta. Na execução de 19/10/2026, com a chave configurada, o teste passou (ver seção 4).

### 5.3. Um projeto de nuvem que não era do executor

Sintoma: o notebook de referência continha um identificador de projeto Google Cloud já preenchido e pedia upload de uma chave JSON. Isso poderia faturar consultas em projetos alheios e expor credenciais. Causa: configuração pessoal herdada do exemplo. Correção: deixar GCP_PROJECT vazio por padrão, autenticar a conta de quem executa e exigir escolha explícita do próprio projeto; manter um ensaio de custo antes de qualquer consulta. Resultado: BigQuery parou de maneira segura, marcando PENDENTE. O NameError na célula seguinte é efeito da falta do cliente, e não uma demonstração de que seis tabelas públicas estão indisponíveis.

### 5.4. Certificados incompletos e o erro do DETRAN-PA

Sintomas: chamadas HTTPS a servidores públicos apresentaram erro de confiança no certificado. O diagnóstico mostrou que o portal do DETRAN-PA enviava apenas o certificado do site, sem o intermediário. Causa: cadeia de certificados incompleta no servidor ou no caminho de conexão, não falta de dados. Correção: o laboratório tentou montar manualmente a cadeia por AIA, mantendo a verificação TLS. A segunda tentativa do DETRAN-PA chegou ao servidor, mas recebeu o HTTP 502; ficou em ATENÇÃO. Um teste diagnóstico ao IBGE com a verificação desligada retornou ao HTTP 200, reforçando a hipótese de confiança TLS, mas essa prática não deve virar método de coleta.

### 5.5. Outras proteções metodológicas

O SICONFI procura dinamicamente um exercício com linhas, em vez de pressupor que o ano corrente já está publicado. O notebook também trocou uma rotina de versão depreciada do PySUS por uma leitura de metadados do pacote. Para portais, distingue "página abriu" de "arquivo municipal foi encontrado". Essas escolhas tornam o teste reprodutível e reduzem falsos positivos.

## 6. Limitações atuais

Dependências manuais: selecionar um projeto Google Cloud próprio com BigQuery habilitado e autenticar a conta; cadastrar/autorizar o projeto no Earth Engine e informar GEE_PROJECT. Só depois disso se podem testar as consultas reais da Base dos Dados e os assets do MapBiomas. O notebook preserva a consulta BigQuery desligada até a revisão do custo.

Limitações das fontes e do alcance do ensaio: o AMB/VPM observado está por UF, sem coluna municipal; os três CSVs da CFEM foram verificados por cabeçalho e amostra, não por coleta completa; a página HTTP 200 dos portais não prova disponibilidade de tabela municipal; PySUS foi apenas importado; DETRAN-PA permaneceu com resposta 502. Cada indicador ainda precisa de período, variável, unidade, tratamento de ausentes e regra de atualização.

## 7. Próximos passos para consumir os dados no produto

A figura 3 mostra o caminho entre uma prova de acesso e um indicador publicado. O laboratório avançou nas sondas; definir a medida, coletar toda a série, validar e atualizar são etapas do produto, ainda não resultados deste teste.

**Figura 3 (transcrita). Do teste ao consumo no produto** — fluxo planejado; as etapas futuras não são contadas como testes concluídos.

1. **Provar acesso** — 24 provas registradas (concluído).
2. **Definir o indicador** — variável, período e unidade.
3. **Coletar os municípios** — 12 códigos IBGE como recorte.
4. **Tratar e validar** — conferir valores e origem.
5. **Publicar e atualizar** — série, data e fonte visíveis.

Próximos passos:

1. Implementar primeiro uma série de população pelo SIDRA para os 12 municípios: escolher agregado, variável, período e unidade; coletar, padronizar por código IBGE, validar e publicar uma versão tratada. A prova atual mostra que essa rota responde sem credencial.
2. Completar as rotas diretas já abertas: paginar e selecionar contas/estágio no SICONFI; baixar os CSVs completos da CFEM, filtrar os municípios e guardar arrecadação, distribuição e autuação em séries separadas. Definir se o mês será preservado no esquema comum antes de agregar a visualização por ano.
3. Configurar o Google Cloud com credenciais próprias (o FRED já foi configurado e validado). No BigQuery, descobrir tabela e ano mais recente em execução, confirmar as colunas municipais, fazer dry run com limite de custo e só então consultar RAIS, IDEB, TSE e Censo Escolar que forem necessários. Para o GEE, confirmar o asset MapBiomas e calcular área por município e ano; não extrapolar o VPM estadual para município.
4. Para IPEADATA, escolher cada série e testar período e unidade antes de calcular emprego; para PySUS, escolher uma base concreta e validar recorte municipal. Nos portais de apoio, localizar o arquivo/exportação e sua licença. Se a rota do DETRAN-PA continuar instável, avaliar a fonte principal de frota indicada no planejamento.
5. Registrar em um manifesto de indicadores a origem, o ano, a unidade, a frequência e o método de cada medida. Guardar dados brutos e tratados separadamente, incluir data de atualização e impedir publicação quando as validações falharem. Esse fluxo permite que o professor e futuros usuários rastreiem de onde veio cada número.

## Glossário mínimo

CFEM: compensação paga pela exploração de recursos minerais. DCA: declaração fiscal anual usada no SICONFI. AMB: Anuário Mineral Brasileiro. VPM: valor da produção mineral. BigQuery: serviço de consultas em nuvem. GEE: Google Earth Engine, plataforma de análise espacial. Dry run: estimativa de processamento sem executar a consulta de dados.

## Base documental e critério de evidência

Fonte dos resultados e contagens: saída da célula resumo de "laboratorio_fontes_observatorio_cfem_v3 (1).ipynb", executado no Colab em 17/10/2026. A validação do FRED vem de uma nova execução do mesmo notebook, em 19/10/2026. O arquivo com o nome sem sufixo não contém saídas de execução.
