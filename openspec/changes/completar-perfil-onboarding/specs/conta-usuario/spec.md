## Purpose

Permitir que o usuário autenticado altere o e-mail e a senha da própria conta na tela de Perfil, exigindo a senha atual e sem expor credenciais ou dados de outras contas.

## Modelos de dados envolvidos

Tabela `user` (ver `perfil-usuario`): `email TEXT UNIQUE` (trim + minúsculas) e `senha` (hash, tipo password do Xano, nunca retornado ao cliente).

## ADDED Requirements

### Requirement: Card Conta
A tela `/perfil` SHALL exibir o card "Conta" abaixo do botão "Salvar perfil", com: e-mail atual editável e botão secundário "Alterar"; campo "Nova senha" com placeholder "Mínimo de 8 caracteres" e botão "Alterar"; e um campo "Senha atual" exigido para confirmar qualquer uma das duas alterações. As alterações da conta SHALL ser independentes do botão "Salvar perfil".

#### Scenario: Exibir e-mail atual
- **WHEN** o usuário autenticado abre `/perfil`
- **THEN** o campo de e-mail mostra o e-mail da própria conta e os campos de senha aparecem vazios

### Requirement: Alterar e-mail
O botão "Alterar" do e-mail SHALL ficar habilitado somente quando o e-mail digitado for diferente do atual (após trim e minúsculas), tiver formato válido e a senha atual estiver preenchida. O backend SHALL verificar a senha atual do usuário autenticado e a unicidade do novo e-mail antes de gravar, e SHALL alterar apenas a conta do token de sessão.

#### Scenario: E-mail igual ou inválido
- **WHEN** o e-mail digitado é igual ao atual ou não tem formato válido
- **THEN** o botão "Alterar" do e-mail fica desabilitado

#### Scenario: Alteração bem-sucedida
- **WHEN** o usuário informa um e-mail novo e válido e a senha atual correta
- **THEN** o e-mail da conta é atualizado, a mensagem "E-mail alterado" é exibida, o campo de senha atual é limpo e o próximo login aceita o novo e-mail

#### Scenario: E-mail já em uso
- **WHEN** o novo e-mail pertence a outra conta
- **THEN** a alteração é recusada com mensagem genérica "Não foi possível alterar o e-mail." sem confirmar a existência da outra conta

#### Scenario: Senha atual incorreta
- **WHEN** a senha atual informada está errada
- **THEN** nada é alterado e a mensagem "Senha atual incorreta." é exibida

### Requirement: Alterar senha
O botão "Alterar" da senha SHALL ficar habilitado somente quando a nova senha tiver no mínimo 8 caracteres — a mesma regra do cadastro e do campo no Xano — e a senha atual estiver preenchida. O backend SHALL validar a senha atual e o tamanho mínimo antes de gravar o novo hash. Após sucesso, os campos de senha SHALL ser limpos e a mensagem "Senha alterada com sucesso." SHALL ser exibida.

#### Scenario: Senha curta
- **WHEN** a nova senha tem menos de 8 caracteres
- **THEN** o botão "Alterar" da senha fica desabilitado e o backend também recusaria a gravação

#### Scenario: Troca bem-sucedida
- **WHEN** a senha atual está correta e a nova tem 8 ou mais caracteres
- **THEN** a senha é alterada, os campos de senha ficam vazios, a confirmação é exibida e o próximo login aceita apenas a nova senha

### Requirement: Proteção das credenciais
Senhas SHALL NOT aparecer em mensagens, logs, respostas da API ou estado enviado ao navegador além do campo que o usuário está digitando. Falhas SHALL usar mensagens amigáveis sem detalhes técnicos. Cada operação de conta SHALL atuar exclusivamente sobre o usuário identificado pelo token.

#### Scenario: Resposta da API
- **WHEN** qualquer endpoint de conta ou de autenticação responde
- **THEN** o corpo não contém o hash nem a senha

#### Scenario: Falha inesperada
- **WHEN** o Xano retorna erro inesperado em uma alteração de conta
- **THEN** a tela mostra uma mensagem amigável, sem código ou texto técnico do servidor
