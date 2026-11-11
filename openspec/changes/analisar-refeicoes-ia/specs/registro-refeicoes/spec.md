## MODIFIED Requirements

### Requirement: Nenhum valor nutricional inventado
O app SHALL NOT estimar, calcular ou preencher por conta própria calorias, proteínas, carboidratos, gorduras ou análise de uma refeição, e SHALL NOT aceitar esses valores vindos do cliente. O endpoint de criação SHALL aceitar apenas data, tipo e descrição; valores nutricionais enviados junto com a criação SHALL ser ignorados. Esses campos SHALL ser preenchidos somente pela análise por IA validada e gravada pelo servidor do Pulse, conforme a capability `analise-refeicoes-ia`. Enquanto `analise_ia` estiver vazio, a interface SHALL exibir "Analisando…" (análise em andamento) ou o selo "Aguardando análise" no lugar dos valores, e a refeição SHALL NOT entrar nos totais.

#### Scenario: Cliente tenta enviar calorias
- **WHEN** o app envia `calorias` ou macros junto com a refeição
- **THEN** a refeição é gravada sem esses valores

#### Scenario: Refeição recém-registrada
- **WHEN** o usuário registra uma refeição
- **THEN** ela aparece na lista com "Analisando…" e sem calorias ou macros até a análise por IA ser gravada

#### Scenario: Valores só depois de análise válida
- **WHEN** a análise por IA de uma refeição falha ou é inválida
- **THEN** a refeição continua sem calorias ou macros, com "Aguardando análise", e não entra nos totais

### Requirement: Página de Refeições
A rota `/refeicoes` SHALL ser privada: sem sessão redireciona para `/login`; com onboarding pendente, para `/perfil`. A página SHALL exibir a navbar logada com "Refeições" ativo; cabeçalho com ícone de talheres, título "Refeições", o subtítulo "Descreva o que você comeu. A IA estima calorias e macronutrientes automaticamente." e o botão "+ Nova refeição"; os cards de totais do dia com o aviso de IA; e a lista de refeições.

#### Scenario: Acesso sem login
- **WHEN** uma pessoa sem sessão abre `/refeicoes`
- **THEN** é redirecionada para `/login` sem ver dados

#### Scenario: Item ativo na navbar
- **WHEN** o usuário abre `/refeicoes`
- **THEN** o item "Refeições" da navbar aparece ativo com `aria-current="page"`

#### Scenario: Subtítulo sem promessa futura
- **WHEN** o usuário abre `/refeicoes`
- **THEN** o subtítulo diz "Descreva o que você comeu. A IA estima calorias e macronutrientes automaticamente." e não contém "Em breve"

### Requirement: Totais do dia
A página SHALL exibir 4 cards — "CALORIAS HOJE" (kcal), "PROTEÍNAS", "CARBOIDRATOS" e "GORDURAS" (g) — somando apenas refeições com `data_refeicao` igual à data atual do navegador **e** já analisadas. Sem nenhum valor, cada card SHALL mostrar "0". Havendo N refeições de hoje sem análise (aguardando ou em análise), SHALL exibir abaixo dos cards "N refeição(ões) aguardando análise da IA". Os totais SHALL ser recalculados sempre que uma análise for gravada. Junto aos cards SHALL aparecer, sempre, o aviso "Valores estimados por IA a partir da sua descrição. Não substituem a orientação de um nutricionista.".

#### Scenario: Só refeições sem análise
- **WHEN** o usuário tem 2 refeições de hoje sem análise
- **THEN** os 4 cards mostram 0 e a nota diz "2 refeição(ões) aguardando análise da IA"

#### Scenario: Refeições de outros dias
- **WHEN** existem refeições analisadas de ontem
- **THEN** elas não entram nos totais de hoje

#### Scenario: Análise gravada atualiza os totais
- **WHEN** a análise de uma refeição de hoje com 450 kcal é gravada e os cards mostravam 300 kcal
- **THEN** "CALORIAS HOJE" passa a mostrar 750 sem recarregar a página e a nota de pendentes diminui em 1

### Requirement: Lista de refeições
A lista SHALL mostrar as refeições do usuário da mais recente para a mais antiga (por `data_refeicao` e, no mesmo dia, por `created_at`). Cada item SHALL exibir o chip do tipo, a data em dd/mm/aaaa, a descrição e um botão de exclusão com `aria-label` descritivo. Quando analisada, SHALL exibir também as calorias em azul, a linha "Proteínas X g · Carboidratos Y g · Gorduras Z g", o selo "Estimado por IA" e o resumo da IA. Quando em análise, SHALL exibir "Analisando…". Quando sem análise e fora de análise, SHALL exibir o selo "Aguardando análise", a mensagem da última falha de análise (quando houver) e o botão "Analisar". Sem refeições, SHALL exibir um card de borda tracejada com ícone de talheres, "Nenhuma refeição registrada" e "Descreva sua primeira refeição para começar o seu histórico.". Durante o carregamento SHALL exibir skeleton; se a listagem falhar, SHALL exibir mensagem amigável com botão "Tentar novamente".

#### Scenario: Ordem da lista
- **WHEN** existem refeições de hoje e de ontem
- **THEN** as de hoje aparecem primeiro, e entre as de hoje a registrada por último vem antes

#### Scenario: Estado vazio
- **WHEN** o usuário não tem refeições
- **THEN** o card de estado vazio é exibido

#### Scenario: Falha ao listar
- **WHEN** o Xano não responde ao carregar a lista
- **THEN** a página mostra uma mensagem sem detalhes técnicos e o botão "Tentar novamente", que refaz a busca

#### Scenario: Item analisado
- **WHEN** uma refeição tem análise gravada
- **THEN** o item mostra calorias, a linha de macros, o selo "Estimado por IA" e o resumo, sem o botão "Analisar"

#### Scenario: Item sem análise
- **WHEN** uma refeição não tem análise e não está sendo analisada
- **THEN** o item mostra "Aguardando análise" e o botão "Analisar"

### Requirement: Registrar refeição pelo modal
"+ Nova refeição" SHALL abrir o modal "Nova refeição" (`aria-labelledby` no título, foco preso, foco inicial no primeiro campo, retorno do foco ao botão, fechamento por X com `aria-label="Fechar"`, Esc e clique no overlay, mantendo o conteúdo digitado). Campos: Data (padrão hoje, sem datas futuras), Tipo (apenas Café da manhã, Almoço, Café da tarde, Jantar; padrão pelo horário local: 5h–10h59 Café da manhã, 11h–14h59 Almoço, 15h–17h59 Café da tarde, demais Jantar) e Descrição (textarea, 3 a 500 caracteres). Data, tipo e descrição SHALL ser obrigatórios na interface. O botão "Salvar" SHALL mostrar spinner e ficar desabilitado durante a chamada. Ao salvar com sucesso, o modal SHALL fechar, o formulário SHALL ser limpo, lista e totais SHALL ser atualizados, o toast "Refeição registrada" SHALL aparecer no canto superior direito por cerca de 3s e a análise por IA da nova refeição SHALL começar (capability `analise-refeicoes-ia`), sem manter o modal aberto à espera dela. Falhas do Xano SHALL mostrar mensagem amigável acima do botão, mantendo o modal aberto.

#### Scenario: Opções do tipo
- **WHEN** o select de tipo é aberto
- **THEN** exibe exatamente Café da manhã, Almoço, Café da tarde e Jantar

#### Scenario: Descrição curta
- **WHEN** o usuário tenta salvar com descrição de menos de 3 caracteres
- **THEN** nada é enviado e o campo mostra o erro

#### Scenario: Data futura
- **WHEN** a data escolhida é posterior a hoje
- **THEN** nada é enviado e o campo mostra o erro

#### Scenario: Registro bem-sucedido
- **WHEN** o usuário salva uma refeição válida
- **THEN** o modal fecha, a refeição aparece no topo da lista com "Analisando…" e o toast "Refeição registrada" é exibido

#### Scenario: Falha ao registrar não chama a IA
- **WHEN** o Xano recusa o registro da refeição
- **THEN** o modal continua aberto com a mensagem de falha e nenhuma análise por IA é pedida
