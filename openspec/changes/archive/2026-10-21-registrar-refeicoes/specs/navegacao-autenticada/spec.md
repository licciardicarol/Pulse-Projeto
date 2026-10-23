## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Páginas placeholder
As rotas `/inicio`, `/treinos`, `/sono`, `/peso` e `/relatorios` SHALL exibir a navbar logada e um aviso simples de que a área ainda está em construção, sem registros, dados inventados ou formulários. A rota `/refeicoes` deixa de ser placeholder e segue a capability `registro-refeicoes`.

#### Scenario: Abrir área ainda não implementada
- **WHEN** um usuário com onboarding concluído abre `/sono`
- **THEN** vê a navbar com Sono ativo e a mensagem de área em construção
