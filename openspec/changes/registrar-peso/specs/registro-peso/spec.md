## Purpose

Permitir que o usuário autenticado registre o próprio peso corporal, acompanhe o peso atual, a variação desde o primeiro registro e o histórico, e exclua registros, com cada usuário acessando apenas os próprios dados e sem nenhum valor inventado.

## Modelos de dados envolvidos

Representação SQL equivalente à tabela `Registro_Peso` do Xano (`xano/table/registro_peso.xs`):

```sql
CREATE TABLE registro_peso (
  id            SERIAL PRIMARY KEY,
  created_at    TIMESTAMP DEFAULT now(),
  user_id       INT REFERENCES "user"(id),   -- dono; preenchido só pelo servidor (token)
  peso          DECIMAL(5,2),                -- kg; 20 a 400, até 2 casas decimais
  data_horario  TIMESTAMP                    -- instante da pesagem (UTC no banco; exibido em UTC−03:00)
);
CREATE INDEX ON registro_peso (user_id);
```

## ADDED Requirements

### Requirement: Somente o dono acessa os próprios registros de peso
O backend SHALL listar, criar e excluir registros de peso apenas para o usuário autenticado, identificado pelo token de sessão. A criação SHALL gravar o dono a partir do token e SHALL ignorar `user_id` enviado pelo cliente. Endpoints públicos de listagem, criação, edição ou exclusão de registros de peso SHALL NOT existir. Requisições sem token válido SHALL ser recusadas sem retornar dados.

#### Scenario: Listar os próprios registros
- **WHEN** o usuário A, autenticado, lista seus registros de peso
- **THEN** recebe apenas registros com `user_id` de A

#### Scenario: Outro usuário não vê nem apaga
- **WHEN** o usuário B tenta listar ou excluir um registro de A
- **THEN** a lista de B não contém o registro de A e a exclusão responde "não encontrado", sem alterar nada

#### Scenario: Sem autenticação
- **WHEN** uma requisição sem token chama qualquer endpoint de peso
- **THEN** o backend responde com erro de autenticação e nenhum dado

### Requirement: Validação do registro de peso
O peso SHALL ser obrigatório, numérico, entre 20 e 400 kg e com no máximo 2 casas decimais, aceitando vírgula ou ponto como separador. Data e horário SHALL ser obrigatórios, e o instante combinado SHALL NOT estar no futuro. Mais de um registro no mesmo dia SHALL ser permitido. O Xano SHALL repetir as validações de faixa, casas decimais e data futura. Erros SHALL aparecer abaixo do campo; falhas do Xano SHALL aparecer acima do botão, com texto amigável e sem detalhes técnicos.

#### Scenario: Peso com vírgula
- **WHEN** o usuário informa "70,5"
- **THEN** o registro é gravado com peso 70.5

#### Scenario: Peso inválido
- **WHEN** o usuário informa "0", "19,9", "400,01", "70,123" ou "abc"
- **THEN** nada é enviado e o campo Peso mostra o erro

#### Scenario: Horário no futuro
- **WHEN** a data é hoje e o horário é posterior ao horário atual
- **THEN** nada é enviado e o campo Horário mostra o erro

### Requirement: Fuso horário sem deslocamento
O sistema SHALL interpretar Data + Horário informados como horário de Brasília (UTC−03:00), enviar ao Xano o instante correspondente e exibir os registros de volta em UTC−03:00, de modo que o horário exibido seja exatamente o informado. Data e horário padrão do formulário SHALL ser o momento atual em UTC−03:00.

#### Scenario: Persistência do horário
- **WHEN** o usuário registra um peso em 23/10/2026 às 17:38 e recarrega a página
- **THEN** o item mostra "23/10/2026 · 17:38"

### Requirement: Página de Peso
A rota `/peso` SHALL ser privada: sem sessão redireciona para `/login`; com onboarding pendente, para `/perfil`. A página SHALL exibir a navbar logada com "Peso" ativo e um cabeçalho com ícone de balança em círculo azul translúcido, título "Peso corporal" e subtítulo "Registre seu peso e acompanhe as variações.". Sem registros, SHALL exibir o card do formulário e, abaixo, um card de borda tracejada com ícone de balança, "Nenhum peso registrado ainda" e "Registre seu peso de hoje para começar a acompanhar sua evolução.". Com registros, SHALL exibir os cartões de resumo, o card do formulário e a lista, nessa ordem.

#### Scenario: Acesso sem login
- **WHEN** uma pessoa sem sessão abre `/peso`
- **THEN** é redirecionada para `/login` sem ver dados

#### Scenario: Estado vazio
- **WHEN** o usuário não tem registros de peso
- **THEN** vê o formulário e o card "Nenhum peso registrado ainda", sem cartões de resumo

### Requirement: Cartões de resumo sem valores inventados
Com registros, a página SHALL exibir três cartões: "PESO ATUAL" (peso do registro com maior `data_horario`, ex. "70,0 kg"); "DESDE O 1º REGISTRO" (peso atual menos o peso do registro com menor `data_horario`, com sinal, ex. "-1,2 kg"/"+0,8 kg", ou "—" com um único registro, sem cor de bom/ruim); e "FALTA PARA A META", sempre "—" com a legenda "Disponível em breve". O sistema SHALL NOT estimar, calcular ou exibir meta de peso.

#### Scenario: Um registro
- **WHEN** existe apenas um registro de 70,0 kg
- **THEN** "Peso atual" mostra "70,0 kg" e "Desde o 1º registro" mostra "—"

#### Scenario: Peso atual pela data da pesagem
- **WHEN** um registro de 69,0 kg com data anterior é criado depois de um de 70,0 kg com data posterior
- **THEN** "Peso atual" mostra "70,0 kg" e "Desde o 1º registro" mostra "+1,0 kg"

#### Scenario: Meta indisponível
- **WHEN** a página exibe os cartões
- **THEN** "Falta para a meta" mostra "—" e "Disponível em breve"

### Requirement: Registrar peso
O botão "Salvar registro" SHALL mostrar spinner e ficar desabilitado durante a chamada (sem duplo envio). Ao salvar com sucesso, SHALL limpar apenas o Peso, atualizar Data e Horário para agora, atualizar resumo e lista e exibir o toast "Peso registrado" no canto superior direito por cerca de 3 s.

#### Scenario: Registro bem-sucedido
- **WHEN** o usuário salva 70,0 kg
- **THEN** o item aparece no topo da lista, o cartão "Peso atual" mostra "70,0 kg", o campo Peso fica vazio e o toast "Peso registrado" é exibido

### Requirement: Lista e exclusão
A lista SHALL mostrar os registros do mais recente para o mais antigo por `data_horario`, cada um como card com o peso em destaque ("70,0 kg"), data e hora em cor secundária ("23/10/2026 · 17:38") e lixeira vermelha com `aria-label` descritivo. Durante o carregamento SHALL exibir skeleton; se a listagem falhar, mensagem amigável com "Tentar novamente". A lixeira SHALL pedir confirmação ("Excluir este registro?" com Cancelar/Excluir); confirmada, o registro SHALL ser excluído, os cartões recalculados e o toast "Registro excluído" exibido. Ao excluir o último registro, a página SHALL voltar ao estado vazio.

#### Scenario: Cancelar exclusão
- **WHEN** o usuário clica em Cancelar
- **THEN** nada é excluído

#### Scenario: Excluir o último registro
- **WHEN** o usuário confirma a exclusão do único registro
- **THEN** o toast "Registro excluído" aparece e a página volta ao estado vazio

### Requirement: Responsividade e acessibilidade
A página SHALL funcionar sem rolagem horizontal em 360px, 768px, 1280px e 1920px, com conteúdo centralizado (largura máxima de cerca de 1200px). Os cartões de resumo SHALL ter 3 colunas no desktop e, no celular, "Peso atual" em largura total e os outros dois lado a lado. O formulário SHALL ter 3 campos em linha no desktop e 1 coluna no celular, com "Salvar registro" em largura total. Alvos de toque SHALL ter no mínimo 44px; todo campo SHALL ter `<label>` associado; erros SHALL usar `aria-live="polite"`; toasts SHALL usar `role="status"`; foco SHALL ser visível em azul `#2B8CFF`; animações SHALL respeitar `prefers-reduced-motion`.

#### Scenario: Celular
- **WHEN** a página é aberta em 360px
- **THEN** os campos ficam em uma coluna, o botão ocupa a largura total e não há rolagem horizontal
