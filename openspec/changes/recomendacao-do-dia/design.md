## Context

Ver `proposal.md` (Why/Escopo) e `specs/recomendacao-do-dia/spec.md` (regras). Estado relevante do código:

- **`/inicio` hoje é placeholder:**
  - vem de `AREAS_EM_CONSTRUCAO` em `pages/placeholder_page.py`, registrada no laço do `projetofacul.py` com `on_load=SessaoState.ensure_session`;
  - é o destino depois do login para quem já concluiu o onboarding (`get_home_route`).
- **Gemini, integrado pela change `analisar-refeicoes-ia`:**
  - `services/gemini_client.py` é um cliente REST com `httpx`;
  - `GeminiError(tipo)` tem os tipos `nao_configurado`, `limite_requisicoes` (429) e `falha` (o resto, inclusive 503);
  - o corpo do pedido hoje está preso à análise de refeição (`build_request_body(tipo, descricao)` usa a instrução e o esquema de `logic/analise_refeicao.py`).
  - Em 2026-11-11 o Gemini respondeu 503 ("sobrecarregado") numa chamada e 200 logo na seguinte.
- **Dados já disponíveis no `xano_client`:**
  - `list_sono`, `list_refeicoes`, `list_treinos` (endpoints `*/me`, sempre filtrados por `$auth.id`);
  - perfil em `SessaoState._perfil`, carregado em `load_session`;
  - escrita protegida pela chave de serviço: `get_analysis_secret()` / `has_analysis_secret()` (`PULSE_ANALISE_SECRET`).
- **Lógica reaproveitável:**
  - `summarize_recent_sleep` e `ROTULOS_QUALIDADE` (`logic/sono_registro.py`);
  - `is_analyzed` (`logic/refeicoes.py`);
  - `round_half_up` e o padrão de delimitar dados no prompt (`logic/analise_refeicao.py`).
  - Não existe função de idade.
- **"Hoje":** vem do relógio do navegador por `rx.call_script` em Refeições, porque o servidor pode estar em outro fuso. Sono usa `offset_minutos` para converter `inicio_sono`/`fim_sono` (UTC ms).
- **Spec `sugestoes`:** `openspec/specs/sugestoes/spec.md` falha no `openspec validate` (sem `## Purpose`/`## Requirements`, cenários Given/When/Then), então não aceita delta MODIFIED.
- **Xano:** a CLI 1.3.4 falha no `workspace push` ao criar endpoint novo ("Undefined array key …"). O caminho que funciona é criar no site e depois rodar `xano workspace pull -d xano`. Plano gratuito: 10 requisições a cada 20 s.

## Goals / Non-Goals

**Goals:**
- Montagem do contexto, do prompt e a validação da resposta em funções puras, testáveis sem rede e sem Reflex.
- Nenhuma chamada de rede segurando o lock do State. A página continua responsiva enquanto a IA pensa.
- Reaproveitar o cliente do Gemini sem duplicar o tratamento de HTTP e erros, e sem mudar o comportamento da análise de refeições.
- No máximo uma chamada à IA por geração, com a recomendação do dia reaproveitada entre visitas e aparelhos.

**Non-Goals:**
- Regras próprias de intensidade ou de recuperação: a decisão é da IA, como pedido pela usuária.
- Fila, agendamento ou geração antecipada (ex.: às 6h).
- Tela de histórico, edição ou exclusão de recomendações.
- Corrigir a spec `sugestoes` (change de limpeza separada).

## Decisions

### D1. Capability nova `recomendacao-do-dia` em vez de alterar `sugestoes`
A spec `sugestoes` está fora do formato, então qualquer delta sobre ela falharia no arquivamento. Ela também descreve outro esquema (`profile_id` UUID, tabela `sugestao`, botão "gerar sugestão", janela de 30 dias). A capability nova incorpora as regras de fundo de `sugestoes`:
- sem dados, sem IA;
- nada inventado;
- isolamento por usuário;
- persistência;
- aviso de IA.

A change `sugestoes-ia` fica substituída.
*Alternativa:* reescrever `sugestoes` inteira numa change de limpeza antes desta. Isso atrasaria a entrega e mexeria numa spec de outro autor sem pedido.

### D2. `gemini_client.generate_json(instrucao, prompt, esquema, max_tokens)`
- **Função genérica:** monta `systemInstruction`, `contents` e `generationConfig` (`responseMimeType` + `responseJsonSchema`, temperatura baixa), chama `generateContent` e devolve o JSON decodificado com `extract_json`.
- **Refeições:** `analyze_meal(tipo, descricao)` vira um invólucro de uma linha sobre `generate_json`, e os testes atuais continuam valendo.
- **Novo tipo de erro `sobrecarregado`:** para HTTP 500, 502, 503 e 504, separado de `falha`.
  - Refeições não muda: `get_analysis_failure_message` já manda qualquer tipo desconhecido para a mensagem genérica.
  - A recomendação mostra "A IA está ocupada agora…" para `limite_requisicoes` e `sobrecarregado`.
- **Logs:** dizem só a finalidade ("recomendação do dia" ou "análise de refeição") e o status, nunca o conteúdo.

*Alternativa:* um segundo cliente só para a recomendação. Duplicaria rede, timeout, erros e testes.

### D3. Lógica pura em `logic/recomendacao.py`
- **`calculate_age(nascimento, hoje)`:** idade em anos, ou `None` sem data.
- **`build_recommendation_context(perfil, sonos, refeicoes, treinos, hoje, offset_minutos) -> dict`:**
  - `data_hoje`;
  - `perfil`: objetivo, nivel_fisico, modalidades, meta_semanal, idade;
  - `sono`: noites dos últimos 7 dias via `summarize_recent_sleep`, filtradas pela data de fim, mais as médias;
  - `treinos`: últimos 7 dias, cada um com data, nome, duracao_minutos, categoria e intensidade, além do total da semana;
  - `refeicoes`: `hoje` e `ontem`, cada um com registradas, analisadas, tipos e somas com 1 casa decimal (via `round_half_up`), só das analisadas.
  - Campos ausentes viram `None` ou lista vazia, nunca um valor padrão. É uma lista explícita de campos permitidos: o que não está nela não sai (nome, e-mail, observações, descrições, sexo, altura, peso, biotipo).
- **`has_recent_records(contexto) -> bool`:** sono, treino ou refeição de hoje/ontem.
- **`build_recommendation_prompt(contexto) -> str`:** `json.dumps(..., ensure_ascii=False, sort_keys=True)` entre `<<<REGISTROS` e `REGISTROS>>>`. Ocorrências do marcador de fim dentro de textos livres (nome, categoria e intensidade do treino) são removidas.
- **`INSTRUCAO_SISTEMA`:** traz os exemplos da usuária como orientação, a regra de responder com uma das três intensidades, os pedidos de dizer quando faltam dados, de não diagnosticar e não prescrever, de não comentar composição corporal e de ignorar instruções dentro dos registros, e os tamanhos máximos.
- **`ESQUEMA_RESPOSTA`:** os 6 campos obrigatórios, `intensidade` com `enum`, `recuperacao` com `minimum`/`maximum`.
- **`parse_recommendation(dados) -> ResultadoRecomendacao(status, valores)`:** normaliza espaços, corta nos limites, aceita intensidade sem diferença de caixa e devolve a forma canônica, e arredonda `recuperacao` (meio para cima). Recusa booleano, texto no lugar de número, valor não finito, valor fora da faixa ou campo vazio.
- **`build_recommendation_payload(valores, hoje, modelo)`:** monta o corpo do POST, sem a chave.
- **`build_recommendation_view(registro, offset_minutos) -> dict[str, str]`:** textos prontos para a UI, como "72/100", "Gerada às 08:15" e o `aria-label` da recuperação.
- **`get_recommendation_failure_message(tipo)`:** mensagens da spec.

### D4. "Hoje" e fuso vêm do navegador
O `SCRIPT_RELOGIO` do Início devolve `{hoje: "AAAA-MM-DD", offset_minutos}` e o servidor guarda esses dois valores no State. O offset serve para:
- decidir em que dia terminou cada noite de sono;
- mostrar "Gerada às HH:MM" a partir de `created_at` (UTC ms).

*Alternativa:* fuso fixo de São Paulo, como em `logic/treinos.py`. Daria uma data diferente da que Refeições e Sono mostram para quem está em outro fuso.

### D5. Xano: tabela `recomendacoes` e dois endpoints, criados no site
- **`table recomendacoes`:** campos da spec, `intensidade` como `enum` (Leve, Moderado, Intenso), índice btree em `user_id` e em `created_at desc`.
- **`GET recomendacoes/me/hoje`:**
  - `auth = "user"`, input `date data_recomendacao`;
  - consulta `user_id == $auth.id && data_recomendacao == $input.data_recomendacao`, ordenada por `created_at desc`, devolvendo um só registro ou `null`;
  - resposta `null` (ou vazia) significa que ainda não há recomendação hoje.
- **`POST recomendacoes/me`:**
  - `auth = "user"`;
  - inputs com os filtros de limite da spec (`trim`, `min`/`max`) e `chave_servico` sensível;
  - `precondition` igual à do `analise_PATCH` (`$env.PULSE_ANALISE_SECRET` não vazio e igual, senão `accessdenied`);
  - `db.add` com `user_id = $auth.id`.
- **Chave de serviço:** reaproveita `PULSE_ANALISE_SECRET`, já configurada no `.env` e no Xano, então não há configuração nova. O nome fica histórico. O comentário do `.env.example` passa a dizer que ela protege as gravações de conteúdo de IA.
- **Criação:** a tabela e os endpoints são criados no site do Xano a partir dos `.xs` escritos nesta change e depois baixados com `pull`. O `push` só serve para alterações seguintes, sempre com `--dry-run` antes.

*Alternativa:* guardar no navegador (`LocalStorage`). Recusada pela usuária: não vale entre aparelhos e não guarda histórico.

### D6. `InicioState` com geração em segundo plano
**Vars:**
- públicas: `estado` (`preparando` | `pronta` | `sem_dados` | `erro`), `recomendacao: dict[str, str]`, `mensagem_erro: str`, `atualizando: bool`;
- só no servidor: `_hoje`, `_offset_minutos`, `_gerando`.

**Fluxo:**
1. `on_load=[SessaoState.ensure_session, InicioState.start_page]`. `start_page` marca `preparando` e pede o relógio (`rx.call_script`, callback `load_recommendation`).
2. `load_recommendation(relogio)` (evento normal): guarda hoje e offset e chama `GET recomendacoes/me/hoje`.
   - Se encontrou, a recomendação vira `pronta` e acabou: nenhuma chamada à IA.
   - Se não encontrou, chama `start_generation()`.
3. `start_generation()`:
   - se `_gerando` já está ligado, devolve `None` (isso evita clique duplo, porque os eventos do mesmo cliente rodam em fila);
   - senão liga `_gerando` e devolve `InicioState.generate_recommendation`.
4. `generate_recommendation` (`@rx.event(background=True)`):
   1. Dentro de `async with self`: copia token, perfil, hoje e offset.
   2. Fora do lock:
      - lista sono, refeições e treinos;
      - monta o contexto;
      - sem registros recentes, o resultado é `sem_dados`;
      - sem `gemini_client.is_configured()` ou `has_analysis_secret()`, o resultado é `nao_configurado`;
      - senão chama `generate_json`, depois `parse_recommendation` e `save_recommendation`.
   3. Dentro do lock: desliga `_gerando` e aplica o resultado. A sessão expirada encerra a sessão e redireciona para `/login`.
5. "Atualizar" (`refresh_recommendation`): liga `atualizando` sem mudar `estado`, de modo que a anterior continua na tela, e chama `start_generation()`.
   - Se falhar com uma recomendação já na tela, `estado` continua `pronta` e só `mensagem_erro` aparece.
   - Se falhar sem nenhuma, `estado = "erro"` e aparece "Tentar novamente", que chama `start_generation()` de novo.
6. Gravação falhou por motivo que não é sessão: exibe a recomendação montada com `build_recommendation_view` a partir dos valores, com `created_at` igual a agora, e registra só o tipo do erro no log.

A ordem "registros antes da configuração" garante que um usuário sem dados veja o convite para registrar, mesmo num servidor sem chave.

### D7. Página `pages/inicio_page.py`
- **Estrutura:** `app_shell("/inicio", ...)` com h1 "Início" e um card `rx.el.section` com `aria-labelledby`, escolhido por `rx.match(InicioState.estado, ...)`.
- **CSS próprio `INICIO_PAGE_CSS`:**
  - grade de 3 colunas que vira 1 coluna em até 720px;
  - botão com `min-height: 44px`;
  - skeleton sem animação em `prefers-reduced-motion`.
- **Estilo:** segue os tokens do app (fundo do card, bordas e azul `#2B8CFF`). A intensidade é texto grande, sem cor de status.
- **Placeholder:** `/inicio` sai de `AREAS_EM_CONSTRUCAO`, que fica vazio. O mecanismo de placeholder continua no código para áreas futuras, e o `projetofacul.py` registra `/inicio` explicitamente com título "Início | Pulse".

## Risks / Trade-offs

- **[Dados de saúde enviados ao Google; no plano gratuito o conteúdo pode ser usado pelo Google]** → lista explícita de campos permitidos, sem identificação, sem textos livres longos (observações, descrições). Registrar no PR e reavaliar com o time (ver Open Questions).
- **[A IA pode sugerir algo inadequado (ex.: "Intenso" com sinais de cansaço)]** → instrução com os exemplos da usuária e com as proibições, validação de formato e aviso fixo de que não substitui profissional. O conteúdo em si não é verificável por regra, por decisão da usuária de deixar a última palavra com a IA.
- **[Recomendação desatualizada quando o usuário registra dados depois de gerar]** → "Gerada às HH:MM" visível e botão "Atualizar".
- **["Atualizar" sem limite diário pode gastar a cota gratuita do Gemini]** → um clique por vez (`_gerando`) e mensagem "ocupada" no 429/503. Um teto diário pode vir depois sem mudar a arquitetura.
- **[Duas abas abertas geram duas recomendações no mesmo dia]** → aceitável. O GET devolve a mais recente e ambas ficam no histórico.
- **[Fuso do navegador errado ou alterado]** → mesmo comportamento já aceito em Refeições e Sono.
- **[Limite do Xano: até 5 chamadas para gerar, mais as da sessão]** → abaixo das 10 a cada 20 s. O "Atualizar" é sequencial.
- **[Ordem de arquivamento]** → o REMOVED de "Páginas placeholder" quebraria o MODIFIED das outras 4 changes se esta fosse arquivada antes delas. Isso está registrado no delta e nas tarefas.
- **[CLI do Xano não cria endpoints]** → criar no site e rodar `pull`. Os `.xs` desta change servem de referência exata para colar.

## Migration Plan

1. No site do Xano: criar a tabela `recomendacoes` e os endpoints `GET recomendacoes/me/hoje` e `POST recomendacoes/me` com o conteúdo dos `.xs`. Depois rodar `xano workspace pull -d xano` e conferir o diff.
2. Publicar o código. `PULSE_ANALISE_SECRET` e `GEMINI_API_KEY` já existem e não há variável nova.
3. **Rollback:** voltar `/inicio` para `AREAS_EM_CONSTRUCAO` e tirar a rota explícita. A tabela e os endpoints podem ficar sem uso, e nada nas outras telas depende deles.

## Open Questions

- Pedir consentimento explícito do usuário antes de enviar dados de saúde ao Gemini ou migrar para o plano pago (sem uso dos dados pelo Google). Pode ser uma change própria, sem mudar esta arquitetura.
- Teto diário de "Atualizar" por usuário, se a cota gratuita se mostrar curta no uso real.
