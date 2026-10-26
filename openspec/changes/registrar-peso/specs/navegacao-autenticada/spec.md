## MODIFIED Requirements

### Requirement: Páginas placeholder
As rotas `/inicio`, `/treinos`, `/sono` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. As rotas `/refeicoes` e `/peso` deixam de ser placeholder e seguem as capabilities `registro-refeicoes` e `registro-peso`.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a mensagem de área em construção
