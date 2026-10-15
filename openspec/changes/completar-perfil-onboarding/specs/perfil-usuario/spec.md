## Purpose

Permitir que o usuário autenticado complete (onboarding) e depois edite o próprio Perfil — dados pessoais, biotipo, preferências de treino e de registro — usados para personalizar recomendações, garantindo que cada usuário leia e altere apenas o próprio Perfil.

## Modelos de dados envolvidos

Representação SQL equivalente às tabelas do Xano (`xano/table/user.xs` e `xano/table/perfil.xs`) após esta change:

```sql
CREATE TABLE "user" (
  id          SERIAL PRIMARY KEY,
  created_at  TIMESTAMP DEFAULT now(),
  nome        TEXT,
  email       TEXT UNIQUE,          -- normalizado: trim + minúsculas
  senha       TEXT                  -- hash (tipo password do Xano), nunca retornado
);                                   -- auth = true (emite token de sessão)

CREATE TABLE perfil (
  id                     SERIAL PRIMARY KEY,
  created_at             TIMESTAMP DEFAULT now(),
  user_id                INT UNIQUE REFERENCES "user"(id),   -- 1:1 com user
  nome                   TEXT,
  data_de_nascimento     DATE,
  sexo                   TEXT CHECK (sexo IN ('Feminino','Masculino','Outro')),
  altura_cm              DECIMAL,
  tipo_fisico            TEXT CHECK (tipo_fisico IN ('Ectomorfo','Mesomorfo','Endomorfo')),
  nivel_fisico           TEXT CHECK (nivel_fisico IN ('Iniciante','Intermediário','Avançado')),
  modalidade_fav1        TEXT[]  -- lista sem mínimo no banco (perfil nasce vazio); ≥ 1 exigido ao salvar; cada item em ('Musculação','Cardio','Funcional','Luta',
                                 --   'CrossFit','Yoga','Esportes de areia','Pilates')
  horario_fav_de_treino  TEXT CHECK (horario_fav_de_treino IN ('Madrugada','Manhã','Tarde','Noite')),
  meta_semanal           INT,
  objetivo               TEXT CHECK (objetivo IN (
                           'Hipertrofia (ganho de massa muscular)',
                           'Emagrecimento (perda de gordura)',
                           'Melhorar condicionamento físico',
                           'Preservação de saúde mental')),
  medidas                BOOLEAN DEFAULT false,
  onboarding_concluido   BOOLEAN DEFAULT false,
  data_atualizacao       TIMESTAMP
);
```

## ADDED Requirements

### Requirement: Perfil criado e vinculado no cadastro
Ao concluir o cadastro de uma conta, o sistema SHALL criar exatamente um Perfil vinculado ao `user_id` da nova conta, com `nome` igual ao nome informado no cadastro, `onboarding_concluido = false` e `medidas = false`. Nenhum outro campo SHALL ser preenchido com valores inventados.

#### Scenario: Cadastro cria Perfil vazio vinculado
- **WHEN** uma conta é criada com nome "Ana Souza"
- **THEN** existe um único Perfil com `user_id` da conta, `nome = "Ana Souza"`, `onboarding_concluido = false` e os demais campos vazios

#### Scenario: Um Perfil por usuário
- **WHEN** se tenta criar um segundo Perfil para o mesmo `user_id`
- **THEN** o backend rejeita a operação e o Perfil existente permanece inalterado

### Requirement: Somente o dono lê e edita o próprio Perfil
O backend SHALL expor leitura e edição do Perfil apenas para o usuário autenticado, sempre identificando o Perfil pelo token de sessão (nunca por id informado pelo cliente). Endpoints públicos de listagem ou edição de Perfil e de usuário por id SHALL NOT existir. Requisições sem token válido SHALL ser rejeitadas sem retornar dados. O `user_id` e o `onboarding_concluido` SHALL NOT ser alteráveis diretamente pelo cliente.

#### Scenario: Ler o próprio Perfil
- **WHEN** o usuário A, autenticado, solicita seu Perfil
- **THEN** recebe somente o Perfil cujo `user_id` é o de A

#### Scenario: Tentar acessar Perfil alheio
- **WHEN** o usuário A tenta ler ou editar o Perfil do usuário B por qualquer meio disponível na API
- **THEN** a operação falha ou atua apenas sobre o Perfil de A, e nenhum dado de B é retornado ou alterado

#### Scenario: Sem autenticação
- **WHEN** uma requisição sem token ou com token inválido solicita o Perfil
- **THEN** o backend responde com erro de autenticação e nenhum dado

#### Scenario: Tentar trocar o dono
- **WHEN** o cliente envia `user_id` ou `onboarding_concluido` na edição do Perfil
- **THEN** esses valores são ignorados ou rejeitados e o vínculo do Perfil não muda

#### Scenario: Endpoints públicos removidos
- **WHEN** alguém chama a listagem pública de usuários ou de Perfis, ou a edição por id sem token
- **THEN** o endpoint não existe ou exige autenticação, e nenhum e-mail ou dado de Perfil é exposto

### Requirement: Tela de Perfil carrega os dados atuais
A rota `/perfil` SHALL exibir, para o usuário autenticado, os cards Dados pessoais, Biotipo corporal, Preferências de treino, Preferências de registro, o botão "Salvar perfil" e o card Conta, nessa ordem, preenchidos com os valores atuais do Perfil. A tela SHALL NOT exibir card de metas.

#### Scenario: Abrir Perfil recém-criado
- **WHEN** o usuário acaba de se cadastrar e abre `/perfil`
- **THEN** "Nome completo" vem preenchido com o nome do cadastro e os demais campos aparecem vazios, sem valores pré-selecionados salvos

#### Scenario: Abrir Perfil já preenchido
- **WHEN** o usuário com Perfil salvo abre `/perfil`
- **THEN** todos os campos exibem os valores gravados, incluindo todas as modalidades selecionadas e o estado do switch de medidas

#### Scenario: Ausência do card de metas
- **WHEN** a tela é exibida
- **THEN** não há card "Minhas metas" nem botão "Salvar metas"

### Requirement: Campos e opções do Perfil
A tela SHALL oferecer exatamente estas entradas e opções, mapeadas aos campos do Perfil:
- Nome completo (`nome`, texto); Data de nascimento (`data_de_nascimento`, data); Sexo (`sexo`: Feminino, Masculino, Outro); Altura em cm (`altura_cm`, número).
- Biotipo (`tipo_fisico`, escolha única entre Ectomorfo, Mesomorfo, Endomorfo, cada um com sua descrição).
- Condicionamento (`nivel_fisico`: Iniciante, Intermediário, Avançado); Horário habitual (`horario_fav_de_treino`: Madrugada, Manhã, Tarde, Noite); Meta semanal de treinos (`meta_semanal`, inteiro); Objetivo (`objetivo`: os 4 valores do Xano).
- Modalidades favoritas (`modalidade_fav1`, seleção múltipla entre Musculação, Cardio, Funcional, Luta, CrossFit, Yoga, Esportes de areia, Pilates).
- Registrar medidas corporais (`medidas`, liga/desliga).
Selects SHALL NOT gravar um valor de espaço reservado como "Selecione".

#### Scenario: Seleção múltipla de modalidades
- **WHEN** o usuário marca Musculação e Yoga e salva
- **THEN** o Perfil grava a lista com exatamente esses dois valores e ambos aparecem ativos ao reabrir

#### Scenario: Biotipo é escolha única
- **WHEN** o usuário seleciona Ectomorfo e depois Endomorfo
- **THEN** apenas Endomorfo fica selecionado

#### Scenario: Placeholder não é valor
- **WHEN** um select permanece em "Selecione"
- **THEN** o campo é tratado como vazio na validação e nunca é enviado como valor

### Requirement: Validação dos campos obrigatórios
Todos os campos do Perfil exibidos SHALL ser obrigatórios para salvar: nome (1 a 50 caracteres após remover espaços), data de nascimento (data válida no passado e não anterior a 1900-01-01), sexo, altura (número entre 100 e 250 cm), biotipo, condicionamento, horário habitual, meta semanal (inteiro entre 1 e 14), objetivo e ao menos uma modalidade. A validação SHALL ocorrer no backend do Reflex antes de chamar o Xano e SHALL ser repetida pelo Xano. Cada erro SHALL aparecer abaixo do respectivo campo, em região `aria-live="polite"`.

#### Scenario: Salvar com campos vazios
- **WHEN** o usuário clica em "Salvar perfil" com campos obrigatórios vazios
- **THEN** nenhuma chamada de gravação é feita e cada campo vazio exibe sua mensagem de erro

#### Scenario: Data no futuro
- **WHEN** a data de nascimento é posterior à data atual
- **THEN** o campo exibe erro e o Perfil não é salvo

#### Scenario: Altura implausível
- **WHEN** a altura é 0, negativa, não numérica, menor que 100 ou maior que 250
- **THEN** o campo exibe erro e o Perfil não é salvo

#### Scenario: Backend rejeita dados inválidos
- **WHEN** uma requisição ao Xano chega com campo obrigatório ausente ou fora das opções
- **THEN** o Xano rejeita a gravação e o Perfil permanece inalterado

### Requirement: Salvar o Perfil e concluir o onboarding
Ao salvar com todos os campos válidos, o sistema SHALL atualizar o Perfil do usuário autenticado, registrar `data_atualizacao` com o horário do servidor e, se `onboarding_concluido` for `false`, marcá-lo como `true`. Durante a chamada, o botão SHALL exibir spinner e ficar desabilitado. Após sucesso, o sistema SHALL exibir a mensagem "Perfil salvo". Falhas do Xano SHALL exibir uma mensagem amigável acima do botão, sem detalhes técnicos, e SHALL NOT alterar `onboarding_concluido`.

#### Scenario: Concluir onboarding
- **WHEN** um usuário em onboarding salva um Perfil válido
- **THEN** o Perfil é gravado, `onboarding_concluido` passa a `true`, "Perfil salvo" é exibido e o usuário é levado a `/inicio`

#### Scenario: Editar após onboarding
- **WHEN** um usuário com onboarding concluído salva alterações válidas
- **THEN** o Perfil é atualizado, "Perfil salvo" é exibido e o usuário permanece em `/perfil`

#### Scenario: Duplo clique
- **WHEN** o usuário clica duas vezes rapidamente em "Salvar perfil"
- **THEN** apenas uma gravação é enviada

#### Scenario: Falha do Xano
- **WHEN** o Xano está indisponível ou retorna erro inesperado
- **THEN** a tela mostra "Não foi possível salvar seu perfil agora. Tente novamente em instantes.", sem código ou mensagem técnica, e o usuário continua em onboarding se ainda não o tinha concluído

### Requirement: Modo onboarding
Enquanto `onboarding_concluido` for `false`, `/perfil` SHALL exibir no topo a faixa "Complete seu perfil para personalizar suas recomendações". Após a conclusão, a faixa SHALL NOT ser exibida.

#### Scenario: Faixa visível no onboarding
- **WHEN** um usuário com `onboarding_concluido = false` abre `/perfil`
- **THEN** a faixa de onboarding é exibida

#### Scenario: Faixa oculta após concluir
- **WHEN** um usuário com `onboarding_concluido = true` abre `/perfil`
- **THEN** a faixa não é exibida

### Requirement: Layout, responsividade e acessibilidade do Perfil
A tela SHALL usar os tokens visuais de `styles/theme.py`, conteúdo centralizado com largura máxima de cerca de 960px e sem rolagem horizontal em 360px, 768px, 1280px e 1920px. Em larguras de celular, as grades de 2 colunas e os cards de biotipo SHALL virar coluna única, os chips SHALL quebrar linha e o botão "Salvar perfil" SHALL ocupar a largura total. Todo controle interativo SHALL ter alvo de toque de pelo menos 44px, foco visível e rótulo associado; os campos SHALL ter `autocomplete` adequado; o biotipo SHALL ser um grupo de rádio navegável por setas; os chips SHALL expor `aria-pressed`. Animações de entrada SHALL ser desativadas sob `prefers-reduced-motion`.

#### Scenario: Celular
- **WHEN** a tela é aberta em 360px
- **THEN** campos, biotipos e botão de salvar ficam em coluna única e não há rolagem horizontal

#### Scenario: Teclado no biotipo
- **WHEN** o foco está no grupo de biotipo e o usuário pressiona as setas
- **THEN** a seleção percorre as três opções e o foco permanece visível

#### Scenario: Leitor de tela nos chips
- **WHEN** um chip de modalidade é ativado
- **THEN** seu `aria-pressed` passa a `true`

#### Scenario: Movimento reduzido
- **WHEN** o sistema operacional solicita movimento reduzido
- **THEN** os cards aparecem sem animação de entrada
