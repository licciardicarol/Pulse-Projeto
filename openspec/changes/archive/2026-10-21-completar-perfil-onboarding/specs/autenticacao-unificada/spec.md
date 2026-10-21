## MODIFIED Requirements

### Requirement: A tela comunica o estado real da integração
O sistema SHALL usar mensagens genéricas e amigáveis para falhas de autenticação, sem expor detalhes técnicos. Com a integração de autenticação do Xano configurada, a interface SHALL indicar sucesso e redirecionar somente após o Xano confirmar o cadastro ou o login. Se a URL do Xano não estiver configurada no ambiente, a interface SHALL informar que o acesso está temporariamente indisponível, SHALL NOT criar sessão e SHALL NOT redirecionar. O acesso com Google SHALL permanecer indisponível até existir um fluxo OAuth configurado.

#### Scenario: Integração indisponível
- **WHEN** a pessoa envia um formulário sem a URL do Xano configurada no ambiente
- **THEN** a interface informa a indisponibilidade sem criar sessão, afirmar sucesso ou redirecionar

#### Scenario: Cadastro ou login confirmado
- **WHEN** o Xano confirma o cadastro ou o login
- **THEN** a interface cria a sessão e redireciona conforme a capability `acesso-usuario`

#### Scenario: Falha de autenticação integrada
- **WHEN** uma chamada integrada de login ou cadastro falha
- **THEN** a interface mostra uma mensagem genérica e amigável em região acessível, sem detalhes técnicos do servidor

### Requirement: Onboarding de perfil continua acessível após reservar a rota de cadastro
O sistema SHALL redirecionar a rota antiga `/onboarding` para `/perfil`, onde o onboarding passa a acontecer. A tela de autenticação SHALL oferecer navegação de retorno à página inicial.

#### Scenario: Abrir onboarding de perfil
- **WHEN** uma pessoa acessa `/onboarding`
- **THEN** é redirecionada para `/perfil`, que aplica as regras de sessão e onboarding

#### Scenario: Voltar à página inicial
- **WHEN** a pessoa seleciona o link de retorno na tela de autenticação
- **THEN** o sistema navega para `/`
