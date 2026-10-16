## Context

Ver `proposal.md` (Why/Escopo). Estado relevante após o pull do Xano em 2026-10-14:

- `user` (nome, email, senha) existe, mas com `auth = false`: não emite token.
- `Perfil` já tem `user_id` (sem índice único) e `onboarding_concluido` (sem padrão); `tipo_fisico` tem o valor digitado `Mesoformo`; `modalidade_fav` ainda é enum de valor único.
- Só existem CRUDs gerados automaticamente e **públicos** (`user`, `perfil`, `profiles`, `obj_user` etc.): `GET /user` lista e-mails de todos.
- Reflex 0.9.10: `AuthState` só valida localmente; `/onboarding` usa `PerfilState` com POST `/profiles` sem dono. Não há sessão.
- Restrições: sem bibliotecas novas; tokens de `styles/theme.py`; variáveis em português, funções em inglês; chamadas ao Xano só a partir do backend (States).

## Goals / Non-Goals

**Goals:**
- O cliente nunca escolhe qual Perfil acessa: o Xano resolve sempre por `$auth.id`.
- Validação como lógica pura em `logic/`, testável sem Reflex e sem rede, reaproveitada pelos States.
- Um único ponto de chamada HTTP ao Xano (`services/`), fácil de simular nos testes.

**Non-Goals:**
- Refresh de token, "lembrar de mim", múltiplas sessões, revogação de token no servidor.
- Componentes visuais genéricos reutilizáveis além do necessário para Perfil/navbar.

## Decisions

### D1. Autenticação nativa do Xano na tabela `user`, mesmo grupo de API
`user.auth = true` e endpoints `auth/signup`, `auth/login`, `auth/me` no grupo "Luna's Workspace" (base `XANO_API_URL`). O token é gerado por `security.create_auth_token` e as consultas autenticadas usam `auth = "user"`.
- *Alternativa:* grupo de API separado para auth → exigiria uma segunda URL (`XANO_AUTH_URL`) sem ganho; descartada e removida do `.env.example`.

### D2. Cadastro cria `user` + `Perfil` no mesmo endpoint
`auth/signup` valida e-mail único, cria o `user`, cria o `Perfil` (`user_id`, `nome`, `onboarding_concluido=false`, `medidas=false`) e devolve `{authToken}`. Assim não existe conta sem Perfil e o cliente nunca chama um POST de Perfil.
- *Alternativa:* o Reflex chamar signup e depois um POST de Perfil → duas chamadas, risco de conta órfã e endpoint de criação exposto.

### D3. Endpoints de Perfil por token (`perfil/me`)
- `GET perfil/me` → `db.get Perfil` por `user_id = $auth.id`.
- `PATCH perfil/me` com **inputs explícitos** (sem `dblink`, para não aceitar `user_id`, `id` ou `onboarding_concluido`), `precondition` para cada obrigatório e opções, e grava `data_atualizacao = now` e `onboarding_concluido = true`. Como só é possível salvar com todos os obrigatórios válidos, marcar `true` em todo salvamento é equivalente a "marcar na primeira conclusão".
- Os CRUDs gerados (`user*`, `perfil*`, `profiles*`) são **apagados**; `obj_user` e as tabelas de registros ficam fora (ver Riscos).

### D4. Conta: `auth/me/email` e `auth/me/password`
Ambos `auth = "user"`, com input `senha_atual` verificado por `security.check_password`. E-mail: normalização + unicidade (erro genérico). Senha: `filters=min:8` no input. Respostas nunca incluem `senha` (campo `sensitive`/`internal`).

### D5. Sessão no Reflex: `SessaoState` com token em cookie
`SessaoState(rx.State)` guarda `token` em `rx.Cookie` (`same_site="strict"`, `max_age` igual à expiração do token no Xano, 24h) e carrega `usuario_id`, `usuario_nome`, `usuario_email`, `onboarding_concluido`. `PerfilState`, `ContaState` e `AuthState` leem o token via `get_state(SessaoState)`.
- *Alternativa:* `rx.LocalStorage` → mesmo nível de exposição a JS, mas o cookie expira sozinho e não persiste indefinidamente. Ambos são legíveis por JS (Reflex não oferece cookie `httpOnly`); mitigação em Riscos.

### D6. Guarda de rotas como função pura + `on_load`
`logic/navegacao.py::resolve_redirect(autenticado, onboarding_concluido, rota) -> str | None` decide o destino (`/login`, `/perfil` ou nenhum). `SessaoState.ensure_session` (on_load de toda rota privada) chama `auth/me` + `perfil/me` e aplica a função. As páginas privadas só renderizam o conteúdo quando `sessao_verificada` é verdadeiro, evitando "piscar" dados antes do redirecionamento. `/login` e `/cadastro` usam a mesma função para mandar quem já está logado ao destino correto.

### D7. Validação pura em `logic/`
- `logic/perfil_validacao.py::validate_perfil(dados: dict, hoje: date) -> dict[str, str]` (campo → mensagem) e `build_perfil_payload(dados) -> dict` (normaliza tipos).
- `logic/conta_validacao.py::is_valid_email`, `can_change_email`, `can_change_password`.
- Constantes de opções (`OPCOES_SEXO`, `OPCOES_BIOTIPO` …) num só módulo `logic/perfil_opcoes.py`, usadas pela UI, pela validação e pelos testes, espelhando exatamente os enums do Xano.
- Faixas assumidas (registradas na spec): altura 100–250 cm; meta semanal 1–14; nascimento entre 1900-01-01 e ontem; nome 1–50 caracteres (limite do domain-model).

### D8. Cliente Xano em `services/xano_client.py` com `httpx`
Funções assíncronas (`signup`, `login`, `get_me`, `get_perfil`, `update_perfil`, `change_email`, `change_password`) que levantam `XanoError(tipo)` com tipos fechados (`nao_configurado`, `nao_autorizado`, `conflito`, `invalido`, `indisponivel`). Os States convertem o tipo em mensagem amigável; o texto do servidor nunca chega à UI. `httpx` já vem com o Reflex — nenhuma dependência nova.

### D9. UI com elementos nativos + Radix onde dá acessibilidade pronta
- Selects: `rx.el.select` nativo (label `for`, `autocomplete`, primeira opção vazia desabilitada "Selecione").
- Biotipo: `<input type="radio">` nativos com o mesmo `name`, escondidos dentro de `<label>` estilizados como cards, num `role="radiogroup"` → setas e foco nativos. *Revisado em 2026-10-16:* `rx.radio_cards` aplicava as cores de destaque do tema Radix, que não seguem os tokens do Pulse.
- Chips: `rx.el.button` com `aria-pressed`.
- Toast: `rx.toast`.
- Cards empilhados com 32px de espaço entre eles; conteúdo com largura máxima de ~768px, como nas referências visuais de 2026-10-16.
- CSS em string com tokens substituídos (mesmo padrão de `auth_page.py`), com breakpoints 768px/520px, fade-in escalonado e `prefers-reduced-motion`.

### D10. Estrutura de arquivos
```
projetofacul/
  services/xano_client.py
  logic/perfil_opcoes.py, perfil_validacao.py, conta_validacao.py, navegacao.py
  states/sessao_state.py, perfil_state.py
  components/navbar.py, app_shell.py   (navbar + container + guarda)
  pages/perfil_page.py, placeholder_page.py
  auth_page.py      (AuthState passa a chamar o xano_client)
  projetofacul.py   (registro de rotas; remove onboarding_page/PerfilState antigo)
```

## Risks / Trade-offs

- [Token legível por JS (cookie não-httpOnly)] → `same_site="strict"`, expiração de 24h, nenhum `rx.html` com conteúdo vindo do usuário; refresh/httpOnly ficam para uma change futura.
- [Apagar CRUDs públicos pode quebrar algo que os use] → no código, só `/onboarding` usa `/profiles`, e ele é substituído nesta change; confirmar no Xano que nenhuma outra integração os usa antes do Push.
- [Mudar `modalidade_fav` para lista e corrigir `Mesoformo` com dados existentes] → verificar no Xano se há registros; se houver, migrar o valor antigo para lista de 1 item e `Mesoformo` → `Mesomorfo` antes do Push.
- [Trocar os valores de `nivel_fisico`, `objetivo` e `modalidade_fav1` com Perfis já salvos] → antes de aplicar, conferir no Xano se algum Perfil usa valores antigos (ex.: "Hipertrofia (ganho de massa muscular)", "Pilates", "Cardio"); se houver, limpar ou converter manualmente esses campos (são contas de teste). O `PATCH perfil/me` precisa ser editado no site do Xano, porque o push de endpoints pelo CLI falha (ver notas).
- [Sem o switch de medidas na tela] → o `PATCH perfil/me` continua exigindo `medidas`; o `PerfilState` reenvia o valor lido no `GET perfil/me`, então nada muda no Xano.
- [`user_id` sem índice único permitiria 2 Perfis] → adicionar índice único; `auth/signup` também verifica.
- [Tabelas `treinos`, `sono`, `refeicoes`, `registro_peso`, `obj_user` continuam com CRUD público e sem dono] → fora do escopo; registrar como risco aberto para a próxima change de RLS.
- [Validação duplicada Reflex/Xano pode divergir] → opções vêm de `perfil_opcoes.py` e os testes comparam essas constantes com os enums de `xano/table/perfil.xs`.

## Migration Plan

1. Editar os `.xs` em `xano/` (tabelas, novos endpoints, remoção dos CRUDs) → revisão → Push pela usuária.
2. Criar 2 contas de teste no Xano e validar os endpoints (incluindo acesso cruzado).
3. Configurar `.env` com `XANO_API_URL`.
4. Publicar o código Reflex.
- **Rollback:** reverter o commit do Reflex; no Xano, recriar os CRUDs a partir do histórico do Git (`xano/` versionado) e fazer Push.

## Notas de implementação (2026-10-14)

- O push de endpoints pelo CLI (`xano workspace push`) falha no servidor com `Undefined array key "<rota>:<verbo>:427970"` para qualquer query do grupo "Luna's Workspace"; tabelas sobem normalmente. Endpoints são criados/editados no site do Xano e sincronizados com pull. Nunca fazer pull com alterações locais não enviadas (o pull sobrescreve).
- `modalidade_fav1` usa `enum[]` sem mínimo: com `enum[1:8]` o `db.add Perfil` do signup era recusado, e o Xano não desfaz o `db.add user` anterior (sem transação), deixando usuário sem Perfil.
- O plano gratuito do Xano limita requisições em rajada; respostas fora dos códigos mapeados viram `indisponivel` ("Tente novamente em instantes").

## Decisões de 2026-10-16 (referências visuais da tela de Perfil)

- Opções novas: Condicionamento (Sedentário, Iniciante, Intermediário, Avançado, Atleta), Horário (Manhã, Tarde, Noite, Madrugada), Objetivo (Perder gordura, Ganhar massa, Manter, Performance) e Modalidades (Musculação, Corrida, Ciclismo, Funcional, Crossfit, Luta, Yoga, Natação, Esportes coletivos). `logic/perfil_opcoes.py`, `xano/table/perfil.xs` e `PATCH perfil/me` mudam juntos; o teste que compara as opções com o `.xs` garante que não divergem.
- A tela `/perfil` tem só Dados pessoais, Biotipo corporal e Preferências de treino, mais o botão "Salvar perfil". Os cards Preferências de registro e Conta foram adiados, assim como o `ContaState`.
- A navbar continua sem "Social", mesmo aparecendo na referência visual.
- O login de quem já concluiu o onboarding continua indo para `/inicio`.
