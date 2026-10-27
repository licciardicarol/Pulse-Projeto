## MODIFIED Requirements

### Requirement: Páginas placeholder
As rotas `/inicio`, `/sono`, `/peso` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. As rotas `/refeicoes` e `/treinos` deixam de ser placeholder e seguem as capabilities `registro-refeicoes` e `registro-treinos`.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a mensagem de área em construção

#### Scenario: Treinos não é mais placeholder
- **WHEN** um usuário com onboarding concluído abre `/treinos`
- **THEN** vê a página de Treinos, sem a mensagem de área em construção
