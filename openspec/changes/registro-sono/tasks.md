## 1. Back-end Xano (tabela e endpoints)

- [x] 1.1 Atualizar `xano/table/sono.xs`: adicionar `user_id` (ref. `user`), `duracao_minutos` (int), `observacoes` (text, trim), `updated_at` (timestamp) e índice btree em `user_id`, e trocar `qualidade_sono` para int. Verificar revisando o diff contra `refeicoes.xs`.
- [x] 1.2 Criar `xano/api/lunas_workspace/sono/me_GET.xs` (lista por `$auth.id`) e `sono/me_POST.xs` (inputs tipados; preconditions de fim > início, 15–1440 min, fim ≤ agora e sem sobreposição; calcula `duracao_minutos`). Verificar revisando que nenhum input aceita `user_id`.
- [x] 1.3 Criar `sono/me/sono_id_PATCH.xs` e `sono/me/sono_id_DELETE.xs` (404 para registro inexistente ou de outro usuário; o PATCH ignora o próprio id na sobreposição e atualiza `updated_at`). Remover `sono_GET.xs`, `sono_POST.xs` e `sono/sono_id_*.xs`. Verificar listando `xano/api/lunas_workspace/sono*`.
- [x] 1.4 Atualizar a seção Sono de `docs/domain-model.md` (dono por `user_id`, qualidade 1–5, duração e observações).

## 2. Back-end app (lógica pura e cliente)

- [x] 2.1 Criar `projetofacul/logic/sono_registro.py` com opções de qualidade, `parse_local_datetime`, `to_utc_ms`/`from_utc_ms` (offset em minutos), `calculate_duration_minutes`, `format_duration` e `format_period` (horário de Brasília, virada às 00:00). Verificar com `tests/test_sono_registro.py` (8h, 7h 30min, 45min, —, intervalo com e sem meia-noite).
- [x] 2.2 Adicionar a `sono_registro.py` as funções `validate_sono` (obrigatórios, ordem, 15 min–24 h, futuro, qualidade, 500 caracteres), `find_overlap` (encostados permitidos, ignora id em edição), `sort_sono`, `build_sono_payload`, `build_registro_view` e `summarize_recent_sleep`. Verificar com testes unitários de cada regra e cenário da spec.
- [x] 2.3 Adicionar ao `xano_client` as funções `list_sono`, `create_sono`, `update_sono` e `delete_sono`. Verificar em `tests/test_xano_client.py` (método, caminho, token e corpo) com o transporte simulado já usado.

## 3. State

- [x] 3.1 Criar `projetofacul/states/sono_state.py` (`SonoState`) com campos do formulário, `erros`, `erro_geral`, `duracao_texto`, `pode_salvar`, `salvando`, `carregando`, `erro_lista`, `registros`, `editando_id`, `exclusao_id`, `excluindo` e `fuso_offset_minutos`, importando `ESTILO_TOAST_SUCESSO` e `get_failure_message` de `refeicoes_state.py`. Eventos: `start_page` (após o guarda; `call_script` do fuso), `load_records`, `update_field` e `select_qualidade`. Verificar com `tests/test_sono_state.py` (carregar, erro de carregamento, recálculo da duração, sessão expirada).
- [x] 3.2 Implementar `save_sono` (bloqueio de duplo clique, conflito local, create/update, toast, reset, lista reordenada, `nao_autorizado` → `/login`, `invalido` → mensagem de conflito e recarregar, outras falhas → erro com "Tentar novamente"), mais `start_edit`, `cancel_edit`, `ask_delete`, `set_delete_open` e `confirm_delete`. Verificar com testes de cada cenário de salvar, editar e excluir da spec.

## 4. Front-end (componentes Reflex)

- [x] 4.1 Criar `projetofacul/pages/sono_page.py` injetando `REFEICOES_PAGE_CSS` + `SONO_PAGE_CSS` (só o que não existe em Refeições), cabeçalho `ref-header` com `moon`, card do formulário (início/fim 50/50, chips de qualidade com estrela e `aria-pressed`, observações com contador, rodapé com duração e "Salvar sono"/"Salvar alterações"/"Cancelar edição") e erros por campo com `aria-describedby`. Verificar com `tests/test_sono_page.py` (textos, ids, atributos ARIA, handlers).
- [ ] 4.2 Implementar a área de registros com as classes de Refeições: skeleton, estado vazio com lua, erro com "Tentar novamente", item da lista (data, intervalo, duração, estrelas e rótulo, observações, Editar/Excluir) e confirmação de exclusão, com os breakpoints de Refeições (640px). Verificar com testes de componente e conferência visual no navegador em 1280px e 360px.
- [x] 4.3 Registrar `/sono` em `projetofacul.py` com `on_load=[SessaoState.ensure_session, SonoState.start_page]` e remover `/sono` de `AREAS_EM_CONSTRUCAO`. Verificar com `tests/test_routes.py` (rota aponta para `sono_page`, continua privada e navbar com Sono ativo).

## 5. Verificação final

- [x] 5.1 Rodar `pytest` com todos os testes passando, `reflex compile` sem erros e `openspec validate registro-sono --strict` OK.
- [ ] 5.2 Teste ponta a ponta, depois de publicar no Xano: criar, sobrepor (bloqueado), editar, excluir, ver o estado vazio, ver o celular em 360px e navegar só com teclado. Registrar o resultado no PR.
