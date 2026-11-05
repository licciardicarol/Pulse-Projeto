## MODIFIED Requirements

### Requirement: Páginas placeholder
A rota `/inicio` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. As rotas `/refeicoes`, `/treinos`, `/sono`, `/peso` e `/relatorios` deixam de ser placeholder e seguem as capabilities `registro-refeicoes`, `registro-treinos`, `registro-sono`, `registro-peso` e `relatorios`.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/inicio`
- **THEN** vê a navbar com Início ativo e a mensagem de área em construção

#### Scenario: Relatórios não é mais placeholder
- **WHEN** um usuário com onboarding concluído abre `/relatorios`
- **THEN** vê a navbar com Relatórios ativo e a tela de relatórios, sem a mensagem de área em construção
