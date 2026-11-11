## Purpose

Estimar por IA as calorias, proteínas, carboidratos e gorduras de cada refeição que o usuário descreve em texto, gravando o resultado na própria refeição de forma protegida e deixando claro na interface que os valores são estimativas geradas por IA, sem substituir a orientação de um nutricionista.

## Modelos de dados envolvidos

Nenhuma tabela nova. A análise preenche colunas que já existem na tabela `refeicoes` do Xano, sempre na linha do próprio dono (`user_id` do token). Representação SQL equivalente:

```sql
-- colunas já existentes, preenchidas somente pela análise por IA
UPDATE refeicoes
   SET calorias     = :calorias,      -- DECIMAL, kcal, 0 a 5000, 1 casa decimal
       proteinas    = :proteinas,     -- DECIMAL, g, 0 a 500, 1 casa decimal
       carboidratos = :carboidratos,  -- DECIMAL, g, 0 a 500, 1 casa decimal
       gorduras     = :gorduras,      -- DECIMAL, g, 0 a 500, 1 casa decimal
       analise_ia   = :resumo         -- TEXT, 1 a 300 caracteres; preenchido = refeição analisada
 WHERE id = :refeicao_id
   AND user_id = :usuario_do_token;
-- data_refeicao, tipo, descricao, user_id e created_at nunca são alterados pela análise
```

Para a IA vão apenas `tipo` e `descricao` da refeição analisada.

## ADDED Requirements

### Requirement: Análise automática após registrar
Depois que uma refeição é registrada com sucesso, o sistema SHALL pedir a análise dessa refeição à IA sem nenhuma ação extra do usuário. O registro SHALL terminar como antes (modal fechado, toast "Refeição registrada") sem esperar a IA. Enquanto a análise roda, a refeição SHALL aparecer com o estado "Analisando…". Quando a análise é gravada, a refeição e os 4 cards de totais SHALL ser atualizados sem recarregar a página. A falha da análise SHALL NOT desfazer nem impedir o registro da refeição.

#### Scenario: Registro com análise bem-sucedida
- **WHEN** o usuário registra hoje "2 ovos mexidos e 1 pão francês" e a IA devolve uma análise válida
- **THEN** a refeição aparece primeiro com "Analisando…" e, em seguida, com calorias, macros, selo "Estimado por IA" e resumo, e os cards de totais de hoje somam esses valores

#### Scenario: IA falha depois do registro
- **WHEN** o usuário registra uma refeição e a chamada à IA falha
- **THEN** a refeição continua salva e listada com "Aguardando análise", e nenhuma caloria ou macro é gravada

### Requirement: Dados enviados à IA
O pedido à IA SHALL conter apenas o tipo e a descrição da refeição que está sendo analisada. O pedido SHALL NOT conter nome, e-mail, id do usuário, token de sessão, outras refeições ou dados de outros usuários. A chamada à IA SHALL partir somente do servidor do Pulse, e a chave da API da IA SHALL ficar apenas em variável de ambiente do servidor, nunca no repositório nem no código enviado ao navegador.

#### Scenario: Conteúdo do pedido
- **WHEN** o sistema monta o pedido para a refeição "Almoço" com descrição "arroz, feijão e frango grelhado"
- **THEN** o pedido contém "Almoço" e "arroz, feijão e frango grelhado" e não contém o nome, o e-mail, o id nem o token do usuário

#### Scenario: Chave fora do navegador
- **WHEN** a página `/refeicoes` é compilada e carregada no navegador
- **THEN** o código e os dados enviados ao navegador não contêm a chave da API da IA, e o navegador não faz requisições diretas à IA

### Requirement: Resposta da IA validada antes de gravar
O sistema SHALL pedir à IA uma resposta estruturada com: se reconheceu alimentos (`reconhecido`), um resumo curto (`resumo`), `calorias` (kcal), `proteinas`, `carboidratos` e `gorduras` (g). A análise SHALL ser gravada somente quando `reconhecido` for verdadeiro, o resumo não for vazio e os 4 números existirem, forem finitos e estiverem nas faixas: calorias de 0 a 5000 kcal e cada macronutriente de 0 a 500 g. Os números SHALL ser arredondados para 1 casa decimal e o resumo SHALL ter espaços aparados e no máximo 300 caracteres. Qualquer resposta fora desse formato SHALL ser tratada como falha, sem gravar nada.

#### Scenario: Resposta válida
- **WHEN** a IA devolve `reconhecido` verdadeiro, resumo "2 ovos (~140 kcal), 1 pão francês (~135 kcal)", calorias 275.36, proteínas 16.04, carboidratos 29.9 e gorduras 10.55
- **THEN** a refeição é gravada com 275,4 kcal, 16 g de proteínas, 29,9 g de carboidratos, 10,6 g de gorduras e o resumo informado

#### Scenario: Valor fora da faixa
- **WHEN** a IA devolve calorias 12000 ou um macronutriente negativo
- **THEN** nada é gravado e a refeição continua "Aguardando análise" com a mensagem de falha da análise

#### Scenario: Resposta ilegível
- **WHEN** a IA devolve texto que não é JSON ou um JSON sem algum dos campos
- **THEN** nada é gravado e a refeição continua "Aguardando análise" com a mensagem de falha da análise

### Requirement: Descrição sem alimentos reconhecíveis
Quando a IA indicar que não reconheceu alimentos na descrição (`reconhecido` falso), o sistema SHALL NOT gravar calorias, macros nem resumo, e a refeição SHALL mostrar "Não reconhecemos alimentos nesta descrição. Exclua e registre de novo com mais detalhes.".

#### Scenario: Descrição sem comida
- **WHEN** o usuário registra a descrição "asdfgh" e a IA responde `reconhecido` falso
- **THEN** a refeição fica sem valores, com "Aguardando análise" e a mensagem de alimentos não reconhecidos

### Requirement: Gravação protegida da análise
O backend de dados (Xano) SHALL oferecer uma operação para gravar a análise de uma refeição que exige, ao mesmo tempo, o token de sessão válido do usuário e uma chave secreta de serviço conhecida apenas pelo servidor do Pulse. A operação SHALL gravar somente em refeições cujo dono é o usuário do token; SHALL validar de novo as faixas de valores (calorias 0–5000, macros 0–500, resumo de 1 a 300 caracteres); SHALL alterar apenas `calorias`, `proteinas`, `carboidratos`, `gorduras` e `analise_ia`; e SHALL NOT alterar data, tipo, descrição ou dono. A chave de serviço SHALL ficar somente em variáveis de ambiente (servidor do Pulse e Xano), nunca no repositório nem no navegador.

#### Scenario: Chave de serviço ausente ou errada
- **WHEN** uma requisição com token válido, mas sem a chave de serviço correta, tenta gravar a análise de uma refeição do próprio usuário
- **THEN** a requisição é recusada como acesso negado e a refeição não é alterada

#### Scenario: Refeição de outro usuário
- **WHEN** o servidor do Pulse, com a chave correta e o token do usuário B, tenta gravar a análise de uma refeição do usuário A
- **THEN** a resposta é "não encontrada" e a refeição de A não é alterada

#### Scenario: Sem autenticação
- **WHEN** uma requisição sem token chama a gravação da análise
- **THEN** o backend responde com erro de autenticação e nada é alterado

#### Scenario: Valores fora da faixa no backend
- **WHEN** a gravação recebe calorias 6000 ou resumo vazio
- **THEN** a requisição é recusada como entrada inválida e nada é alterado

#### Scenario: Campos do registro preservados
- **WHEN** a análise de uma refeição é gravada
- **THEN** `data_refeicao`, `tipo`, `descricao` e `user_id` continuam iguais aos de antes da análise

### Requirement: Falhas da análise não travam a tela
Se a IA não estiver configurada, não responder a tempo, recusar o pedido, atingir o limite de requisições, devolver resposta inválida, ou se a gravação no Xano falhar, a refeição SHALL continuar salva e sem valores, com "Aguardando análise", uma mensagem curta sem detalhes técnicos e o botão "Analisar". O restante da página (lista, totais, registro e exclusão) SHALL continuar funcionando. As mensagens SHALL ser:
- limite de requisições da IA: "A IA está ocupada agora. Tente analisar de novo em alguns instantes.";
- IA não configurada no servidor: "Análise por IA indisponível no momento.";
- demais falhas: "Não foi possível analisar esta refeição agora.".

Se a sessão expirar durante a gravação, a sessão SHALL ser encerrada e o usuário SHALL ser redirecionado para `/login`.

#### Scenario: Limite da IA
- **WHEN** a IA responde que o limite de requisições foi atingido
- **THEN** nada é gravado e a refeição mostra "A IA está ocupada agora. Tente analisar de novo em alguns instantes." e o botão "Analisar"

#### Scenario: IA não configurada
- **WHEN** o servidor não tem a chave da IA configurada e o usuário registra uma refeição
- **THEN** a refeição é registrada, nenhuma chamada à IA é feita e ela mostra "Análise por IA indisponível no momento."

#### Scenario: Sessão expirada ao gravar
- **WHEN** a IA responde, mas o Xano recusa a gravação por token inválido
- **THEN** a sessão é encerrada e o usuário é redirecionado para `/login`

### Requirement: Analisar de novo pelo botão
Cada refeição sem análise que não esteja sendo analisada SHALL mostrar o botão "Analisar", com `aria-label` "Analisar refeição: <tipo> de <data>". O clique SHALL pedir a análise apenas daquela refeição, com as mesmas regras da análise automática. Durante a análise, o botão SHALL dar lugar ao estado "Analisando…" (anunciado a leitores de tela), e cliques repetidos SHALL NOT disparar uma segunda análise da mesma refeição. Abrir ou recarregar a página SHALL NOT disparar análises automaticamente.

#### Scenario: Refeição registrada antes desta funcionalidade
- **WHEN** o usuário abre `/refeicoes` com uma refeição antiga sem análise e clica em "Analisar"
- **THEN** só essa refeição é enviada à IA e, com análise válida, passa a mostrar valores, selo e resumo

#### Scenario: Clique duplo
- **WHEN** o usuário clica duas vezes seguidas em "Analisar" na mesma refeição
- **THEN** a IA é chamada uma única vez para essa refeição

#### Scenario: Abrir a página não chama a IA
- **WHEN** o usuário abre `/refeicoes` com refeições sem análise
- **THEN** nenhuma chamada à IA é feita até ele registrar uma refeição ou clicar em "Analisar"

### Requirement: Conteúdo identificado como gerado por IA
Toda refeição analisada SHALL exibir o selo "Estimado por IA" e o resumo da IA. A página SHALL exibir junto aos cards de totais, sempre, o aviso "Valores estimados por IA a partir da sua descrição. Não substituem a orientação de um nutricionista.". O pedido à IA SHALL se limitar a estimar valores e identificar os alimentos e porções; o resumo SHALL NOT conter recomendações de dieta, saúde ou tratamento.

#### Scenario: Selo e resumo
- **WHEN** uma refeição analisada aparece na lista
- **THEN** ela mostra o selo "Estimado por IA" e o resumo da IA junto com calorias e macros

#### Scenario: Aviso sempre visível
- **WHEN** o usuário abre `/refeicoes`, com ou sem refeições analisadas
- **THEN** o aviso de que os valores são estimados por IA e não substituem um nutricionista aparece junto aos cards de totais
