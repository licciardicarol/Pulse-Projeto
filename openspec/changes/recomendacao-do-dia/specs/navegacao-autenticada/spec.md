## ADDED Requirements

### Requirement: Rotas privadas sem área em construção
Nenhuma rota privada SHALL exibir aviso de área em construção. As rotas `/inicio`, `/refeicoes`, `/treinos`, `/sono`, `/peso` e `/relatorios` seguem, respectivamente, as capabilities `recomendacao-do-dia`, `registro-refeicoes`, `registro-treinos`, `registro-sono`, `registro-peso` e `relatorios`.

#### Scenario: Início tem conteúdo próprio
- **WHEN** um usuário com onboarding concluído abre `/inicio`
- **THEN** vê a navbar com Início ativo e o card "Recomendação de hoje", sem a mensagem de área em construção

#### Scenario: Nenhuma área em construção
- **WHEN** um usuário com onboarding concluído abre qualquer rota privada
- **THEN** nenhuma delas exibe a mensagem de área em construção

## REMOVED Requirements

### Requirement: Páginas placeholder
**Reason**: com o Início passando a mostrar a recomendação do dia, nenhuma rota privada continua como área em construção, então o requisito não descreve mais nenhuma tela.
**Migration**: substituído por "Rotas privadas sem área em construção". Esta change deve ser arquivada depois de `registro-sono`, `registrar-treinos`, `registrar-peso` e `relatorios`, que ainda reescrevem "Páginas placeholder".
