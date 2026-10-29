# Privacidade e licenças

Regras sobre dados pessoais, registros individuais, acesso restrito e reuso de dados de terceiros. Legenda de status e siglas das fontes: [README](README.md).

### RN-PRI-01: CPF e CNPJ nunca entram na camada tratada
- **Status:** DECIDIDA
- **Regra:** A camada tratada e publicada não deve guardar nem publicar CPF ou CNPJ; do titular de uma autuação só se guarda o nome.
- **Motivo:** Os arquivos brutos da ANM contêm campos identificadores, e o nome do titular já exige revisão jurídica antes de qualquer exibição.
- **Exemplo:** O validador dos arquivos da ANM leu os CSVs completos sem exportar CPF/CNPJ nem nomes de titulares.
- **Exceções:** O titular pode ser pessoa física; a decisão de exibir o nome continua em aberto e sujeita à revisão jurídica (RN-CFE-18).
- **Fonte:** DECISÃO-MANTENEDOR de 24/10/2026 (resposta à pergunta 7); VAL-15/10 §Rodada adicional; DECISÕES §Bloco 3 (nome da empresa: guardar agora, exibir depois); README do repositório e `.gitignore`.
- **Relacionadas:** RN-CFE-18, RN-FON-15, RN-ENT-06

### RN-PRI-02: Registros individuais não são coletados nem publicados
- **Status:** PROPOSTA
- **Regra:** O observatório não deve coletar nem publicar registros individuais de pessoas, e só deve usar dados agregados.
- **Motivo:** Evita exposição de pessoas e risco com a LGPD.
- **Exemplo:** Para pobreza, usa-se a consulta agregada pública do CECAD, nunca registros do Cadastro Único.
- **Fonte:** CONSUMO §Sociedade, serviços e segurança (Pobreza). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-PRI-03, RN-PRI-08

### RN-PRI-03: Agregar microdados antes de expor
- **Status:** PROPOSTA
- **Regra:** Microdados (RAIS, CAGED, SIM) devem ser agregados antes de serem expostos, e os identificadores que não forem necessários devem ser excluídos.
- **Motivo:** Reduz o risco de reidentificação e o volume exposto.
- **Exemplo:** A RAIS entra como vínculos agregados por setor, sexo e escolaridade por município, e não como vínculo individual.
- **Fonte:** CONSUMO §Economia e mercado de trabalho. Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-PRI-02, RN-FON-19

### RN-PRI-04: Proteger grupos muito pequenos
- **Status:** PROPOSTA
- **Regra:** Indicadores calculados sobre grupos muito pequenos devem ser protegidos, e o recorte só deve ser publicado quando houver agregação municipal.
- **Motivo:** Números de grupos pequenos podem identificar pessoas.
- **Exemplo:** Algumas variáveis de entorno do Censo têm escala de setor censitário; é preciso confirmar se existe agregação municipal publicada.
- **Fonte:** CONSUMO §Sociedade, serviços e segurança (Veículos, infraestrutura censitária, favelas, entorno). Não consta em DECISÕES, BLOCOS, LAB-19/10 ou VAL-15/10.
- **Relacionadas:** RN-PRI-03

### RN-PRI-05: Verificar a licença antes de republicar
- **Status:** DECIDIDA
- **Regra:** Antes de republicar o dado de um produto ou portal, deve-se confirmar o ano, a licença, as colunas e o recorte municipal do arquivo ou da exportação concreta.
- **Motivo:** Um portal que abre não garante que o dado possa ser redistribuído.
- **Exemplo:** FAPESPA, Atlas da Violência, SEEG, World Bank Pink Sheet, IDSC, TSE e INEP abriram (HTTP 200) no laboratório de 17/10/2026, mas nenhum arquivo ou licença foi verificado (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** LAB-19/10 §4 (Portais de apoio), §7 (Próximos passos, item 4); VAL-15/10 §Matriz operacional (FAPESPA, ICMS e Barômetro; IDSC e ranking CLP).
- **Relacionadas:** RN-PRI-06, RN-ENT-03, RN-ENT-10

### RN-PRI-06: Licenças de redistribuição ainda não confirmadas
- **Status:** EM ABERTO
- **Regra:** O mantenedor deve confirmar a licença de redistribuição de cada fonte antes de a camada publicada e o CSV aberto a incluírem, começando por FAPESPA, IDSC e SEEG.
- **Motivo:** Nenhuma das fontes de decisão registra licenças confirmadas.
- **Exemplo:** BLOCOS diz que a planilha do SEEG é guardada no repositório, e a licença de redistribuição do SEEG não foi verificada (conflito 16).
- **Fonte:** PESQUISA §Conclusões principais (item 4); CONSUMO §Contrato de dados para o front-end; BLOCOS §Bloco 5 (CO₂); DECISÃO-MANTENEDOR de 24/10/2026 (conflito 16 em aberto).
- **Relacionadas:** RN-FON-15, RN-PRI-05, RN-ENT-10

### RN-PRI-07: Recortes por aluno e professor só até 2020
- **Status:** DECIDIDA
- **Regra:** Os recortes de matrícula e docente por pessoa do Censo Escolar só devem ser usados até 2020, e o observatório deve usar as tabelas já agregadas por município.
- **Motivo:** A restrição decorre da LGPD.
- **Exemplo:** As tabelas `escola` e `turma` vão até 2024 ou 2025; `matricula` e `docente` vão só até 2020.
- **Fonte:** DECISÕES §Censo Escolar; BLOCOS §Bloco 4.
- **Relacionadas:** RN-PRI-02, RN-FNT-11

### RN-PRI-08: Não usar a área restrita do CECAD
- **Status:** PROPOSTA
- **Regra:** O observatório não deve usar o módulo restrito do CECAD ("sem Bolsa Família"), reservado a gestores e técnicos, e só deve usar as consultas agregadas públicas.
- **Motivo:** Usar a área restrita seria contornar controle de acesso.
- **Exemplo:** A pobreza e o percentual de famílias pobres usam a consulta pública agregada, com data-base e definição registradas.
- **Fonte:** CONSUMO §Sociedade, serviços e segurança (Pobreza); MAPA-TEMAS §Sociedade. DECISÕES §Rotas de coleta por fonte registra apenas "sem API; só download manual".
- **Relacionadas:** RN-FON-05, RN-PRI-02, RN-FNT-16

### RN-PRI-09: Declaração de uso do Earth Engine
- **Status:** DECIDIDA
- **Regra:** O cadastro do projeto no Earth Engine deve ser preenchido pelo responsável pela conta, com respostas verdadeiras sobre a finalidade, escolhendo a modalidade de uso não comercial só se ela corresponder ao projeto.
- **Motivo:** O formulário verifica elegibilidade não comercial e o responsável responde pelas declarações.
- **Exemplo:** O laboratório de 17/10/2026 deixou o Earth Engine PENDENTE porque `GEE_PROJECT` estava vazio (transcrito do relatório LAB-19/10, não conferido no JSON).
- **Fonte:** VAL-15/10 §Como repetir os testes (item 8); LAB-19/10 §4, §6.
- **Relacionadas:** RN-FON-09, RN-FNT-13

### RN-PRI-10: Autorizações de conta com escopo mínimo
- **Status:** DECIDIDA
- **Regra:** O pipeline só pode usar autorização de escopo mínimo no Google Cloud (leitura e consulta). O acesso amplo de edição e exclusão observado no consentimento do laboratório não é aceito. Como autenticar continua em aberto em RN-FON-09 e deve caber nesse limite.
- **Motivo:** Uma autorização ampla permitiria alterar ou apagar arquivos do Drive e recursos do Google Cloud em caso de erro ou vazamento da credencial; a consulta de dados públicos não precisa disso.
- **Exemplo:** A célula de autenticação do laboratório abriu um consentimento com acesso amplo de edição e exclusão no Drive e no Google Cloud; a autenticação não foi concluída (transcrito do relatório VAL-15/10, não conferido no JSON). O notebook é só de testes e não vai para produção, então o consentimento serve de evidência; a regra vale para o pipeline.
- **Fonte:** DECISÃO-MANTENEDOR de 28/10/2026; VAL-15/10 §Pendências externas e limites desta execução; DECISÃO-MANTENEDOR de 24/10/2026 (conflito 7 não decidido).
- **Relacionadas:** RN-FON-09
