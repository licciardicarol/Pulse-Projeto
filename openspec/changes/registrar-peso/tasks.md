# Tasks: registrar-peso

Cada task cabe em até 2h. **[BACK]** = Xano / lógica / States; **[FRONT]** = componentes Reflex. Tasks com **(aceite)** geram código grande e são apresentadas antes de aplicar.

## 1. Back-end Xano (etapa 1)

- [x] 1.1 [BACK] `Registro_Peso`: campo `user_id` (referência a `user`) com índice; `Peso` → `peso`, `Data_Horario` → `data_horario` (feito no site). Verificar: `xano workspace pull` igual ao esperado em `xano/table/registro_peso.xs`.
- [x] 1.2 [BACK] Endpoints `GET/POST registro_peso/me` e `DELETE registro_peso/me/{registro_peso_id}` (criados no site a partir do XanoScript) e remoção dos 5 CRUDs públicos. Verificar: chamadas reais com duas contas (lista isolada, exclusão cruzada recusada, `user_id` enviado ignorado, peso/casas/data futura inválidos recusados, sem token → 401, públicos → 404).
- [x] 1.3 [BACK] `docs/domain-model.md` (RegistroDePeso): tabela `Registro_Peso`, `user_id` → User, `peso` decimal(5,2) 20–400, `data_horario` timestamp UTC exibido em UTC−03:00, `observacoes` não implementado, nota sobre `peso_meta` e `MedidaCorporal` futuros. Verificar: revisão da usuária.

## 2. Back-end Reflex: lógica, cliente e State

- [x] 2.1 [BACK] `logic/peso.py`: `parse_weight` (vírgula/ponto), `validate_registro_peso(dados, agora)`, `combine_date_time` → milissegundos em UTC−03:00, `from_milliseconds` (ms → data/hora UTC−03:00), `sort_registros`, `get_current_weight`, `calculate_change_since_first`, `format_weight`/`format_change` (pt-BR, sinal, "—"); `tests/test_peso_logic.py` (20/400 limites, 19,99/400,01, 3 casas, texto, futuro, mesma data, fuso 17:38 ida e volta, peso atual por data e não por criação, 1 registro → "—"). Verificar: `pytest` passa.
- [x] 2.2 [BACK] `xano_client`: `list_registros_peso`, `create_registro_peso` (envia só `peso` e `data_horario`), `delete_registro_peso`; testes com `httpx.MockTransport`. Verificar: `pytest` passa.
- [x] 2.3 [BACK] `states/peso_state.py`: `start_page` (skeleton/erro/tentar de novo), formulário com data/hora padrão = agora, `save_weight` (validação, spinner, anti-duplo-clique, limpar só o peso, toast, recarregar), `ask_delete`/`confirm_delete`; testes com Xano simulado. Verificar: `pytest` passa. **(aceite)**

## 3. Front-end: página, formulário e estado vazio (etapa 2)

- [x] 3.1 [FRONT] `pages/peso_page.py` com `app_shell("/peso")`, cabeçalho, card do formulário (Data, Horário, Peso com `inputmode="decimal"`, "Salvar registro"), estado vazio, skeleton e erro com "Tentar novamente"; rota com `ensure_session` + `start_page` e `/peso` fora dos placeholders. Verificar: `reflex compile`, testes de rota e textos. **(aceite)**

## 4. Front-end: listar, excluir e resumo (etapas 3 e 4)

- [x] 4.1 [FRONT] Lista (peso em destaque, "dd/mm/aaaa · hh:mm", lixeira com `aria-label`), `rx.alert_dialog` "Excluir este registro?", toasts "Peso registrado"/"Registro excluído". Verificar: testes de componente.
- [x] 4.2 [FRONT] Cartões "Peso atual", "Desde o 1º registro" e "Falta para a meta" ("—", "Disponível em breve", `# TODO: integração futura com IA (falta para a meta)`). Verificar: testes de texto.

## 5. Validação, responsividade e microinterações (etapa 5)

- [x] 5.1 [FRONT] CSS: cartões 3 colunas → celular "Peso atual" em largura total + 2 lado a lado; formulário 3 → 1 coluna com botão em largura total; foco azul com glow, hover, elevação, scale .98, fade-in, `prefers-reduced-motion`, alvos de 44px. Verificar: teste do CSS.
- [x] 5.2 Navegador (Chrome headless): vazio → 70,0 kg → resumo e "—" → segundo peso e diferença → recarregar (persistência e horário sem deslocamento) → excluir até o vazio; 360/768/1280/1920px sem rolagem horizontal. Verificar: resultados no PR.
- [ ] 5.3 Privacidade com duas contas pela tela; `pytest` completo; `openspec validate registrar-peso --strict`; PR da branch `feat/registrar-peso`. Verificar: saídas no PR.
