## Purpose

Permitir que o usuário autenticado altere o e-mail e a senha da própria conta pela API do Xano, exigindo a senha atual e sem expor credenciais ou dados de outras contas. A interface (card "Conta" na tela de Perfil) fica para uma change futura, por decisão de 2026-10-16.

## Modelos de dados envolvidos

Tabela `user` (ver `perfil-usuario`): `email TEXT UNIQUE` (trim + minúsculas) e `senha` (hash, tipo password do Xano, nunca retornado ao cliente).

## ADDED Requirements

### Requirement: Alterar e-mail
O backend SHALL oferecer a alteração de e-mail apenas ao usuário autenticado, exigindo a senha atual. Antes de gravar, SHALL verificar a senha atual, normalizar o novo e-mail (trim e minúsculas) e garantir que ele não pertence a outra conta, e SHALL alterar apenas a conta do token de sessão.

#### Scenario: Alteração bem-sucedida
- **WHEN** o usuário autenticado envia um e-mail novo e válido e a senha atual correta
- **THEN** o e-mail da conta é atualizado e o próximo login aceita o novo e-mail

#### Scenario: E-mail já em uso
- **WHEN** o novo e-mail pertence a outra conta
- **THEN** a alteração é recusada com erro genérico, sem confirmar a existência da outra conta

#### Scenario: Senha atual incorreta
- **WHEN** a senha atual informada está errada
- **THEN** nada é alterado e o backend responde com erro

### Requirement: Alterar senha
O backend SHALL oferecer a troca de senha apenas ao usuário autenticado, exigindo a senha atual e uma nova senha com no mínimo 8 caracteres — a mesma regra do cadastro — antes de gravar o novo hash.

#### Scenario: Senha curta
- **WHEN** a nova senha tem menos de 8 caracteres
- **THEN** o backend recusa a gravação

#### Scenario: Troca bem-sucedida
- **WHEN** a senha atual está correta e a nova tem 8 ou mais caracteres
- **THEN** a senha é alterada e o próximo login aceita apenas a nova senha

### Requirement: Proteção das credenciais
Senhas SHALL NOT aparecer em mensagens, logs, respostas da API ou estado enviado ao navegador além do campo que o usuário está digitando. Falhas SHALL usar mensagens amigáveis sem detalhes técnicos. Cada operação de conta SHALL atuar exclusivamente sobre o usuário identificado pelo token.

#### Scenario: Resposta da API
- **WHEN** qualquer endpoint de conta ou de autenticação responde
- **THEN** o corpo não contém o hash nem a senha

#### Scenario: Falha inesperada
- **WHEN** o Xano retorna erro inesperado em uma operação de conta ou de autenticação
- **THEN** o cliente recebe apenas um tipo de erro fechado, sem código ou texto técnico do servidor
