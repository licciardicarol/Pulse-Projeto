# Tasks: relatorios

Cada task cabe em até 2h. Tag **[BACK]** = lógica / States / chamadas ao Xano; **[FRONT]** = componentes Reflex. Tasks marcadas com **(aceite)** geram código grande e são apresentadas para aprovação da usuária antes de serem aplicadas.

## 1. Back-end: séries dos relatórios (lógica pura)

- [x] 1.1 [BACK] Criar `logic/relatorios.py` com `build_weekly_workouts` e `build_sleep_hours`, reaproveitando `sort_sono`/`get_duration_minutes`/`from_utc_ms`, e `tests/test_relatorios_logic.py` cobrindo: 8 semanas segunda→domingo com a semana atual, semanas vazias com 0, treino fora da janela e futuro descartados, cenário 04/11/2026 da spec; sono limitado a 30 mais recentes em ordem cronológica, 450 min → 7,5 h, duração calculada por início/fim quando falta `duracao_minutos`, registro sem duração descartado. Verificar: `pytest tests/test_relatorios_logic.py` passa. **(aceite)**
- [x] 1.2 [BACK] Em `logic/relatorios.py`, `build_weight_evolution`, `build_daily_calories`, `has_enough_data` e `normalize_chart_type`, com testes: peso em ordem cronológica e inválido descartado, menos de 2 pesos = sem dados; 14 dias até hoje, só refeições com `analise_ia` contam, dia sem análise = `None` (nunca 0), soma de várias refeições no mesmo dia; `texto` em formato brasileiro com unidade ("7,5 h", "71,8 kg", "1.850 kcal", "—"); tipo inválido/vazio cai no padrão do relatório. Verificar: `pytest` passa.

## 2. Back-end: State

- [x] 2.1 [BACK] Criar `states/relatorios_state.py` (`start_page` após o guarda, 4 leituras em sequência, `pontos_*`/`erro_*` por relatório, `carregando`, `nao_autorizado` → limpa sessão e vai a `/login`, 429 → mensagem de limite; 4 `rx.LocalStorage` + `set_chart_type` validado + tipos efetivos computados). Verificar: `tests/test_relatorios_state.py` com Xano simulado para sucesso, usuário sem registros, falha só no sono (outros cards preenchidos), token rejeitado, limite de requisições e `set_chart_type` recusando relatório/tipo inválidos. **(aceite)**

## 3. Front-end: tela de Relatórios

- [x] 3.1 [FRONT] Criar `pages/relatorios_page.py` com `app_shell("/relatorios", …)`, cabeçalho "Relatórios" e `report_card` genérico (título `h2`, seletor Colunas/Linhas com `aria-pressed` em `role="group"`, `rx.cond` carregando/erro + "Tentar novamente"/vazio/gráfico, tabela `sr-only` com `aria-describedby`), gráficos `rx.recharts` conforme D4 do design, notas de IA e de calorias gastas no card de calorias. Verificar: `tests/test_relatorios_page.py` confirma os 4 títulos na ordem da spec, os 2 botões por card sem Pizza/Rosca, `aria-pressed`, a mensagem "Ainda não há dados suficientes.", o aviso de IA e as tabelas. **(aceite)**
- [x] 3.2 [FRONT] Registrar `/relatorios` em `projetofacul.py` com `on_load=[SessaoState.ensure_session, RelatoriosState.start_page]` e remover `/relatorios` de `AREAS_EM_CONSTRUCAO`; atualizar `tests/test_routes.py`. Verificar: teste de rotas confirma o guarda como primeiro evento, a página própria e só `/inicio` como placeholder.
- [x] 3.3 [FRONT] CSS da tela com `apply_theme_tokens`: cards com 32px de espaço, largura máxima ~960px, seletor em pílulas (≥ 44px em toque), coluna única e seletor abaixo do título em ≤ 520px, `sr-only`, fade-in dos cards desligado em `prefers-reduced-motion`. Verificar: teste confirma `gap: 32px`, `prefers-reduced-motion`, `min-height: 44px` e o breakpoint no CSS.

## 4. Validação final

- [x] 4.1 `reflex compile --dry` sem erros (instala `recharts` no front-end; conferir a alteração em `reflex.lock/`). Verificar: saída de sucesso registrada no PR.
- [ ] 4.2 Com o app rodando e uma conta de teste: sem registros (4 estados vazios), depois com treinos, sono, 2 pesos e refeições não analisadas; trocar Colunas/Linhas em cada card, recarregar e confirmar a preferência lembrada; conferir 360px e 1280px sem rolagem horizontal. Verificar: notas ou capturas no PR.
- [x] 4.3 Rodar `pytest` (todos passando) e `openspec validate relatorios --strict`. Verificar: saídas anexadas ao PR.
