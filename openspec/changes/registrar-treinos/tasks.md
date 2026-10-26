# Tasks: registrar-treinos

Cada task cabe em até 2h. **[BACK]** = Xano / lógica / States; **[FRONT]** = componentes Reflex. Tasks com **(aceite)** geram código grande e são apresentadas antes de aplicar.

## 1. Back-end Xano

- [x] 1.1 [BACK] `Treinos`: sincronizar `xano/table/treinos.xs` com o servidor (campos `user_id`, `nome`, `duracao_minutos`, `categoria`, `intensidade`, `observacoes` já existem) e adicionar índice em `user_id`. Verificar: pull do servidor igual ao arquivo.
- [x] 1.2 [BACK] Endpoints `GET/POST treinos/me` e `DELETE treinos/me/{treino_id}` (criados no site) e remoção dos 5 CRUDs públicos `treino*`. Verificar: pull igual aos `.xs`; chamadas com duas contas (lista isolada, exclusão cruzada → 404, `user_id` enviado ignorado, inválidos → 400, sem token → 401, públicos → 404).
- [x] 1.3 [BACK] Atualizar `docs/domain-model.md` (Treino, Exercício planejado, relacionamentos, regras). Verificar: revisão da usuária.

## 2. Back-end Reflex: lógica, cliente e State

- [x] 2.1 [BACK] `logic/treinos.py`: limites dos campos, `get_today_sao_paulo`, `validate_treino(dados, hoje)`, `build_treino_payload`, `sort_treinos`, `format_date_br`; `tests/test_treinos_logic.py` (duração 0/1/1440/1441/decimal/vazia, nome 1/2/60/61/espaços, categoria 40/41, intensidade 20/21, observações 500/501, data futura só pelo dia, 22h SP = hoje, ordenação, payload sem `user_id`). Verificar: `pytest` passa.
- [x] 2.2 [BACK] `xano_client`: `list_treinos`, `create_treino`, `delete_treino`; testes com `httpx.MockTransport` (Bearer, corpo só com campos permitidos, 404 → `nao_encontrado`, 429). Verificar: `pytest` passa.
- [x] 2.3 [BACK] `states/treinos_state.py`: `start_page`/`load_workouts` (skeleton/erro/tentar de novo), `open_new_workout` (data de hoje em SP, rascunho mantido), `save_workout` (validação, spinner, anti-duplo-clique, toast, recarregar), `ask_delete`/`confirm_delete`/`cancel_delete`; testes com Xano simulado. Verificar: `pytest` passa. **(aceite)**

## 3. Front-end: página, cabeçalho e estado vazio

- [x] 3.1 [FRONT] `pages/treinos_page.py` com `app_shell("/treinos")`, cabeçalho (haltere, título, subtítulo, "+ Novo treino"), estado vazio, skeleton e erro com "Tentar novamente"; registrar a rota com `ensure_session` + `start_page` e tirar `/treinos` dos placeholders. Verificar: `reflex compile` e testes de rota e textos. **(aceite)**

## 4. Front-end: modal e formulário

- [x] 4.1 [FRONT] Modal `rx.dialog` "Novo treino": grid 2 colunas (Data/Duração; Nome; Categoria/Intensidade em texto com `max_length`; Observações), labels associados, erros em `aria-live`, erro geral, "Salvar treino" com spinner. Verificar: teste dos placeholders, limites e atributos de acessibilidade. **(aceite)**

## 5. Salvar, listar e excluir

- [x] 5.1 [FRONT] Card do treino (nome, data dd/mm/aaaa, chips só quando preenchidos, "N min", observações, lixeira com `aria-label`) ligado ao State; `rx.alert_dialog` "Excluir este treino?"; toasts "Treino registrado"/"Treino excluído". Verificar: `reflex compile` e testes de componente.

## 6. Validação, responsividade e microinterações

- [x] 6.1 [FRONT] CSS: cabeçalho empilhado no celular, modal ~560px/tela cheia no celular com Salvar fixo, hover/elevação, scale .98, fade/scale, fade-in, `prefers-reduced-motion`, alvos de 44px. Verificar: teste do CSS.
- [x] 6.2 Navegador: vazio → registrar → lista → recarregar → excluir → vazio; 360/768/1280/1920px sem rolagem horizontal; foco e Esc no modal; data padrão em SP. Verificar: Chrome (Playwright) contra o Xano real, 39/39 verificações. O foco ao fechar o modal/confirmação é devolvido explicitamente ao botão "Novo treino" (o Radix não o reconhecia como gatilho).
- [x] 6.3 RLS com duas contas pela API (status e corpo registrados); `pytest` completo; `openspec validate registrar-treinos --strict`; conferir consistência domain-model × spec × `xano/table/treinos.xs`. Verificar: 13 chamadas reais com as contas de teste A e B; 251 testes; change válida; campos e limites iguais nos quatro lugares.
- [ ] 6.4 PR da branch `feat/registrar-treinos` (aguardando autorização para commit e push).
