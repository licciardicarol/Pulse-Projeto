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
As rotas `/inicio`, `/treinos`, `/sono`, `/peso` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. A rota `/refeicoes` deixa de ser placeholder e segue a capability `registro-refeicoes`.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a mensagem de área em construção

### Requirement: Sair
Ao acionar "Sair", o sistema SHALL descartar o token e os dados da sessão no navegador e no estado do servidor e SHALL redirecionar para `/`. Após sair, rotas privadas SHALL exigir novo login.

#### Scenario: Encerrar sessão
- **WHEN** o usuário clica em "Sair"
- **THEN** é levado para `/` e, ao tentar abrir `/perfil`, é redirecionado para `/login`

### Requirement: Sessão reaproveitada e limite de requisições
Para respeitar o limite do Xano (10 requisições a cada 20 segundos no plano atual), o sistema SHALL reaproveitar a última confirmação da sessão por até 60 segundos enquanto o token for o mesmo, sem chamar o Xano a cada troca de página. Ao sair ou ao ter o token recusado, esse reaproveitamento SHALL ser descartado. Quando o Xano responder que o limite foi atingido, a UI SHALL exibir "Muitas ações em pouco tempo. Aguarde alguns segundos e tente novamente." sem detalhes técnicos, e a tela de erro da sessão SHALL oferecer o botão "Tentar novamente".

#### Scenario: Navegar entre páginas em sequência
- **WHEN** um usuário com sessão confirmada há menos de 60 segundos abre outra rota privada
- **THEN** a página é liberada sem nova chamada de confirmação ao Xano

#### Scenario: Confirmação expirada
- **WHEN** a última confirmação tem mais de 60 segundos
- **THEN** o token é confirmado de novo no Xano antes de liberar a página

#### Scenario: Limite atingido
- **WHEN** o Xano responde 429 ao confirmar a sessão
- **THEN** a página mostra "Muitas ações em pouco tempo. Aguarde alguns segundos e tente novamente." e o botão "Tentar novamente", e o token é mantido

#### Scenario: Sair descarta o reaproveitamento
- **WHEN** o usuário clica em "Sair" e entra de novo
- **THEN** a nova sessão é confirmada no Xano
