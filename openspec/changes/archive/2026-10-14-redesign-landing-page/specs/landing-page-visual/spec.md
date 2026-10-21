## Purpose

A capability `landing-page-visual` define a apresentação pública e o comportamento visual da home do Pulse, mantendo a estrutura e os dados do produto sem alterar o schema ou os serviços existentes.

## ADDED Requirements

### Requirement: Design visual da home pública
A home pública deve apresentar identidade visual consistente em dark mode, com gradiente azul-marinho, contraste adequado, espaçamento generoso e componentes com estado visual claro.

#### Scenario: Exibição inicial da home
- **WHEN** um usuário acessa `/`
- **THEN** a home deve exibir navbar, hero, seções de funcionalidades, público-alvo, FAQ, CTA e rodapé.

#### Scenario: Visibilidade dos componentes
- **WHEN** o usuário acessa a página em diferentes tamanhos de tela
- **THEN** os componentes devem manter legibilidade, espaçamento e ordem lógica, com colunas reduzidas para 2 ou 1 coluna conforme o espaço disponível.

### Requirement: Navegação
A navbar deve apresentar o logo Pulse, o link de entrada e o botão para iniciar cadastro.

#### Scenario: Navegação pela landing page
- **WHEN** o usuário clica em `Entrar`
- **THEN** o aplicativo deve navegar para `/login`.

#### Scenario: Início do cadastro
- **WHEN** o usuário clica em `Começar grátis`, `Criar minha conta grátis` ou `Criar conta`
- **THEN** o aplicativo deve navegar para `/cadastro`.

### Requirement: Conteúdo da landing page
A landing page deve divulgar o valor do Pulse, explicar sua análise de dados e informar que as sugestões são geradas por IA.

#### Scenario: Conteúdo informativo
- **WHEN** o usuário visualiza cada seção da landing
- **THEN** o texto deve descrever funcionalidades existentes do produto sem afirmar resultados médicos ou de saúde inexistentes.

#### Scenario: Aviso sobre IA
- **WHEN** o usuário visualiza o rodapé ou CTA
- **THEN** deve constar que as sugestões são geradas por IA e não substituem orientação profissional.

### Requirement: FAQ
A página deve apresentar um accordion com as perguntas solicitadas e respostas claras sobre gratuidade, privacidade, registro de refeições, acesso mobile e orientação profissional.

#### Scenario: Abrir uma pergunta
- **WHEN** o usuário clica em uma pergunta do FAQ
- **THEN** a resposta deve abrir e fechar com animação, sem perder o foco no elemento acionado.

### Requirement: Microinterações
Os componentes interativos devem apresentar feedback visual de hover, foco, clique e entrada incremental.

#### Scenario: Interação com botão
- **WHEN** o usuário passa o mouse sobre um botão ou navega por teclado até ele
- **THEN** o botão deve mostrar estado de hover ou foco visível.

#### Scenario: Clique no botão
- **WHEN** o usuário pressiona um botão
- **THEN** deve ocorrer uma redução de escala de aproximadamente 3% com transição de 150–200ms.

#### Scenario: Entrada de elementos
- **WHEN** um elemento entra na área visível da página
- **THEN** ele deve usar uma animação de fade-in e slide-up, respeitando a preferência de redução de movimento.

### Requirement: Responsividade
A landing page deve ser responsiva sem perda de conteúdo ou funcionalidade.

#### Scenario: Dispositivo móvel
- **WHEN** a página é exibida em telas pequenas
- **THEN** o navbar deve ser compacto, as grades devem reduzir para uma ou duas colunas e os botões devem manter tamanho adequado ao toque.

#### Scenario: Preferência reduzida de movimento
- **WHEN** o usuário configura `prefers-reduced-motion`
- **THEN** animações devem ser desativadas ou reduzidas ao mínimo.

### Requirement: Tema e tokens
Os valores de design devem estar centralizados em um módulo de tema reutilizável e não repetidos como cores literais no layout.

#### Scenario: Aplicação visual
- **WHEN** a landing page for implementada
- **THEN** as cores, tipografia, espaçamentos e raios devem ser obtidos de constantes compartilhadas pelo módulo de tema.

### Requirement: Autenticação no cliente
A landing page deve considerar o estado de autenticação do usuário, sem alterar a autenticação Xano.

#### Scenario: Usuário autenticado
- **WHEN** o sistema identificar um usuário autenticado
- **THEN** o usuário deve ser redirecionado para o dashboard, sem exibir fluxo de cadastro desnecessário.

#### Scenario: Usuário não autenticado
- **WHEN** o usuário não estiver autenticado
- **THEN** a landing page deve permanecer acessível e permitir entrada ou cadastro.
