## Purpose

Permitir que o usuário autenticado registre refeições descritas em texto, acompanhe o histórico e os totais nutricionais do dia e exclua registros, com cada usuário acessando apenas as próprias refeições e sem nenhum valor nutricional inventado.

## Modelos de dados envolvidos

Representação SQL equivalente à tabela `Refeicoes` do Xano (`xano/table/refeicoes.xs`):

```sql
CREATE TABLE refeicoes (
  id             SERIAL PRIMARY KEY,
  created_at     TIMESTAMP DEFAULT now(),
  user_id        INT REFERENCES "user"(id),        -- dono; preenchido só pelo servidor (token)
  data_refeicao  DATE,                             -- só a data; o período vem do tipo
  tipo           TEXT CHECK (tipo IN ('Café da manhã','Almoço','Café da tarde','Jantar')),
  descricao      TEXT,                             -- 3 a 500 caracteres ao registrar
  calorias       DECIMAL,                          -- kcal; vazio até a análise por IA
  proteinas      DECIMAL,                          -- g;    idem
  carboidratos   DECIMAL,                          -- g;    idem
  gorduras       DECIMAL,                          -- g;    idem
  analise_ia     TEXT                              -- vazio = refeição aguardando análise
);
CREATE INDEX ON refeicoes (user_id);
```

O Xano devolve decimais não preenchidos como `0`; por isso uma refeição é considerada **analisada** somente quando `analise_ia` não está vazio.

## ADDED Requirements

### Requirement: Somente o dono acessa as próprias refeições
O backend SHALL listar, criar e excluir refeições apenas para o usuário autenticado, identificado pelo token de sessão. A criação SHALL gravar o dono a partir do token e SHALL ignorar ou recusar `user_id` enviado pelo cliente. Endpoints públicos de listagem, edição ou exclusão de refeições por id SHALL NOT existir. Requisições sem token válido SHALL ser recusadas sem retornar dados.

#### Scenario: Listar as próprias refeições
- **WHEN** o usuário A, autenticado, lista suas refeições
- **THEN** recebe apenas refeições com `user_id` de A

#### Scenario: Outro usuário não vê nem apaga
- **WHEN** o usuário B tenta listar ou excluir uma refeição de A
- **THEN** a lista de B não contém a refeição de A e a exclusão responde "não encontrada", sem alterar nada

#### Scenario: Sem autenticação
- **WHEN** uma requisição sem token chama qualquer endpoint de refeições
- **THEN** o backend responde com erro de autenticação e nenhum dado

### Requirement: Nenhum valor nutricional inventado
O sistema SHALL NOT estimar, calcular ou preencher calorias, proteínas, carboidratos, gorduras ou análise ao registrar uma refeição. O endpoint de criação SHALL aceitar apenas data, tipo e descrição; valores nutricionais enviados pelo cliente SHALL ser ignorados. Enquanto `analise_ia` estiver vazio, a interface SHALL exibir o selo "Aguardando análise" no lugar dos valores.

#### Scenario: Cliente tenta enviar calorias
- **WHEN** o app envia `calorias` ou macros junto com a refeição
- **THEN** a refeição é gravada sem esses valores

#### Scenario: Refeição recém-registrada
- **WHEN** o usuário registra uma refeição
- **THEN** ela aparece na lista com "Aguardando análise" e sem calorias ou macros

### Requirement: Página de Refeições
A rota `/refeicoes` SHALL ser privada: sem sessão redireciona para `/login`; com onboarding pendente, para `/perfil`. A página SHALL exibir a navbar logada com "Refeições" ativo; cabeçalho com ícone de talheres, título "Refeições", o subtítulo "Descreva o que você comeu. Em breve a IA estimará calorias e macronutrientes automaticamente." e o botão "+ Nova refeição"; os cards de totais do dia; e a lista de refeições.

#### Scenario: Acesso sem login
- **WHEN** uma pessoa sem sessão abre `/refeicoes`
- **THEN** é redirecionada para `/login` sem ver dados

#### Scenario: Item ativo na navbar
- **WHEN** o usuário abre `/refeicoes`
- **THEN** o item "Refeições" da navbar aparece ativo com `aria-current="page"`

### Requirement: Totais do dia
A página SHALL exibir 4 cards — "CALORIAS HOJE" (kcal), "PROTEÍNAS", "CARBOIDRATOS" e "GORDURAS" (g) — somando apenas refeições com `data_refeicao` igual à data atual do navegador **e** já analisadas. Sem nenhum valor, cada card SHALL mostrar "0". Havendo N refeições de hoje aguardando análise, SHALL exibir abaixo dos cards "N refeição(ões) aguardando análise da IA".

#### Scenario: Só refeições sem análise
- **WHEN** o usuário tem 2 refeições de hoje sem análise
- **THEN** os 4 cards mostram 0 e a nota diz "2 refeição(ões) aguardando análise da IA"

#### Scenario: Refeições de outros dias
- **WHEN** existem refeições analisadas de ontem
- **THEN** elas não entram nos totais de hoje

### Requirement: Lista de refeições
A lista SHALL mostrar as refeições do usuário da mais recente para a mais antiga (por `data_refeicao` e, no mesmo dia, por `created_at`). Cada item SHALL exibir o chip do tipo, a data em dd/mm/aaaa, a descrição, as calorias em azul e a linha "Proteínas X g · Carboidratos Y g · Gorduras Z g" quando analisada, ou o selo "Aguardando análise" quando não, e um botão de exclusão com `aria-label` descritivo. Sem refeições, SHALL exibir um card de borda tracejada com ícone de talheres, "Nenhuma refeição registrada" e "Descreva sua primeira refeição para começar o seu histórico.". Durante o carregamento SHALL exibir skeleton; se a listagem falhar, SHALL exibir mensagem amigável com botão "Tentar novamente".

#### Scenario: Ordem da lista
- **WHEN** existem refeições de hoje e de ontem
- **THEN** as de hoje aparecem primeiro, e entre as de hoje a registrada por último vem antes

#### Scenario: Estado vazio
- **WHEN** o usuário não tem refeições
- **THEN** o card de estado vazio é exibido

#### Scenario: Falha ao listar
- **WHEN** o Xano não responde ao carregar a lista
- **THEN** a página mostra uma mensagem sem detalhes técnicos e o botão "Tentar novamente", que refaz a busca

### Requirement: Registrar refeição pelo modal
"+ Nova refeição" SHALL abrir o modal "Nova refeição" (`aria-labelledby` no título, foco preso, foco inicial no primeiro campo, retorno do foco ao botão, fechamento por X com `aria-label="Fechar"`, Esc e clique no overlay, mantendo o conteúdo digitado). Campos: Data (padrão hoje, sem datas futuras), Tipo (apenas Café da manhã, Almoço, Café da tarde, Jantar; padrão pelo horário local: 5h–10h59 Café da manhã, 11h–14h59 Almoço, 15h–17h59 Café da tarde, demais Jantar) e Descrição (textarea, 3 a 500 caracteres). Data, tipo e descrição SHALL ser obrigatórios na interface. O botão "Salvar" SHALL mostrar spinner e ficar desabilitado durante a chamada. Ao salvar com sucesso, o modal SHALL fechar, o formulário SHALL ser limpo, lista e totais SHALL ser atualizados e o toast "Refeição registrada" SHALL aparecer no canto superior direito por cerca de 3s. Falhas do Xano SHALL mostrar mensagem amigável acima do botão, mantendo o modal aberto.

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
- **THEN** o modal fecha, a refeição aparece no topo da lista com "Aguardando análise" e o toast "Refeição registrada" é exibido

### Requirement: Excluir refeição
O botão de exclusão SHALL pedir confirmação ("Excluir esta refeição?" com Cancelar/Excluir). Confirmada, a refeição SHALL ser excluída no Xano, a lista e os totais SHALL ser atualizados e o toast "Refeição excluída" SHALL ser exibido. Falhas SHALL mostrar mensagem amigável sem remover o item.

#### Scenario: Cancelar exclusão
- **WHEN** o usuário clica em Cancelar na confirmação
- **THEN** nada é excluído

#### Scenario: Confirmar exclusão
- **WHEN** o usuário confirma a exclusão da própria refeição
- **THEN** ela some da lista, os totais são recalculados e o toast "Refeição excluída" aparece

### Requirement: Responsividade e acessibilidade
A página SHALL funcionar sem rolagem horizontal em 360px, 768px, 1280px e 1920px, com conteúdo centralizado (largura máxima de cerca de 1200px). Os cards de totais SHALL ter 4 colunas no desktop e 2 no tablet/celular; no celular o botão "+ Nova refeição" SHALL ir para baixo do subtítulo em largura total; o modal SHALL ter largura máxima de cerca de 560px e, no celular, ocupar quase a tela inteira com rolagem interna e botão Salvar sempre visível, com Data e Tipo em coluna única. Alvos de toque SHALL ter no mínimo 44px; todo campo SHALL ter `<label>` associado; erros SHALL usar `aria-live="polite"`; toasts SHALL usar `role="status"`; animações SHALL respeitar `prefers-reduced-motion`. Componentes Radix SHALL usar o azul `#2B8CFF` como cor de destaque.

#### Scenario: Celular
- **WHEN** a página é aberta em 360px
- **THEN** os cards de totais ficam em 2 colunas, o botão "+ Nova refeição" ocupa a largura total e não há rolagem horizontal

#### Scenario: Destaque do select
- **WHEN** o select de tipo é aberto
- **THEN** o item selecionado aparece com fundo azul translúcido e check, sem o destaque ciano padrão
