## Why

O Pulse apresenta um placeholder de login e uma tela de cadastro de perfil em rotas distintas, sem uma experiência unificada de acesso à conta. Uma tela única reduz a fricção entre entrar e criar conta, preservando o onboarding de perfil como fluxo separado.

## What Changes

- Introduzir uma tela de autenticação compartilhada entre `/login` e `/cadastro`, com modo inicial correspondente à rota e alternância sem recarregar a página.
- Adicionar formulário de login e criação de conta com validação, estados de envio, acessibilidade e layout responsivo conforme a identidade existente.
- Preservar o onboarding de perfil e reutilizar os contratos de autenticação existentes sem alterar endpoints, tabelas ou regras de negócio.
- Usar os links Xano fornecidos para `/auth/login` e `/auth/signup`, mas confirmar seus métodos, payloads, respostas e sessão antes de integrar: os endpoints não estão nos exports versionados e as URLs não publicam documentação acessível; também não há rota de dashboard no app atual.
- Não remover a tela de cadastro do perfil: atualmente `/cadastro` é essa tela, portanto sua substituição exige definir como o perfil continuará acessível após a criação da conta.

## Capabilities

### New Capabilities
- `autenticacao-unificada`: experiência compartilhada de login e criação de conta nas rotas `/login` e `/cadastro`.

### Modified Capabilities

## Impact

- Código potencialmente afetado: `projetofacul/landing_page.py`, `projetofacul/projetofacul.py` e `tests/test_routes.py`.
- Dependência de integração: URLs informadas para `/auth/login` e `/auth/signup`; contratos de request/response e sessão ainda desconhecidos e não encontrados nos arquivos versionados consultados.
- Nenhum endpoint, schema, regra de negócio ou dependência deve ser alterado nesta change.
- Implementação bloqueada até confirmar os contratos de autenticação e a continuidade do onboarding/destino pós-login.