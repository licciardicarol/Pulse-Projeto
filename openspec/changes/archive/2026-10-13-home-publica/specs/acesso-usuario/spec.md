## Purpose

Permite que clientes criem uma conta e autentiquem-se no Pulse usando a autenticação do Xano, mantendo suas credenciais e sessão protegidas durante o acesso ao aplicativo.

## ADDED Requirements

### Requirement: Criação de conta
O sistema MUST permitir a criação de uma conta usando e-mail e senha, validar os dados obrigatórios e criar a identidade por meio da autenticação do Xano. O cadastro de perfil MUST permanecer uma etapa separada, associada ao usuário autenticado.

#### Scenario: Cadastro concluído
- **WHEN** uma pessoa envia e-mail e senha válidos e o Xano confirma a criação da conta
- **THEN** o sistema confirma o cadastro e encaminha a pessoa para completar o perfil

#### Scenario: Dados de cadastro inválidos
- **WHEN** uma pessoa envia dados obrigatórios ausentes ou inválidos
- **THEN** o sistema informa o erro de validação sem criar uma conta

#### Scenario: E-mail já cadastrado
- **WHEN** o Xano rejeita a criação por um e-mail já associado a uma conta
- **THEN** o sistema informa que não foi possível criar a conta e oferece acesso ao fluxo de login, sem expor dados de outros usuários

### Requirement: Login de usuário
O sistema MUST autenticar as credenciais submetidas usando o Xano e criar uma sessão utilizável no fluxo autenticado do Pulse somente após confirmação do backend.

#### Scenario: Credenciais válidas
- **WHEN** uma pessoa envia credenciais válidas
- **THEN** o sistema estabelece o estado autenticado e encaminha a pessoa à área interna disponível

#### Scenario: Credenciais inválidas
- **WHEN** o Xano rejeita as credenciais
- **THEN** o sistema mantém a pessoa não autenticada e exibe uma mensagem genérica que não revela se o e-mail existe

#### Scenario: Serviço de autenticação indisponível
- **WHEN** o serviço Xano não responde ou retorna falha inesperada
- **THEN** o sistema mantém a pessoa não autenticada e informa que não foi possível concluir o acesso

### Requirement: Proteção de credenciais e sessão
O sistema MUST enviar credenciais somente ao backend de autenticação configurado, MUST NOT expor senhas em mensagens, logs ou respostas ao cliente e MUST manter rotas internas indisponíveis para sessões não autenticadas.

#### Scenario: Acesso não autenticado a rota interna
- **WHEN** uma pessoa sem sessão válida tenta acessar uma rota interna protegida
- **THEN** o sistema a encaminha para o login sem revelar conteúdo privado

#### Scenario: Falha de autenticação
- **WHEN** uma tentativa de cadastro ou login falha
- **THEN** nenhum estado autenticado é criado e a senha não aparece no feedback apresentado