# Tasks: registrar-refeicoes

Cada task cabe em até 2h. **[BACK]** = Xano / lógica / States; **[FRONT]** = componentes Reflex. Tasks com **(aceite)** geram código grande e são apresentadas antes de aplicar.

## 1. Back-end Xano (etapa 1)

- [x] 1.1 [BACK] `Refeicoes`: `user_id` → `user` com índice, `descricao` (texto), `gorduras` e `analise_ia`, `proteinas`/`carboidratos` como decimal. Verificar: pull do servidor igual a `xano/table/refeicoes.xs`.
- [x] 1.2 [BACK] Endpoints `GET/POST refeicoes/me` e `DELETE refeicoes/me/{refeicao_id}` (criados no site) e remoção dos 5 CRUDs públicos. Verificar: 15/15 verificações reais com duas contas (lista isolada, exclusão cruzada recusada, calorias enviadas ignoradas, tipo/descrição/data inválidos recusados, sem token → 401, públicos → 404).
- [x] 1.3 [BACK] Atualizar `docs/domain-model.md` (Refeição): `user_id` → User, `data_refeicao: date`, `descricao` texto (3–500), macros `decimal` em gramas opcionais, `analise_ia`, regra "analisada = `analise_ia` preenchido" e RLS por token. Verificar: revisão da usuária.

## 2. Back-end Reflex: lógica, cliente e State

- [x] 2.1 [BACK] `logic/refeicoes.py`: `OPCOES_TIPO`, `suggest_meal_type(hora)`, `validate_refeicao(dados, hoje)`, `is_analyzed(refeicao)`, `sort_refeicoes`, `calculate_daily_totals(refeicoes, hoje)`, `count_pending_today`, `format_date_br`; `tests/test_refeicoes_logic.py` cobrindo faixas de horário, descrição 2/3/500/501, data futura/vazia, tipo fora da lista, ordenação, totais só de hoje e só analisadas, zero sem valores. Verificar: `pytest` passa.
- [x] 2.2 [BACK] `xano_client`: `list_refeicoes`, `create_refeicao` (envia só data, tipo, descrição), `delete_refeicao`; testes com `httpx.MockTransport` (Bearer, corpo sem campos nutricionais, 404 → `nao_encontrado`). Verificar: `pytest` passa.
- [x] 2.3 [BACK] `states/refeicoes_state.py`: `load_meals` (skeleton/erro/tentar de novo), `open_new_meal` (data e tipo pelo navegador), `save_meal` (validação, spinner, anti-duplo-clique, `# TODO: integração futura com IA`, toast, recarregar), `ask_delete`/`confirm_delete`/`cancel_delete`; testes com Xano simulado (sucesso, falha amigável, validação sem chamada HTTP, exclusão). Verificar: `pytest` passa. **(aceite)**

## 3. Front-end: página, cards e estado vazio (etapa 2)

- [x] 3.1 [FRONT] `pages/refeicoes_page.py` com `app_shell("/refeicoes")`, cabeçalho, botão "+ Nova refeição", 4 cards de totais, nota de pendentes, estado vazio, skeleton e erro com "Tentar novamente"; registrar a rota com `ensure_session` + `load_meals` e tirar `/refeicoes` dos placeholders. Verificar: `reflex compile` e testes de rota e textos. **(aceite)**
- [x] 3.2 [FRONT] Tema global com destaque azul (`rx.theme` + `--accent-*` no `app_shell`). Verificar: teste do CSS e captura do Perfil sem ciano.

## 4. Front-end: modal e formulário (etapa 3)

- [x] 4.1 [FRONT] Modal `rx.dialog` "Nova refeição": Data (máx. hoje), Tipo (`rx.select` com as 4 opções, item com fundo azul e check), Descrição (textarea), erros por campo em `aria-live`, erro geral, botão "Salvar" com disquete/spinner; layout em coluna única no celular com Salvar sempre visível. Verificar: teste das 4 opções exatas e dos atributos de acessibilidade. **(aceite)**

## 5. Salvar, listar e excluir (etapa 4)

- [x] 5.1 [FRONT] Lista de refeições (chip do tipo, data dd/mm/aaaa, descrição, calorias/macros ou "Aguardando análise", lixeira com `aria-label`) ligada ao State; `rx.alert_dialog` de exclusão; toasts "Refeição registrada"/"Refeição excluída". Verificar: `reflex compile` e testes de componente.

## 6. Validação, responsividade e microinterações (etapa 5)

- [x] 6.1 [FRONT] CSS: grid de totais 4→2 colunas, cabeçalho empilhado no celular, modal ~560px/tela cheia no celular, hover/elevação, scale .98, fade/scale do modal, fade-in dos itens, `prefers-reduced-motion`, alvos de 44px. Verificar: teste do CSS.
- [x] 6.2 Navegador (Chrome headless): estado vazio → registrar → "Aguardando análise" e totais 0 → recarregar (persistência) → excluir → vazio; 360/768/1280/1920px sem rolagem horizontal; select com exatamente 4 opções; foco e Esc no modal. Verificar: resultados no PR.
- [x] 6.3 [BACK] Limite do Xano (D10): 429 → `limite_requisicoes` no cliente; `SessaoState.load_session` reaproveita a confirmação por 60 s com o mesmo token (zerada em `clear_session`); mensagem própria do limite na sessão e em Refeições; botão "Tentar novamente" na tela de erro da sessão. Verificar: testes de cache (hit, expirado, token trocado, sair), 429 e botão; navegação rápida por 6 páginas no navegador sem erro.
- [x] 6.4 Privacidade com duas contas pela tela e pela API; `pytest` completo; `openspec validate registrar-refeicoes --strict`; PR da branch `feat/registrar-refeicoes`. Verificar: saídas no PR.
