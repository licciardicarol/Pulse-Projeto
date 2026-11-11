## 1. Back-end: Xano e configuração

- [x] 1.1 (1h) Criar `xano/api/lunas_workspace/refeicoes/me/refeicao_id/analise_PATCH.xs` conforme o design D3 (auth de usuário, `chave_servico` sensível comparada com `$env.PULSE_ANALISE_SECRET` antes de tudo, dono pelo token com `notfound`, faixas 0–5000 / 0–500 / resumo 1–300, `db.patch` só dos 5 campos); verificar revisando que a ordem das `precondition` e os campos alterados batem com a spec "Gravação protegida da análise"
- [ ] 1.2 (30min, manual da usuária) Criar a variável de ambiente `PULSE_ANALISE_SECRET` no Xano e publicar o endpoint; verificar no Xano que uma chamada sem a chave responde 403 e uma com a chave e refeição de outro usuário responde 404
- [x] 1.3 (30min) Acrescentar `GEMINI_API_KEY`, `GEMINI_MODEL` e `PULSE_ANALISE_SECRET` (sem valores) ao `.env.example`; verificar com `git check-ignore .env` que o `.env` continua fora do Git e que o diff não contém nenhum valor de chave
- [x] 1.4 (1h) Adicionar `xano_client.save_meal_analysis(token, refeicao_id, valores)` (PATCH com os 5 campos + `chave_servico` lida do ambiente); verificar com testes em `tests/test_xano_client.py` para caminho, corpo, ausência da chave no ambiente e mapeamento de 401/403/404/429

## 2. Back-end: lógica pura e cliente da IA

- [x] 2.1 (1h30) Criar `projetofacul/logic/analise_refeicao.py` com `ESQUEMA_RESPOSTA`, `INSTRUCAO_SISTEMA` e `build_analysis_prompt(tipo, descricao)`; verificar com testes de que o prompt contém o tipo e a descrição entre delimitadores e nenhum outro dado do usuário
- [x] 2.2 (1h30) Implementar `parse_analysis`, `build_analysis_payload` e `get_analysis_failure_message`; verificar com testes: resposta válida com arredondamento meio-para-cima (10.55 → 10,6), faixas (12000 kcal, macro negativo), booleano no lugar de número, campo ausente, `reconhecido` falso, resumo vazio e resumo cortado em 300 caracteres
- [x] 2.3 (2h) Criar `projetofacul/services/gemini_client.py` (`analyze_meal`, `GeminiError`) conforme o design D1; verificar com testes usando `httpx.MockTransport`: URL com modelo padrão e com `GEMINI_MODEL`, cabeçalho `x-goog-api-key`, corpo com esquema JSON, sem chave → `nao_configurado` sem requisição, 429 → `limite_requisicoes`, timeout/5xx/`blockReason`/`finishReason`/texto não-JSON → `falha`, e logs sem a descrição

## 3. Back-end: State do Reflex

- [x] 3.1 (1h30) Em `logic/refeicoes.py` e `RefeicoesState`: incluir `resumo` na visão do item, campos `_analisando` e `_erros_analise` e `rebuild_meal_views()` com `estado` (`analisada`/`analisando`/`pendente`) e `erro_analise`; verificar com testes em `tests/test_refeicoes_logic.py` e `tests/test_refeicoes_state.py`
- [x] 3.2 (2h) Implementar `analyze_meal` em segundo plano e encadeá-lo no `save_meal` e no botão "Analisar" (design D4); verificar com testes de State (Gemini e Xano simulados): sucesso troca a refeição e atualiza os totais sem novo `GET`, falhas deixam a mensagem certa sem gravar, chamada duplicada chama a IA uma vez, sem configuração não chama a IA, `nao_autorizado` redireciona para `/login`, falha ao criar não analisa e abrir a página não chama a IA

## 4. Front-end: componentes Reflex

- [x] 4.1 (1h) Trocar o subtítulo e adicionar o aviso fixo de IA abaixo dos cards de totais em `pages/refeicoes_page.py`; verificar em `tests/test_refeicoes_page.py` que o subtítulo novo aparece, "Em breve" não aparece e o aviso está na página
- [x] 4.2 (2h) Atualizar `meal_item` com os três estados (analisada: selo "Estimado por IA" + resumo; analisando: "Analisando…" com `role="status"`; pendente: selo, mensagem de falha com `aria-live` e botão "Analisar" com `aria-label` descritivo e 44 px), com CSS respeitando `prefers-reduced-motion`; verificar em `tests/test_refeicoes_page.py` e com `reflex compile --dry`

## 5. Validação

- [x] 5.1 (30min) Rodar `pytest` (suíte inteira) e `reflex compile --dry`; verificar que tudo passa
- [x] 5.2 (15min) Rodar `openspec validate analisar-refeicoes-ia --strict`; verificar que a change é válida
- [ ] 5.3 (30min, manual da usuária) Com `GEMINI_API_KEY` e `PULSE_ANALISE_SECRET` configurados e o endpoint publicado, registrar "2 ovos mexidos e 1 pão francês" e ver "Analisando…" virar valores, selo e resumo com os cards atualizados; registrar "asdfgh" e ver a mensagem de alimentos não reconhecidos; conferir a página em 360px sem rolagem horizontal
