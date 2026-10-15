# Tasks: completar-perfil-onboarding

Cada task cabe em até 2h. Tag **[BACK]** = Xano / lógica / States; **[FRONT]** = componentes Reflex. Tasks marcadas com **(aceite)** geram código grande e devem ser apresentadas para aprovação da usuária antes de serem aplicadas.

## 1. Back-end Xano: schema e autenticação (etapa 1)

- [x] 1.1 [BACK] Em `xano/table/user.xs`: `auth = true` e índice único em `email`. Em `xano/table/perfil.xs`: corrigir `Mesoformo` → `Mesomorfo`, `modalidade_fav1` (substitui `modalidade_fav`) como lista `enum[]` sem mínimo — o mínimo de 1 vale só no salvamento, senão o signup não consegue criar o Perfil vazio —, `onboarding_concluido` e `medidas` com padrão `false` e índice único em `user_id`. Verificar: sem erros na extensão XanoScript e diff revisado pela usuária. **(aceite)**
- [x] 1.2 [BACK] Criar `auth/signup` (cria `user` + `Perfil` vinculado, devolve `authToken`), `auth/login` (erro genérico) e `auth/me` (id, nome, email, sem senha). Verificar: arquivos `.xs` sem erros na extensão. **(aceite)**
- [x] 1.3 [BACK] Criar `GET perfil/me` e `PATCH perfil/me` (`auth = "user"`, inputs explícitos, preconditions de obrigatórios/opções, `data_atualizacao = now`, `onboarding_concluido = true`). Verificar: arquivos sem erros; `PATCH` não declara `user_id`, `id` nem `onboarding_concluido` como input. **(aceite)**
- [x] 1.4 [BACK] Criar `PATCH auth/me/email` e `PATCH auth/me/password` (`senha_atual` obrigatória, `nova_senha` `min:8`, unicidade de e-mail com erro genérico). Verificar: arquivos sem erros na extensão. **(aceite)**
- [x] 1.5 [BACK] Remover os CRUDs públicos `user*`, `perfil*` (por id e lista) e `profiles*`, após a usuária confirmar que nada externo os usa e conferir/migrar dados existentes de `modalidade_fav`/`tipo_fisico`. Verificar: `git diff --stat xano/` mostra só os arquivos esperados.
- [x] 1.6 [BACK] A usuária faz o Push. Testar no Xano (Run & Debug) com 2 contas A e B: signup, login, `auth/me`, `perfil/me`; A com o token de A nunca lê nem altera dados de B; sem token → 401; `GET /user` não existe mais. Verificar: resultados registrados no PR.

## 2. Back-end Reflex: cliente, lógica e sessão

- [ ] 2.1 [BACK] Criar `logic/perfil_opcoes.py` e `logic/perfil_validacao.py` (`validate_perfil`, `build_perfil_payload`), com `tests/test_perfil_validacao.py` cobrindo: cada obrigatório vazio, data futura/anterior a 1900, altura fora de 100–250 e não numérica, meta fora de 1–14, opção fora da lista, "Selecione" como vazio, payload válido e um teste que compara as opções com os enums de `xano/table/perfil.xs`. Verificar: `pytest` passa.
- [x] 2.2 [BACK] Criar `logic/conta_validacao.py` e `logic/navegacao.py` (`resolve_redirect`), com testes de e-mail igual/inválido/novo, senha < 8 e ≥ 8, e todas as combinações de autenticado × onboarding × rota (privada, `/perfil`, `/login`). Verificar: `pytest` passa.
- [x] 2.3 [BACK] Criar `services/xano_client.py` (httpx assíncrono, `XanoError` com tipos fechados, `.env.example` só com `XANO_API_URL`), com testes usando `httpx.MockTransport` para sucesso, 401, 409/conflito, 400, timeout e URL ausente, conferindo que nenhuma mensagem do servidor nem senha vaza na exceção. Verificar: `pytest` passa. **(aceite)**
- [ ] 2.4 [BACK] Criar `states/sessao_state.py` (token em `rx.Cookie`, `ensure_session`, `logout`, `sessao_verificada`) e conectar `AuthState.enviar` ao signup/login (spinner, anti-duplo-envio, redirecionamento conforme onboarding, mensagens genéricas). Concluir as tasks 2.3 e 4.3 herdadas de `unificar-tela-autenticacao`. Verificar: testes de `AuthState`/`SessaoState` com o cliente simulado (sucesso, credenciais inválidas, Xano indisponível sem criar sessão). **(aceite)**

## 3. Front-end: navbar logada e rotas (etapa 2)

- [ ] 3.1 [FRONT] Criar `components/navbar.py` e `components/app_shell.py` (navbar fixa, 7 itens com ícones Lucide, item ativo em pílula com `aria-current`, "Sair", menu hambúrguer com `aria-expanded` no celular, alvos ≥ 44px; conteúdo só renderiza com `sessao_verificada`). Verificar: teste confirma os 7 itens, a ausência de "Social" e `aria-current` no item ativo. **(aceite)**
- [x] 3.2 [FRONT] Criar `pages/placeholder_page.py` e registrar `/inicio`, `/treinos`, `/refeicoes`, `/sono`, `/peso`, `/relatorios`, `/perfil` com `on_load=SessaoState.ensure_session`; `/onboarding` redireciona para `/perfil`; remover `onboarding_page` e o `PerfilState` antigo; atualizar `tests/test_routes.py`. Verificar: teste de rotas lista todas as rotas privadas com o guarda e `/onboarding` redirecionando.

## 4. Front-end: cards e campos do Perfil (etapa 3)

- [ ] 4.1 [FRONT] Criar `pages/perfil_page.py` com cabeçalho, faixa de onboarding condicional, card Dados pessoais (grade 2 colunas, labels associados, `autocomplete` name/bday/sex/off) e card Biotipo (`rx.radio_cards` com as 3 descrições). Verificar: `reflex compile` sem erros e teste confirma labels/`html_for`, ausência do card "Minhas metas". **(aceite)**
- [ ] 4.2 [FRONT] Card Preferências de treino (selects nativos de Condicionamento, Horário, Objetivo; número de Meta semanal; chips de modalidades com `aria-pressed`) e card Preferências de registro (switch de medidas). Verificar: teste confirma as opções exatas de cada select e os 8 chips. **(aceite)**

## 5. Salvar, onboarding e redirecionamentos (etapa 4)

- [ ] 5.1 [BACK] Criar `states/perfil_state.py`: carregar `perfil/me` no `on_load`, `toggle_modalidade`, `save_profile` (valida com `validate_perfil`, spinner, anti-duplo-clique, `PATCH perfil/me`, toast "Perfil salvo", redireciona a `/inicio` se estava em onboarding, erro geral amigável). Verificar: testes do State com cliente simulado para vazio (sem chamada HTTP), sucesso em onboarding (redireciona), sucesso após onboarding (permanece) e falha do Xano (mensagem amigável, `onboarding_concluido` inalterado). **(aceite)**
- [ ] 5.2 [FRONT] Ligar os campos ao `PerfilState`: erros abaixo de cada campo em `aria-live="polite"`, erro geral acima do botão, botão "Salvar perfil" com ícone de disquete, spinner e `disabled`. Verificar: `reflex compile` e teste dos atributos `aria-live`/`disabled`.

## 6. Card Conta (etapa 5)

- [ ] 6.1 [BACK] Criar `states/conta_state.py`: `change_email` e `change_password` com senha atual, habilitação via `conta_validacao`, limpeza dos campos de senha após sucesso, mensagens "E-mail alterado", "Senha alterada com sucesso.", "Senha atual incorreta." e genéricas. Verificar: testes com cliente simulado para sucesso, senha errada, e-mail em uso e senha nunca presente nas mensagens. **(aceite)**
- [ ] 6.2 [FRONT] Card Conta: e-mail + "Alterar", Senha atual, Nova senha (placeholder "Mínimo de 8 caracteres") + "Alterar", botões secundários habilitados só quando válidos, `autocomplete` email/current-password/new-password. Verificar: `reflex compile` e teste dos estados `disabled`.

## 7. Estilo, responsividade e microinterações (etapa 6)

- [ ] 7.1 [FRONT] CSS da área logada com tokens de `styles/theme.py`: cards (raio 20px, padding 28px), foco azul `#2B8CFF` com glow, hover de chips/biotipos 150ms, botões com elevação e `scale(.98)`, fade-in + slide-up escalonado, `prefers-reduced-motion`, breakpoints (grades e biotipos em 1 coluna, botão salvar 100%, sem rolagem horizontal). Verificar: teste confirma `prefers-reduced-motion`, `min-height: 44px` e o breakpoint no CSS.
- [ ] 7.2 [FRONT] Executar `reflex run` e inspecionar `/perfil`, `/inicio` e a navbar em 360, 768, 1280 e 1920px (`document.documentElement.scrollWidth <= innerWidth`), menu do celular, teclado no biotipo/chips/switch e foco visível. Verificar: capturas ou notas no PR.

## 8. Validação final

- [ ] 8.1 Fluxo completo contra o Xano: cadastrar → cair em `/perfil` com a faixa → salvar vazio (erros) → salvar válido → `onboarding_concluido = true` no Xano e redirecionamento a `/inicio` → reabrir `/perfil` com os dados → trocar e-mail e senha → Sair → `/perfil` redireciona a `/login`. Verificar: passos registrados no PR.
- [ ] 8.2 Privacidade: com as contas A e B, confirmar que A não lê nem edita o Perfil/conta de B por nenhum endpoint, e que nenhuma resposta contém senha/hash. Verificar: resultados no PR.
- [ ] 8.3 [BACK] Atualizar `docs/domain-model.md`: entidade `User` (nome, email, senha) e relação User 1:1 Perfil; Perfil com `user_id`, `sexo` (Feminino, Masculino, Outro), `tipo_fisico` (Ectomorfo, Mesomorfo, Endomorfo), `nivel_fisico` (Iniciante, Intermediário, Avançado), `modalidade_fav1` (lista dos 8 valores, mínimo 1 ao salvar), `horario_fav_de_treino` (Madrugada, Manhã, Tarde, Noite), `objetivo` (4 valores do Xano), obrigatoriedade e regra de RLS por `user_id`. Verificar: revisão da usuária.
- [ ] 8.4 Rodar `pytest` (todos passando) e `openspec validate completar-perfil-onboarding --strict`; abrir PR da branch `feat/completar-perfil-onboarding` justificando `pytest` e `python-dotenv` no `requirements.txt`. Verificar: saídas anexadas ao PR.
