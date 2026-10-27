## MODIFIED Requirements

### Requirement: Páginas placeholder
As rotas `/inicio`, `/treinos`, `/peso` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. A rota `/refeicoes` segue a capability `registro-refeicoes` e a rota `/sono` segue a capability `registro-sono`; nenhuma das duas é placeholder.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/peso`
- **THEN** vê a navbar com Peso ativo e a mensagem de área em construção

#### Scenario: Sono não é mais placeholder
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a tela de registro de sono, sem a mensagem de área em construção
