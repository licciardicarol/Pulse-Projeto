## Context

Consulte `proposal.md` para a motivação e `specs/autenticacao-unificada/spec.md` para o contrato de comportamento. Hoje `/cadastro` monta o formulário de perfil em `projetofacul/projetofacul.py`; `/login` é um placeholder em `projetofacul/landing_page.py`. Não há AuthState nem chamadas `/auth/login` ou `/auth/signup` no código versionado consultado, e a app registra apenas `/` e `/cadastro`. Os tokens visuais compartilhados estão em `styles/theme.py`.

## Goals / Non-Goals

**Goals:**
- Concentrar os dois modos em uma única tela e preservar o onboarding em `/onboarding`.
- Reutilizar os tokens existentes e manter a landing apontando para os caminhos já definidos.
- Deixar estados e limites de integração explícitos, sem sucesso simulado.

**Non-Goals:**
- Alterar endpoints, tabelas, schema ou regras de negócio no Xano.
- Implementar OAuth Google sem configuração existente.
- Criar destino dashboard ou fluxo de sessão não presente no app.

## Decisions

- Usar uma única função de página registrada em `/login` e `/cadastro`; inicializar o modo conforme a URL e atualizar a rota ao alternar. Isso mantém deep links coerentes; páginas independentes exigiriam duplicar layout/estado.
- Mover a função atual de perfil para `/onboarding`, preservando `PerfilState` e o POST existente em `/profiles`. Isso mantém o fluxo que hoje ocupa `/cadastro` sem apagar nem fundir dados de perfil ao formulário de autenticação.
- Centralizar estado da interface em um `AuthState` com `modo`, e-mail, campos de formulário, visibilidade de senha, erros e estado de envio. Chamada de autenticação permanece bloqueada até o contrato real ser fornecido; a UI não deve fabricar uma sessão.
- Compor a coluna de apresentação, o card e os campos usando `THEME` e CSS local à página para layout, transições, foco, animações e media queries. Não adicionar dependências.
- Manter o botão Google visível, porém indisponível enquanto não existir integração OAuth; oferecer um motivo acessível em vez de uma ação sem efeito.

## Risks / Trade-offs

- [Os URLs Xano foram fornecidos, mas método, payload, resposta, armazenamento de token e criação de perfil não estão documentados no repositório nem nas páginas públicas consultadas] -> Não enviar dados de usuário nem inferir contrato; bloquear chamadas reais até receber exemplos de request/response.
- [Mover `/cadastro` pode afetar links externos que esperavam o cadastro de perfil] -> A nova rota `/onboarding` preserva o formulário e a landing continua apontando `/cadastro` para criação de conta.
- [Não há dashboard nem verificação de sessão no app atual] -> Não implementar redirecionamento autenticado até o destino e a persistência de sessão serem definidos.

## Migration Plan

1. Confirmar os contratos Xano e a persistência de sessão antes de conectar formulários.
2. Registrar a página compartilhada em `/login` e `/cadastro`, movendo o cadastro de perfil para `/onboarding`.
3. Validar rotas, responsividade e acessibilidade; manter a tela honesta enquanto a autenticação real não estiver conectada.
4. Rollback: restaurar a rota `/cadastro` para o formulário de perfil e retirar os registros compartilhados caso a nova navegação seja revertida.

## Open Questions

- Quais são os métodos, campos de request/response e a forma de armazenamento de sessão dos endpoints `/auth/login` e `/auth/signup` fornecidos?
- Qual será o destino após autenticação e como detectar que o usuário já possui sessão?
- A criação de conta Xano cria também o Perfil com nome e e-mail, ou o onboarding em `/onboarding` deve fazê-lo?