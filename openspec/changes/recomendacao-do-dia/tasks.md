## 1. Back-end: Xano

- [x] 1.1 (1h) Escrever `xano/table/recomendacoes.xs`, `xano/api/lunas_workspace/recomendacoes/me/hoje_GET.xs` e `xano/api/lunas_workspace/recomendacoes/me_POST.xs` conforme o design D5:
  - tabela com os campos da spec e `intensidade` enum;
  - GET com `user_id == $auth.id` e `data_recomendacao`, mais recente primeiro, um registro ou `null`;
  - POST com `precondition` de `chave_servico` igual à de `analise_PATCH.xs`, filtros de limite e `user_id = $auth.id`.
  - Verificar revisando, campo a campo, contra a seção "Modelos de dados envolvidos" e o requisito "Gravação protegida e isolada por usuário" da spec.
- [x] 1.2 (30min, manual da usuária) Criar a tabela e os dois endpoints no site do Xano, colando o conteúdo dos `.xs`, e rodar `xano workspace pull -d xano`.
  - Verificar que o `pull` trouxe os 3 arquivos com `guid` e sem diferença de conteúdo.
  - Verificar no Xano que um POST sem `chave_servico` responde 403 e não cria linha.
  - Resultado (2026-11-13):
    - o `pull` trouxe os 3 arquivos com `guid`, mudando só a formatação;
    - `push --dry-run` respondeu "No changes to push";
    - sem token, POST e GET respondem 401;
    - o caso com token válido e chave errada não foi executado (precisa de login), mas a `precondition` está no endpoint publicado.
- [x] 1.3 (15min) Atualizar o comentário de `PULSE_ANALISE_SECRET` no `.env.example`: a chave passa a proteger também as recomendações. Verificar que o diff não contém nenhum valor.
- [x] 1.4 (1h) Adicionar `xano_client.get_today_recommendation(token, data)` e `xano_client.save_recommendation(token, valores)`.
  - Verificar em `tests/test_xano_client.py`: caminho e parâmetro `data_recomendacao`; resposta `null`/vazia vira `None`; corpo do POST só com os campos da spec mais `chave_servico`; sem chave no ambiente, nenhuma requisição; mapeamento de 401/403/429.

## 2. Back-end: cliente da IA

- [x] 2.1 (1h30) Extrair `gemini_client.generate_json(instrucao, prompt, esquema, max_tokens)` e reescrever `analyze_meal` sobre ela, conforme o design D2. Adicionar o tipo `sobrecarregado` para HTTP 500/502/503/504.
  - Verificar que os testes atuais de `tests/test_gemini_client.py` e `tests/test_refeicoes_state.py` continuam passando, com o caso 503 ajustado para `sobrecarregado`.
  - Verificar com teste novo que a mensagem de refeição para `sobrecarregado` continua sendo a genérica.

## 3. Back-end: lógica pura

- [x] 3.1 (2h) Criar `projetofacul/logic/recomendacao.py` com `calculate_age`, `build_recommendation_context` e `has_recent_records`, conforme o design D3.
  - Verificar em `tests/test_recomendacao_logic.py`:
    - janela de 7 dias para sono e treinos;
    - hoje/ontem para refeições;
    - somas só das analisadas;
    - ausentes como `None`/vazio;
    - idade só com data de nascimento;
    - campos proibidos (nome, e-mail, observações, descrições, sexo, altura, peso, biotipo) nunca aparecem no contexto;
    - "só registros antigos" sem registros recentes.
- [x] 3.2 (1h30) Implementar `INSTRUCAO_SISTEMA`, `ESQUEMA_RESPOSTA` e `build_recommendation_prompt`.
  - Verificar com testes:
    - os registros vão como JSON entre os delimitadores;
    - o marcador de fim é removido do nome do treino;
    - a instrução contém os três exemplos de intensidade e as proibições (diagnóstico, prescrição, composição corporal);
    - o esquema exige os 6 campos com o `enum` de intensidade.
- [x] 3.3 (1h30) Implementar `parse_recommendation`, `build_recommendation_payload`, `build_recommendation_view` e `get_recommendation_failure_message`.
  - Verificar com testes:
    - 71.6 vira 72 e 0,5 arredonda para cima;
    - "intenso" vira "Intenso";
    - "Muito forte", 140, texto no lugar de número, booleano e campo vazio são recusados;
    - textos são cortados nos limites;
    - "72/100", "Gerada às 08:15" no offset do usuário e o `aria-label` da recuperação saem certos;
    - as 4 mensagens são exatas.

## 4. Back-end: State do Reflex

- [x] 4.1 (2h) Criar `projetofacul/states/inicio_state.py` com `start_page`, `load_recommendation`, `start_generation` e `generate_recommendation` (segundo plano), conforme o design D6.
  - Verificar em `tests/test_inicio_state.py`, com Xano e Gemini simulados:
    - a recomendação de hoje existente é exibida sem chamar a IA;
    - sem a de hoje, gera, grava e exibe;
    - a de ontem não é reaproveitada;
    - sem registros recentes, mostra `sem_dados`, sem IA e sem gravação;
    - sem configuração, mensagem de indisponível sem IA;
    - 429/503 mostram a mensagem de ocupada;
    - resposta inválida não grava;
    - falha ao gravar ainda exibe;
    - 401 limpa a sessão e redireciona para `/login`;
    - falha ao listar mostra a mensagem de registros.
- [x] 4.2 (1h) Implementar `refresh_recommendation` e "Tentar novamente".
  - Verificar com testes:
    - clique duplo resulta em uma única chamada à IA;
    - durante a atualização a anterior continua em `recomendacao`, com `atualizando` ligado;
    - se atualizar falhar, a anterior fica, com `mensagem_erro`;
    - se der certo, troca a recomendação e o horário;
    - o pedido usa a noite de sono recém-registrada.

## 5. Front-end: componentes Reflex

- [x] 5.1 (2h) Criar `projetofacul/pages/inicio_page.py` com o card "Recomendação de hoje" nos estados preparando, pronta, sem dados e erro, mais o aviso fixo de IA e o `INICIO_PAGE_CSS`, conforme o design D7 e o requisito "Acessível e responsivo".
  - Verificar em `tests/test_inicio_page.py`:
    - textos exatos;
    - "Massa magra" ausente;
    - aviso uma única vez;
    - `role="status"` e `aria-live`;
    - `aria-label` do botão e da recuperação;
    - links para `/sono`, `/refeicoes` e `/treinos`;
    - grade de 3 colunas virando 1 em `@media (max-width: 720px)`;
    - `min-height: 44px`;
    - `prefers-reduced-motion`.
- [x] 5.2 (1h) Registrar `/inicio` em `projetofacul/projetofacul.py` com título "Início | Pulse" e `on_load=[SessaoState.ensure_session, InicioState.start_page]`, e tirar `/inicio` de `AREAS_EM_CONSTRUCAO`.
  - Verificar com os testes de rotas e navegação: `/inicio` privada, item Início ativo, destino pós-login inalterado, nenhuma rota privada com a mensagem de área em construção.
  - Verificar com `reflex compile --dry`.

## 6. Validação

- [x] 6.1 (30min) Rodar `pytest` (suíte inteira) e `reflex compile --dry`.
  - Verificar que tudo passa.
  - Verificar com busca no `.web` compilado que não aparecem a chave da IA, a chave de serviço nem `generativelanguage`.
- [x] 6.2 (15min) Rodar `openspec validate recomendacao-do-dia --strict` e verificar que a change é válida. Registrar no PR:
  - a ordem de arquivamento: depois de `registro-sono`, `registrar-treinos`, `registrar-peso` e `relatorios`;
  - que `sugestoes-ia` fica substituída;
  - que nenhuma biblioteca nova foi instalada.
- [x] 6.3 (30min, manual da usuária) Com a tabela e os endpoints publicados:
  - abrir `/inicio` sem registros recentes e ver o convite com os 3 links;
  - registrar sono, refeição e treino, abrir `/inicio` e ver "Preparando sua recomendação…" virar o card completo;
  - recarregar e ver a mesma recomendação, sem nova geração;
  - clicar em "Atualizar" e ver o novo horário;
  - conferir em 360px que não há rolagem horizontal.
  - Resultado (2026-11-13): com uma conta nova, a usuária registrou os dados e informou que o fluxo funcionou.
