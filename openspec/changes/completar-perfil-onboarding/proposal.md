## Objetivo

Permitir que a pessoa, logo após criar a conta, entre autenticada no Pulse e complete o próprio Perfil (onboarding), e depois use a mesma tela `/perfil` para editar seus dados e sua conta, com cada usuário acessando somente o próprio Perfil.

## Why

Hoje a tela de autenticação não está conectada ao Xano (não há sessão), o Perfil não pertence a nenhum usuário e os endpoints de `user` e `Perfil` são públicos: qualquer pessoa pode listar e-mails ou editar o perfil de outra. Sem sessão e sem vínculo `user` → `Perfil`, não é possível personalizar recomendações nem garantir a privacidade dos dados de saúde. A tabela `user` e os campos `user_id` e `onboarding_concluido` acabaram de ser criados no Xano, o que destrava esse fluxo agora.

## Escopo

**Incluído**
- Integração real de cadastro, login e logout com o Xano (token de sessão), assumindo as tasks 2.3 e 4.3 da change arquivada `unificar-tela-autenticacao`.
- Criação automática do Perfil no cadastro, vinculado ao `user_id`, com `onboarding_concluido = false`.
- Endpoints autenticados `perfil/me` (ler/editar o próprio Perfil) e de conta (`auth/me`, troca de e-mail e senha com senha atual).
- Desativação dos CRUDs públicos de `user`, `Perfil` e `profiles`, substituídos pelos endpoints autenticados.
- Ajustes de schema do Perfil já decididos: correção do valor `Mesoformo` → `Mesomorfo`, modalidades como lista (`modalidade_fav1`, substitui `modalidade_fav`), padrão `false` em `onboarding_concluido`, índice único em `user_id`.
- Tela `/perfil` (Dados pessoais, Biotipo, Preferências de treino, Preferências de registro, Conta), modo onboarding com faixa e redirecionamentos.
- Navbar logada (Início, Treinos, Refeições, Sono, Peso, Relatórios, Perfil, Sair) e páginas placeholder para as áreas ainda inexistentes.
- `/onboarding` passa a redirecionar para `/perfil`.
- Atualização do `domain-model.md` para refletir o schema real.

**Fora do escopo**
- Card "Minhas metas" e qualquer estrutura `user_goals`.
- Implementação das páginas Início, Treinos, Refeições, Sono, Peso e Relatórios (apenas placeholders).
- "Social"/comunidade, login com Google, recuperação de senha.
- RLS das tabelas `treinos`, `sono`, `refeicoes`, `registro_peso` (não possuem `profile_id`/`user_id` hoje; ficam registradas como risco para uma change futura).

## What Changes

- **BREAKING** (Xano): remoção dos endpoints públicos `user*`, `perfil*` por id/lista e `profiles*`; o app passa a usar apenas endpoints autenticados.
- **BREAKING** (Xano): `modalidade_fav` é substituído pela lista `modalidade_fav1`; `tipo_fisico` tem o valor `Mesoformo` corrigido para `Mesomorfo`.
- Tabela `user` com autenticação habilitada (`auth = true`).
- Novos endpoints Xano: `auth/signup`, `auth/login`, `auth/me`, `auth/me/email`, `auth/me/password`, `perfil/me` (GET/PATCH).
- Novos módulos Reflex: cliente Xano (backend), validações de Perfil e Conta (lógica pura testável), `SessaoState`, `PerfilState`, `ContaState`, navbar logada, página de Perfil e placeholders.
- `AuthState` deixa de exibir "não conectada ao Xano" e passa a autenticar de verdade.
- A página antiga `/onboarding` (`onboarding_page` + `PerfilState` com POST `/profiles`) é substituída por redirecionamento para `/perfil`.

## Capabilities

### New Capabilities
- `perfil-usuario`: tela `/perfil`, modo onboarding, campos, validações, salvamento e privacidade do Perfil (somente o dono lê/edita).
- `conta-usuario`: alteração de e-mail e de senha do usuário autenticado, exigindo a senha atual.
- `navegacao-autenticada`: navbar logada, guarda de rotas privadas (login e onboarding), placeholders e logout.

### Modified Capabilities
- `acesso-usuario`: cadastro passa a autenticar e levar ao onboarding; login redireciona conforme o onboarding; adiciona encerramento de sessão.
- `autenticacao-unificada`: a tela deixa de informar "integração indisponível"; `/onboarding` deixa de exibir o formulário antigo e redireciona para `/perfil`.

## Impact

- **Xano** (`xano/`): `table/user.xs`, `table/perfil.xs`, novos endpoints em `api/lunas_workspace/auth/` e `api/lunas_workspace/perfil/me_*.xs`; remoção dos CRUDs públicos. Publicação via Push da extensão XanoScript, feita pela usuária.
- **Reflex**: `projetofacul/projetofacul.py`, `projetofacul/auth_page.py`, novos `projetofacul/services/`, `projetofacul/logic/`, `projetofacul/states/`, `projetofacul/components/`, `projetofacul/pages/`.
- **Configuração**: `.env` com `XANO_API_URL` (um único grupo de API); `.env.example` atualizado.
- **Dependências**: nenhuma nova. HTTP via `httpx`, que já é dependência do Reflex.
- **Testes**: `tests/` ganha testes de validação, redirecionamento, cliente Xano (simulado) e rotas.
- **Documentação**: `docs/domain-model.md`.
