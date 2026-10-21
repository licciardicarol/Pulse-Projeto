# navegacao-autenticada Specification

## Purpose
Definir a navegação da área logada do Pulse — navbar, proteção das rotas privadas por sessão e por onboarding, páginas placeholder e saída — garantindo que conteúdo privado só seja exibido para quem está autenticado.

## Requirements

### Requirement: Navbar logada
Toda rota privada SHALL exibir uma navbar fixa no topo, em largura total, com: logo "Pulse" à esquerda; itens Início (`/inicio`), Treinos (`/treinos`), Refeições (`/refeicoes`), Sono (`/sono`), Peso (`/peso`), Relatórios (`/relatorios`) e Perfil (`/perfil`), cada um com ícone; e "Sair" à direita. O item da rota atual SHALL aparecer destacado em pílula azul translúcida e SHALL expor `aria-current="page"`. A navbar SHALL NOT conter "Social".

#### Scenario: Item ativo
- **WHEN** o usuário está em `/perfil`
- **THEN** o item Perfil aparece destacado com `aria-current="page"` e os demais não

#### Scenario: Sem Social
- **WHEN** a navbar é exibida
- **THEN** não existe item "Social"

### Requirement: Navbar responsiva
Em larguras de celular, a navbar SHALL exibir logo e um botão de menu compacto que abre um painel com todos os itens e "Sair", sem rolagem horizontal. Todos os alvos de toque SHALL ter no mínimo 44px e foco visível; o botão de menu SHALL expor `aria-expanded` e rótulo acessível.

#### Scenario: Abrir menu no celular
- **WHEN** a página é exibida em 360px e o usuário toca no botão de menu
- **THEN** o painel com os 7 itens e "Sair" é exibido, `aria-expanded` passa a `true` e a largura da página não ultrapassa a viewport

### Requirement: Proteção de rotas privadas
As rotas `/inicio`, `/treinos`, `/refeicoes`, `/sono`, `/peso`, `/relatorios` e `/perfil` SHALL ser privadas. Sem sessão válida, o sistema SHALL redirecionar para `/login` sem exibir conteúdo privado. Com sessão válida e `onboarding_concluido = false`, toda rota privada exceto `/perfil` SHALL redirecionar para `/perfil`. Com onboarding concluído, nenhuma rota privada SHALL forçar redirecionamento.

#### Scenario: Não autenticado
- **WHEN** uma pessoa sem sessão abre `/perfil` ou outra rota privada
- **THEN** é redirecionada para `/login` e nenhum dado de Perfil é exibido

#### Scenario: Sessão expirada ou inválida
- **WHEN** o token salvo é rejeitado pelo Xano
- **THEN** a sessão local é descartada e a pessoa é redirecionada para `/login`

#### Scenario: Onboarding pendente
- **WHEN** um usuário com `onboarding_concluido = false` abre `/treinos`
- **THEN** é redirecionado para `/perfil`

#### Scenario: Onboarding concluído
- **WHEN** um usuário com `onboarding_concluido = true` abre `/treinos`
- **THEN** a página é exibida normalmente

### Requirement: Páginas placeholder
As rotas `/inicio`, `/treinos`, `/refeicoes`, `/sono`, `/peso` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a mensagem de área em construção

### Requirement: Sair
Ao acionar "Sair", o sistema SHALL descartar o token e os dados da sessão no navegador e no estado do servidor e SHALL redirecionar para `/`. Após sair, rotas privadas SHALL exigir novo login.

#### Scenario: Encerrar sessão
- **WHEN** o usuário clica em "Sair"
- **THEN** é levado para `/` e, ao tentar abrir `/perfil`, é redirecionado para `/login`
