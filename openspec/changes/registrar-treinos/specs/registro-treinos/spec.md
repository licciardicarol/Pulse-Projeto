## Purpose

Permitir que o usuário autenticado registre sessões de treino, acompanhe o histórico e exclua registros, com cada usuário acessando apenas os próprios treinos e sem nenhum campo ou opção além do schema do Xano.

## Modelos de dados envolvidos

Representação SQL equivalente à tabela `Treinos` do Xano (`xano/table/treinos.xs`) após esta change:

```sql
CREATE TABLE treinos (
  id           SERIAL PRIMARY KEY,
  created_at   TIMESTAMP DEFAULT now(),         -- UTC; privado (não volta na API)
  user_id          INT REFERENCES "user"(id),   -- dono; preenchido só pelo servidor (token)
  data             DATE,                        -- dia do treino; nunca futuro em America/Sao_Paulo
  duracao_minutos  INT,                         -- minutos, 1 a 1440
  nome             TEXT,                        -- 2 a 60 caracteres
  categoria        TEXT,                        -- texto livre, até 40 caracteres
  intensidade      TEXT,                        -- texto livre, até 20 caracteres
  observacoes      TEXT,                        -- até 500 caracteres
  tipo             TEXT CHECK (tipo IN ('Superior','Inferior','Full body (corpo todo)')),  -- legado, não usado nesta tela
  inicio       TIMESTAMP,                       -- legado, não usado nesta tela
  fim          TIMESTAMP,                       -- legado, não usado nesta tela
  carga        DECIMAL,                         -- legado, não usado nesta tela
  repeticoes   INT                              -- legado, não usado nesta tela
);
CREATE INDEX ON treinos (user_id);                -- único item novo no schema
```

Os campos `user_id`, `nome`, `duracao_minutos`, `categoria`, `intensidade` e `observacoes` já existem no servidor (texto com `trim`). No banco todos os campos são opcionais; o endpoint `POST treinos/me` exige `data`, `duracao_minutos` e `nome`. O campo `data` é um `date` puro (sem fuso): o app envia o dia já calculado em America/Sao_Paulo.

## ADDED Requirements

### Requirement: Somente o dono acessa os próprios treinos
O backend SHALL listar, criar e excluir treinos apenas para o usuário autenticado, identificado pelo token de sessão. A criação SHALL gravar o dono a partir do token e SHALL ignorar `user_id` enviado pelo cliente. Endpoints públicos de listagem, criação, edição ou exclusão de treinos SHALL NOT existir. Requisições sem token válido SHALL ser recusadas sem retornar dados. Excluir um treino inexistente ou de outro usuário SHALL responder "não encontrado" (404), sem revelar se ele existe.

#### Scenario: Listar os próprios treinos
- **WHEN** o usuário A, autenticado, chama `GET treinos/me`
- **THEN** recebe apenas treinos com `user_id` de A

#### Scenario: Outro usuário não vê nem apaga
- **WHEN** o usuário B lista treinos e chama `DELETE treinos/me/{id}` com o id de um treino de A
- **THEN** a lista de B não contém o treino de A, a exclusão responde 404 e o treino de A continua existindo

#### Scenario: Cliente tenta definir o dono
- **WHEN** o app envia `user_id` de outro usuário no `POST treinos/me`
- **THEN** o treino é gravado com o `user_id` do token

#### Scenario: Sem autenticação
- **WHEN** uma requisição sem token chama qualquer endpoint `treinos/me`
- **THEN** o backend responde 401 e nenhum dado

#### Scenario: CRUDs públicos removidos
- **WHEN** alguém chama `GET treino` ou `DELETE treino/{id}`
- **THEN** o Xano responde 404 (endpoint inexistente)

### Requirement: Dados do treino fiéis ao schema
O endpoint de criação SHALL aceitar apenas `data`, `duracao_minutos`, `nome`, `categoria`, `intensidade` e `observacoes`. `data`, `duracao_minutos` e `nome` SHALL ser obrigatórios; `duracao_minutos` SHALL ser inteiro entre 1 e 1440; `nome` SHALL ter de 2 a 60 caracteres após remover espaços nas pontas; `categoria` SHALL ter no máximo 40, `intensidade` no máximo 20 e `observacoes` no máximo 500 caracteres. `data` SHALL NOT ser posterior a hoje no fuso America/Sao_Paulo. Valores inválidos SHALL ser recusados pelo app (sem chamada HTTP) e pelo Xano (`inputerror`). O app SHALL NOT enviar `tipo`, `inicio`, `fim`, `carga` nem `repeticoes`.

#### Scenario: Categoria longa
- **WHEN** o usuário tenta salvar com categoria de 41 caracteres
- **THEN** nada é enviado e o campo mostra o erro

#### Scenario: Intensidade livre
- **WHEN** o usuário informa "Alta" em Intensidade
- **THEN** o treino é gravado com intensidade "Alta"

#### Scenario: Duração fora do limite
- **WHEN** o usuário tenta salvar com duração 0, 1441, decimal ou vazia
- **THEN** nada é enviado e o campo mostra o erro

#### Scenario: Nome curto
- **WHEN** o usuário tenta salvar com nome de 1 caractere ou só espaços
- **THEN** nada é enviado e o campo mostra o erro

#### Scenario: Data futura comparando só o dia
- **WHEN** às 23h59 de 26/10/2026 em São Paulo o usuário escolhe 27/10/2026
- **THEN** nada é enviado e o campo mostra "A data não pode estar no futuro."; escolhendo 26/10/2026 o treino é aceito

#### Scenario: Opcionais vazios
- **WHEN** o usuário salva sem categoria, intensidade e observações
- **THEN** o treino é gravado sem esses campos e o card não exibe chips nem texto para eles

### Requirement: "Hoje" no fuso de São Paulo
A data padrão do formulário, o limite de data futura e a comparação de dias SHALL usar o fuso America/Sao_Paulo, independentemente do fuso do servidor do Reflex ou do navegador.

#### Scenario: Treino registrado à noite
- **WHEN** o usuário abre o modal às 22h de 26/10/2026 em São Paulo (01h de 27/10 em UTC)
- **THEN** a Data vem preenchida com 26/10/2026 e o treino salvo aparece com essa data

### Requirement: Página de Treinos
A rota `/treinos` SHALL ser privada: sem sessão redireciona para `/login`; com onboarding pendente, para `/perfil`. A página SHALL exibir a navbar logada com "Treinos" ativo (sem item "Social"); cabeçalho com ícone de haltere em quadrado azul translúcido, título "Treinos", subtítulo "Registre suas sessões de treino e acompanhe seu histórico." e o botão primário "+ Novo treino"; e a lista de treinos, em container centralizado com largura máxima de cerca de 1200px.

#### Scenario: Acesso sem login
- **WHEN** uma pessoa sem sessão abre `/treinos`
- **THEN** é redirecionada para `/login` sem ver dados

#### Scenario: Onboarding pendente
- **WHEN** um usuário com onboarding incompleto abre `/treinos`
- **THEN** é redirecionado para `/perfil`

#### Scenario: Item ativo na navbar
- **WHEN** o usuário abre `/treinos`
- **THEN** o item "Treinos" aparece ativo com `aria-current="page"` e não existe item "Social"

### Requirement: Lista de treinos
A lista SHALL mostrar os treinos do usuário do mais recente para o mais antigo (por `data` desc e, no mesmo dia, por `id` desc). Cada item SHALL ser um card com o nome em destaque, a data em dd/mm/aaaa, o chip da categoria, o chip da intensidade, a duração ("60 min"), as observações em texto secundário e um botão de exclusão com ícone de lixeira vermelha e `aria-label` "Excluir treino {nome}". Campos opcionais vazios SHALL NOT aparecer. Sem treinos, SHALL exibir um card de borda tracejada com ícone de haltere, "Nenhum treino ainda" e "Toque em "Novo treino" para registrar sua primeira sessão.". Durante o carregamento SHALL exibir skeleton; se a listagem falhar, SHALL exibir mensagem amigável com botão "Tentar novamente".

#### Scenario: Ordem da lista
- **WHEN** existem dois treinos de hoje e um de ontem
- **THEN** os de hoje aparecem primeiro, e entre eles o registrado por último vem antes

#### Scenario: Estado vazio
- **WHEN** o usuário não tem treinos
- **THEN** o card de estado vazio é exibido

#### Scenario: Falha ao listar
- **WHEN** o Xano não responde ao carregar a lista
- **THEN** a página mostra uma mensagem sem detalhes técnicos e o botão "Tentar novamente", que refaz a busca

### Requirement: Registrar treino pelo modal
"+ Novo treino" SHALL abrir o modal "Novo treino" centralizado com overlay (`aria-labelledby` no título, foco preso, foco inicial no primeiro campo, retorno do foco ao botão, fechamento por X com `aria-label="Fechar"`, Esc e clique no overlay, mantendo o conteúdo digitado). Campos, em grid de 2 colunas: Data (padrão hoje em SP) e Duração (min) (sem padrão); Nome (linha inteira, placeholder "Ex.: Peito e tríceps"); Categoria (texto, placeholder "Musculação, corrida...") e Intensidade (texto, placeholder "Leve, moderada, alta"); Observações (textarea redimensionável, linha inteira). Erros SHALL aparecer abaixo de cada campo, em região `aria-live="polite"`. O botão "Salvar treino" SHALL mostrar spinner e ficar desabilitado durante a chamada. Ao salvar com sucesso, o modal SHALL fechar, o formulário SHALL ser limpo, a lista SHALL ser atualizada e o toast verde "Treino registrado" SHALL aparecer no canto superior direito por cerca de 3s. Falhas do Xano SHALL mostrar mensagem amigável acima do botão, mantendo o modal aberto e os dados digitados.

#### Scenario: Duplo clique
- **WHEN** o usuário clica duas vezes em "Salvar treino" rapidamente
- **THEN** apenas um treino é criado

#### Scenario: Fechar com dados digitados
- **WHEN** o usuário digita o nome, fecha com Esc e reabre o modal
- **THEN** o nome digitado continua no campo

#### Scenario: Registro bem-sucedido
- **WHEN** o usuário salva um treino válido
- **THEN** o modal fecha, o treino aparece no topo da lista e o toast "Treino registrado" é exibido

#### Scenario: Persistência
- **WHEN** o usuário recarrega a página depois de registrar
- **THEN** o treino continua na lista

### Requirement: Excluir treino
O botão de exclusão SHALL pedir confirmação ("Excluir este treino?" com Cancelar/Excluir). Confirmada, o treino SHALL ser excluído no Xano, a lista SHALL ser atualizada e o toast "Treino excluído" SHALL ser exibido. Falhas SHALL mostrar mensagem amigável sem remover o item.

#### Scenario: Cancelar exclusão
- **WHEN** o usuário clica em Cancelar na confirmação
- **THEN** nada é excluído

#### Scenario: Confirmar exclusão
- **WHEN** o usuário confirma a exclusão do próprio treino
- **THEN** ele some da lista e o toast "Treino excluído" aparece

### Requirement: Responsividade, microinterações e acessibilidade
A página SHALL funcionar sem rolagem horizontal em 360px, 768px, 1280px e 1920px. No celular o botão "+ Novo treino" SHALL ir para baixo do subtítulo em largura total; o modal SHALL ter largura máxima de cerca de 560px e, no celular, ocupar quase a tela inteira com rolagem interna, campos em coluna única e botão "Salvar treino" sempre visível. Alvos de toque SHALL ter no mínimo 44px. Cards SHALL ter hover sutil (borda azul translúcida, elevação leve); botões SHALL elevar no hover e usar scale 0.98 no clique; transições SHALL durar 150–200ms; o modal SHALL entrar com fade + scale, toasts com slide-in e itens novos com fade-in, tudo respeitando `prefers-reduced-motion`. Todo campo SHALL ter `<label>` associado; toasts SHALL usar `role="status"`. Componentes Radix SHALL usar o azul `#2B8CFF` como destaque (foco de inputs, botões e diálogos sem ciano).

#### Scenario: Celular
- **WHEN** a página é aberta em 360px
- **THEN** o botão "+ Novo treino" ocupa a largura total abaixo do subtítulo, o modal mostra os campos em coluna única e não há rolagem horizontal

#### Scenario: Movimento reduzido
- **WHEN** o sistema operacional pede `prefers-reduced-motion: reduce`
- **THEN** modal, toast e itens aparecem sem animação
