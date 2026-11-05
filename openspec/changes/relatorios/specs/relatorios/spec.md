## Purpose

Mostrar ao usuário autenticado a evolução dos próprios registros (treinos, sono, peso e calorias ingeridas) em relatórios gráficos calculados apenas a partir dos dados que ele registrou, com o tipo de gráfico escolhido por ele e sem valores inventados.

## Modelos de dados envolvidos

Somente leitura das tabelas do Xano já existentes, sempre filtradas pelo dono (`user_id` do token). Representação SQL equivalente, apenas com as colunas usadas:

```sql
-- Frequência de treinos
SELECT data FROM treinos WHERE user_id = :usuario;                         -- data DATE

-- Horas de sono
SELECT inicio_sono, fim_sono, duracao_minutos FROM sono WHERE user_id = :usuario;
                                                                            -- TIMESTAMP (UTC), INT

-- Evolução do peso
SELECT peso, data_horario FROM registro_peso WHERE user_id = :usuario;     -- DECIMAL(5,2) kg, TIMESTAMP (UTC)

-- Calorias ingeridas
SELECT data_refeicao, calorias, analise_ia FROM refeicoes WHERE user_id = :usuario;
                                                                            -- DATE, DECIMAL, TEXT
```

Nenhuma tabela, coluna ou endpoint é criado ou alterado. Datas e horários são interpretados no fuso de Brasília (UTC−03:00).

## ADDED Requirements

### Requirement: Relatórios usam somente os dados do próprio usuário
A tela `/relatorios` SHALL ser uma rota privada e SHALL calcular os relatórios exclusivamente a partir dos registros do usuário autenticado, obtidos pelos endpoints que identificam o dono pelo token de sessão. Nenhum relatório SHALL exibir dados de outro usuário, dados de exemplo ou valores estimados pelo app. Sem sessão válida, a pessoa SHALL ser redirecionada para `/login` sem ver dados.

#### Scenario: Usuário vê só os próprios dados
- **WHEN** os usuários A e B têm treinos registrados e A abre `/relatorios`
- **THEN** os gráficos de A refletem apenas os treinos de A

#### Scenario: Sem sessão
- **WHEN** uma pessoa sem sessão abre `/relatorios`
- **THEN** é redirecionada para `/login` e nenhum gráfico ou dado é exibido

#### Scenario: Sessão expira durante o carregamento
- **WHEN** o Xano rejeita o token ao carregar os relatórios
- **THEN** a sessão local é descartada e a pessoa é redirecionada para `/login`

### Requirement: Cards de relatório
A tela SHALL exibir, abaixo de um cabeçalho com o título "Relatórios", estes quatro cards, nesta ordem e com estes títulos: "Frequência de treinos (últimas 8 semanas)", "Horas de sono (últimos 30 registros)", "Evolução do peso" e "Calorias ingeridas x gastas (últimos 14 dias)". Os cards SHALL ser separados por espaço vertical e SHALL ocupar coluna única em larguras de celular, sem rolagem horizontal.

#### Scenario: Ordem dos cards
- **WHEN** um usuário com onboarding concluído abre `/relatorios`
- **THEN** vê os quatro cards com os títulos acima, nessa ordem

#### Scenario: Celular
- **WHEN** a tela é aberta em 360px de largura
- **THEN** os cards ficam em coluna única e a página não tem rolagem horizontal

### Requirement: Frequência de treinos
O relatório SHALL mostrar a quantidade de treinos registrados em cada uma das últimas 8 semanas, incluindo a semana atual. Semanas SHALL ir de segunda a domingo, pela data do treino no fuso de Brasília, e SHALL aparecer em ordem cronológica, rotuladas pela data da segunda-feira (dd/mm). Semanas sem treino SHALL aparecer com 0. Treinos anteriores às 8 semanas ou com data futura SHALL NOT ser contados. O relatório SHALL ser considerado sem dados suficientes quando não houver nenhum treino no período.

#### Scenario: Contagem por semana
- **WHEN** hoje é quarta-feira 04/11/2026 e o usuário registrou 2 treinos em 02/11 e 1 treino em 28/10
- **THEN** a última semana (02/11) mostra 2, a semana de 26/10 mostra 1 e as outras 6 semanas mostram 0

#### Scenario: Treino fora do período
- **WHEN** o único treino do usuário é de 3 meses atrás
- **THEN** o card mostra "Ainda não há dados suficientes."

### Requirement: Horas de sono
O relatório SHALL mostrar as horas dormidas em cada um dos últimos 30 registros de sono (os mais recentes pelo início do sono), em ordem cronológica, com uma casa decimal e rotulados pela data em que a pessoa acordou (dd/mm). A duração SHALL ser a calculada pelo servidor e, na falta dela, a diferença entre fim e início. Registros sem duração válida SHALL NOT aparecer. O relatório SHALL ser considerado sem dados suficientes quando não houver nenhum registro com duração válida.

#### Scenario: Mais de 30 registros
- **WHEN** o usuário tem 45 noites registradas
- **THEN** o gráfico mostra apenas as 30 mais recentes, da mais antiga para a mais nova

#### Scenario: Conversão para horas
- **WHEN** uma noite tem 450 minutos de duração
- **THEN** o valor exibido para ela é 7,5 h

### Requirement: Evolução do peso
O relatório SHALL mostrar o peso de cada registro em ordem cronológica pela data e hora da pesagem, rotulados por dd/mm, em kg com até duas casas decimais. Registros sem peso válido SHALL NOT aparecer. O relatório SHALL ser considerado sem dados suficientes quando houver menos de 2 registros válidos.

#### Scenario: Dois registros
- **WHEN** o usuário registrou 72,4 kg em 01/10 e 71,8 kg em 01/11
- **THEN** o gráfico mostra os dois pontos em ordem, 01/10 antes de 01/11

#### Scenario: Um único registro
- **WHEN** o usuário tem apenas um registro de peso
- **THEN** o card mostra "Ainda não há dados suficientes."

### Requirement: Calorias ingeridas aguardando a IA
O relatório de calorias SHALL mostrar, para cada um dos últimos 14 dias (incluindo hoje, no fuso de Brasília), a soma das calorias das refeições daquele dia que já foram analisadas. Refeições não analisadas SHALL NOT contar, e um dia sem nenhuma refeição analisada SHALL aparecer sem valor (nunca como 0 kcal). O card SHALL informar que as calorias são estimadas por IA e não substituem orientação profissional, e que as calorias gastas aparecerão quando a IA estimar os treinos. Calorias gastas SHALL NOT ser calculadas ou inventadas nesta versão. O relatório SHALL ser considerado sem dados suficientes quando nenhum dos 14 dias tiver refeição analisada.

#### Scenario: Refeições ainda não analisadas
- **WHEN** o usuário registrou refeições nos últimos 14 dias, mas nenhuma foi analisada pela IA
- **THEN** o card mostra "Ainda não há dados suficientes." e o aviso sobre a estimativa por IA

#### Scenario: Dia parcialmente analisado
- **WHEN** em 03/11 há uma refeição analisada com 650 kcal e outra ainda não analisada
- **THEN** o dia 03/11 mostra 650 kcal

#### Scenario: Dia sem análise
- **WHEN** em 02/11 não há refeição analisada
- **THEN** 02/11 aparece sem valor no gráfico e na tabela, e não como 0

### Requirement: Escolha do tipo de gráfico
Cada card SHALL oferecer a escolha entre "Colunas" e "Linhas", exibida como um grupo de botões com o estado selecionado exposto a tecnologias assistivas. A escolha SHALL valer apenas para aquele relatório e SHALL ser lembrada no navegador do usuário entre visitas, sem ser enviada ao Xano. Sem escolha salva, ou com valor salvo inválido, os padrões SHALL ser: Colunas para Frequência de treinos, Horas de sono e Calorias; Linhas para Evolução do peso. Gráficos de colunas SHALL começar o eixo em zero.

#### Scenario: Trocar para linhas
- **WHEN** o usuário escolhe "Linhas" no card de Horas de sono
- **THEN** só esse card passa a mostrar um gráfico de linha, e o botão "Linhas" fica marcado como selecionado

#### Scenario: Preferência lembrada
- **WHEN** o usuário escolheu "Linhas" para Frequência de treinos e volta a `/relatorios` mais tarde no mesmo navegador
- **THEN** o card de Frequência de treinos abre em "Linhas"

#### Scenario: Valor salvo inválido
- **WHEN** o navegador tem um valor salvo diferente de colunas ou linhas para um relatório
- **THEN** o card usa o padrão daquele relatório

### Requirement: Estados de carregamento, vazio e erro
Enquanto os registros são carregados, a tela SHALL indicar carregamento sem exibir gráficos parciais. Um card sem dados suficientes SHALL exibir "Ainda não há dados suficientes." no lugar do gráfico, mantendo o título. Se a leitura de um tipo de registro falhar, o card correspondente SHALL exibir uma mensagem amigável, sem detalhes técnicos, e a tela SHALL oferecer "Tentar novamente"; os demais cards SHALL continuar exibindo seus dados. Quando o Xano recusar por excesso de requisições, a mensagem SHALL pedir para aguardar alguns segundos.

#### Scenario: Sem nenhum registro
- **WHEN** um usuário novo, sem registros, abre `/relatorios`
- **THEN** os quatro cards mostram "Ainda não há dados suficientes."

#### Scenario: Falha em um dos registros
- **WHEN** a leitura do sono falha e as demais funcionam
- **THEN** o card de sono mostra a mensagem de erro com "Tentar novamente" e os outros três cards mostram seus gráficos ou o estado vazio

### Requirement: Leitura acessível dos gráficos
Cada gráfico SHALL ter uma alternativa em tabela com os mesmos rótulos e valores, disponível para leitores de tela, e SHALL mostrar o valor de cada ponto ou coluna ao passar o mouse ou focar. Valores e rótulos SHALL usar unidades (treinos, h, kg, kcal) e o formato brasileiro de números. Animações SHALL ser desativadas quando o sistema pedir movimento reduzido.

#### Scenario: Leitor de tela
- **WHEN** um leitor de tela percorre o card de Evolução do peso
- **THEN** encontra uma tabela com cada data e o peso correspondente em kg

#### Scenario: Formato brasileiro
- **WHEN** o gráfico de sono exibe 7,5 horas
- **THEN** o valor aparece como "7,5 h", com vírgula decimal
