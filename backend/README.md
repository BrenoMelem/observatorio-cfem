# Back-end — Fase 1

API de leitura da camada publicada, separada dos scripts de laboratório. Lê somente `populacao.json` de `OBS_PUBLICADO_DIR`; por padrão, procura `output/observatorio/publicado/` na raiz. Não coleta dados nem cria publicação. O arquivo deve vir do pipeline homologado. Se não existir, a resposta traz `sem_dado_validado` e `dados: []`.

```powershell
uv sync --project backend
uv run --project backend uvicorn app.main:app --app-dir backend
uv run --project backend pytest backend/tests
uv run --project backend ruff check backend/app backend/tests
```

Rotas: `GET /api/v1/dimensoes/{social|economica|ambiental|institucional}`, o mesmo caminho com `.csv`, `GET /api/v1/indicadores/status` e `GET /saude`. Filtros: `municipio_id`, `ano_inicio`, `ano_fim`. O CSV inclui fonte, edição, método e limitações em cada linha. O manifesto `data/indicadores.json` descreve os sete indicadores conhecidos; os demais gráficos do site ainda não têm identificador e não recebem números desta API. Valores fictícios não entram na camada publicada.

A população só é exposta quando existe publicação válida no esquema comum. CFEM, commodities, despesa e indicadores sem pipeline aparecem como lacunas. O selo de dado real das páginas estáticas não comprova homologação. A versão dos dados é um hash do conteúdo lido. `503` indica arquivo publicado inválido; `404`, dimensão desconhecida; `422`, filtro inválido. A ausência de arquivo não é erro operacional.

## Assistente — Fase 2

`POST /api/v1/assistente` recebe `pergunta` e `contexto()` do `assistente.js` (campos `pagina`, `dimensao`, `tema`, `periodo`, `comparacoes`, `graficos`), com `historico` opcional de até cinco textos. Retorna `resposta`, `citacoes` (indicador, fonte, período, edição), `limitacoes` e `acoes`. O front do outro repositório ainda precisa integrar a chamada e aplicar somente ações permitidas; esta API não modifica o site. O `contexto()` atual não envia valores dos gráficos.

Somente perguntas pontuais sobre população estimada de um município e um ano com observação validada recebem número. Sem ano, usa o maior ano publicado; sem município único ou para comparações/crescimento, explica a lacuna. CFEM, emprego, saúde, saneamento e demais indicadores aguardam publicação homologada. O serviço nunca usa os valores embutidos nas páginas nem calcula com o LLM. Busca explicações apenas em `data/indicadores.json`, glossário e regras de modelo/entrega. As ações são objetos de uma lista fechada; o front deve validar novamente os parâmetros antes de executá-las.

`OBS_LLM_MODO=mock` (padrão) não exige chave e é usado nos testes. `OBS_LLM_MODO=openai` exige `OPENAI_API_KEY` e `OPENAI_MODEL` por variável de ambiente; a API Chat Completions é usada apenas para redigir uma introdução. Qualquer número na introdução gerada é rejeitado, e o fato numérico é anexado deterministicamente pela consulta. Não há ferramentas, execução de código ou acesso a fonte externa pela pergunta. A chamada do provedor usa `store: false`, tempo limite de 12 segundos e resposta curta. A integração externa não foi executada nesta fase. Contrato consultado: [documentação oficial da OpenAI](https://platform.openai.com/docs/api-reference/chat/create).

O corpo da requisição é limitado a 8 KiB, a pergunta a 500 caracteres e o histórico a cinco entradas de 500 caracteres. A taxa padrão é de 20 requisições/minuto por endereço no processo. Esse contador em memória é apenas defesa local; implantação com várias instâncias precisa de limite global na plataforma, ainda EM ABERTO. As metas de precisão, latência, disponibilidade e custo seguem EM ABERTO (RN-ENT-08).

Avaliação offline: `backend/tests/test_avaliacao_assistente.py` compara 24 respostas dos 12 municípios para 2025 e 2026 com as referências independentes do IBGE versionadas em `data/`. Os testes adicionais verificam citação, recusa por ausência, tentativa de injeção, ação permitida e tamanho de entrada. Isso avalia o modo mock e o recorte de população; não é uma medição de LLM real, latência de Vercel ou custo.
