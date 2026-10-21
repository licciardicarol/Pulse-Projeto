## Purpose

Oferecer uma experiência visual única para entrar ou criar uma conta Pulse, mantendo o onboarding de perfil separado e sem simular uma autenticação que ainda não está integrada.

## ADDED Requirements

### Requirement: Rotas de autenticação compartilham uma tela com modos distintos
O sistema SHALL registrar a mesma tela de autenticação em `/login` e `/cadastro`. Ao abrir `/login`, SHALL iniciar no modo "Entrar"; ao abrir `/cadastro`, SHALL iniciar no modo "Criar conta". Alternar o modo SHALL atualizar a rota correspondente sem recarregar a página.

#### Scenario: Acessar login diretamente
- **WHEN** uma pessoa abre `/login`
- **THEN** a tela compartilhada exibe o modo "Entrar"

#### Scenario: Acessar criação de conta diretamente
- **WHEN** uma pessoa abre `/cadastro`
- **THEN** a tela compartilhada exibe o modo "Criar conta"

#### Scenario: Alternar entre os modos
- **WHEN** a pessoa seleciona a outra aba
- **THEN** o conteúdo do formulário e a URL mudam para o modo correspondente sem recarregar a página

### Requirement: Formulários exibem os campos e validações do modo selecionado
O modo "Entrar" SHALL exibir e-mail e senha. O modo "Criar conta" SHALL exibir nome completo, e-mail, senha e confirmação de senha. O sistema SHALL exigir nome no cadastro, e-mail em formato válido, senha com ao menos 8 caracteres e confirmação idêntica à senha. Erros de validação SHALL aparecer junto ao campo correspondente e ser anunciados por uma região acessível.

#### Scenario: Enviar campos vazios
- **WHEN** a pessoa tenta enviar qualquer modo com campos obrigatórios vazios
- **THEN** o envio não prossegue e cada campo obrigatório inválido apresenta erro associado

#### Scenario: E-mail inválido ou senha curta
- **WHEN** o e-mail não tem formato válido ou a senha tem menos de 8 caracteres
- **THEN** o envio não prossegue e a validação informa o campo inválido

#### Scenario: Confirmação de senha diferente
- **WHEN** as senhas do cadastro não coincidem
- **THEN** o envio não prossegue e a confirmação apresenta erro

### Requirement: Formulário preserva valores e limpa dados sensíveis ao alternar
Ao alternar entre modos, o sistema SHALL manter o e-mail digitado e limpar senhas e erros. O envio SHALL ocorrer por Enter e por botão; durante um envio em andamento, o botão SHALL indicar carregamento, ficar desabilitado e impedir envios duplicados.

#### Scenario: Alternar após preencher o formulário
- **WHEN** a pessoa alterna de modo após digitar e-mail, senha e/ou confirmação
- **THEN** o e-mail permanece preenchido, senhas e erros são apagados

#### Scenario: Enviar com Enter
- **WHEN** a pessoa pressiona Enter em um formulário válido
- **THEN** o mesmo envio do botão primário é iniciado

#### Scenario: Envio em andamento
- **WHEN** uma submissão está em andamento
- **THEN** o botão mostra carregamento e não aceita uma segunda submissão

### Requirement: A tela comunica o estado real da integração
O sistema SHALL usar mensagens genéricas e amigáveis para falhas de autenticação, sem expor detalhes técnicos. Enquanto os contratos de autenticação Xano não estiverem disponíveis para integração, a interface SHALL informar que a autenticação ainda não está disponível e SHALL NOT indicar sucesso nem redirecionar como se a conta tivesse sido autenticada. O acesso com Google SHALL permanecer indisponível até existir um fluxo OAuth configurado.

#### Scenario: Integração indisponível
- **WHEN** a pessoa envia um formulário antes da integração com autenticação estar configurada
- **THEN** a interface informa a indisponibilidade sem criar sessão, afirmar sucesso ou redirecionar

#### Scenario: Falha de autenticação integrada
- **WHEN** uma chamada integrada de login ou cadastro falha
- **THEN** a interface mostra uma mensagem genérica e amigável em região acessível, sem detalhes técnicos do servidor

### Requirement: Onboarding de perfil continua acessível após reservar a rota de cadastro
O sistema SHALL preservar o formulário atual de cadastro de perfil em `/onboarding`, sem alterar seus campos ou a chamada existente a `/profiles`. A tela de autenticação SHALL oferecer navegação de retorno à página inicial.

#### Scenario: Abrir onboarding de perfil
- **WHEN** uma pessoa acessa `/onboarding`
- **THEN** o formulário atual de perfil permanece disponível

#### Scenario: Voltar à página inicial
- **WHEN** a pessoa seleciona o link de retorno na tela de autenticação
- **THEN** o sistema navega para `/`

### Requirement: Tela de autenticação é responsiva e acessível
A tela SHALL adaptar-se a celular, tablet e desktop sem rolagem horizontal, mantendo formulário utilizável e conteúdo legível. Campos SHALL ter rótulos associados e autocomplete apropriado; abas SHALL expor semântica de tablist/tab e estado selecionado, aceitar teclado e exibir foco visível. Erros SHALL usar `aria-live="polite"`. Animações SHALL respeitar preferência por movimento reduzido.

#### Scenario: Usar em viewport estreita
- **WHEN** a tela é exibida em larguras de 360px, 768px, 1280px ou 1920px
- **THEN** não há rolagem horizontal e o formulário permanece visível e utilizável

#### Scenario: Navegar pelas abas com teclado
- **WHEN** uma pessoa navega pela seleção de modo usando teclado
- **THEN** o foco é visível e a aba selecionada é anunciada corretamente

#### Scenario: Preferência por movimento reduzido
- **WHEN** o sistema operacional solicita movimento reduzido
- **THEN** as animações não essenciais são desativadas