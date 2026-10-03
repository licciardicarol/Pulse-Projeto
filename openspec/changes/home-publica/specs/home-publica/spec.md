## Purpose

Apresenta o Pulse antes da autenticação e orienta clientes novos e existentes para o fluxo adequado, com informações objetivas sobre o produto e respostas às dúvidas mais comuns.

## ADDED Requirements

### Requirement: Home pública do Pulse
O sistema MUST disponibilizar uma página inicial acessível sem autenticação, com informações claras sobre as áreas de acompanhamento do Pulse, incluindo perfil, objetivos, treinos, refeições, sono e evolução de peso.

#### Scenario: Cliente acessa a home
- **WHEN** uma pessoa não autenticada acessa a rota inicial
- **THEN** o sistema exibe a apresentação do Pulse e mantém disponíveis as ações para criar conta e entrar

#### Scenario: Home em diferentes tamanhos de tela
- **WHEN** a home é acessada em uma tela estreita ou larga
- **THEN** o conteúdo permanece legível, sem sobreposição, e as ações de cadastro e login continuam acessíveis

### Requirement: Perguntas frequentes
O sistema MUST apresentar perguntas e respostas sobre o funcionamento do Pulse, criação de conta, cadastro de perfil e registros acompanhados. Qualquer conteúdo sobre insights ou saúde MUST informar que o aplicativo não substitui orientação profissional.

#### Scenario: Cliente consulta as dúvidas
- **WHEN** uma pessoa acessa a seção de perguntas frequentes
- **THEN** encontra respostas sobre conta, perfil e tipos de registro suportados pelo aplicativo

#### Scenario: Conteúdo relacionado a saúde
- **WHEN** a home ou FAQ menciona sugestões, insights ou dados de saúde e bem-estar
- **THEN** o conteúdo esclarece que não constitui aconselhamento médico nem substitui profissionais qualificados

### Requirement: Acesso aos fluxos de conta
A home MUST oferecer ações distintas para criação de conta e login, cada uma direcionando à sua respectiva rota, sem confundir o cadastro de credenciais com o cadastro de perfil.

#### Scenario: Cliente novo inicia cadastro
- **WHEN** uma pessoa seleciona a ação para criar conta
- **THEN** o sistema abre o fluxo de criação de credenciais

#### Scenario: Cliente existente inicia login
- **WHEN** uma pessoa seleciona a ação para entrar
- **THEN** o sistema abre o fluxo de login