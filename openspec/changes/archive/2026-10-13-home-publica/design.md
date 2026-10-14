## Context

Consulte `proposal.md` para a motivação e os specs para o comportamento esperado. Hoje `/` e `/cadastro` apontam para o formulário de perfil; não há rotas de credencial. A exportação Xano marca `Obj_user` como `auth = false`, contém apenas `id`, `created_at` e `Objetivo_treino`, e não inclui endpoints de signup/login.

## Goals / Non-Goals

**Goals:**
- Tornar a home pública a entrada do Pulse, preservando `/cadastro` como onboarding de perfil.
- Fazer a autenticação real acontecer no backend Reflex contra endpoints de autenticação documentados/configurados no Xano.
- Proteger rotas e manter credenciais e token de sessão fora do estado renderizado ao cliente.

**Non-Goals:**
- Construir um dashboard ou novas áreas de acompanhamento além das páginas já existentes.
- Reutilizar `Obj_user` como tabela de credenciais sem configurar formalmente sua autenticação no Xano.
- Implementar redefinição de senha ou login social nesta mudança.

## Decisions

- **Separar conta de perfil.** Signup cria a identidade de autenticação; após sucesso encaminha para `/cadastro` para completar o perfil. Isso preserva o contrato de perfil existente sem misturar campos de credencial com dados pessoais.
- **Configurar autenticação no Xano antes do fluxo Reflex.** Usar a tabela de usuário autenticável e endpoints oficiais de signup/login do workspace Xano; associar o perfil ao identificador do usuário autenticado. Não enviar senhas ao endpoint genérico `/profiles` nem reutilizar a tabela `Obj_user` atual como se já suportasse auth.
- **Manter integração no backend.** O State do Reflex submete e-mail/senha ao Xano via backend e mantém token/estado de sessão no servidor. Não incluir senha ou token em componentes, feedback, logs ou payloads destinados ao navegador. O endereço e os endpoints devem vir de configuração de ambiente, nunca ser presumidos a partir do export atual.
- **Proteger páginas por estado de autenticação.** A home e os formulários de conta permanecem públicos. As rotas de perfil e demais áreas internas exigem sessão válida; no estado atual, o fluxo autenticado pode encaminhar para `/cadastro` como área interna existente.
- **Conteúdo da home estático e conservador.** Descrever as áreas de acompanhamento previstas no projeto sem afirmar disponibilidade de integração ou aconselhamento clínico; FAQ inclui ressalva explícita sobre profissionais de saúde.

Alternativas consideradas: mostrar apenas links sem autenticação real (não atende ao escopo confirmado); guardar credenciais no cliente (expõe segredos); usar `Obj_user` diretamente (não existe configuração de auth nem campos adequados no schema exportado).

## Risks / Trade-offs

- [Endpoints e configuração de autenticação Xano ainda não estão no repositório] → implementar/configurar e validar o contrato no Xano antes de conectar as páginas; manter falhas explícitas e sessão fechada quando o serviço estiver indisponível.
- [Associação entre conta e perfil pode não estar disponível no contrato atual de `profiles`] → confirmar e incluir vínculo pelo identificador do usuário autenticado no Xano antes de liberar o onboarding.
- [Token persistido incorretamente pode expor acesso à conta] → armazenar sessão somente no estado de servidor do Reflex e não retorná-la aos componentes.
- [Não existe dashboard para usuários recorrentes] → usar `/cadastro` como destino interno provisório e não apresentar na home funcionalidades de dashboard ainda não implementadas.

## Migration Plan

1. Configurar tabela autenticável e endpoints de signup/login no Xano, incluindo vínculo seguro entre usuário e perfil.
2. Configurar URL/endpoints no ambiente do backend e validar cenários de sucesso e falha.
3. Implementar a home e os formulários/rotas de conta no Reflex, protegendo as rotas internas.
4. Publicar o backend antes de habilitar os CTAs de cadastro/login. Para rollback, restaurar a rota `/` ao conteúdo anterior e desabilitar as rotas de conta; manter os dados de usuário já criados no Xano.

## Open Questions

- Quais são os caminhos e o formato exatos de request/response dos endpoints de autenticação no workspace Xano? O export atual não os contém e devem ser confirmados antes da implementação.