## Purpose

Permitir que o usuário autenticado registre, consulte, edite e exclua as próprias noites de sono (início, fim, qualidade e observações), com duração calculada e dados consistentes para as recomendações de recuperação e intensidade de treino e para os Relatórios.

## Modelos de dados envolvidos

Tabela `Sono` do Xano (ajustada nesta change):

```sql
-- equivalente relacional da tabela Sono do Xano
CREATE TABLE sono (
    id               INTEGER PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES "user"(id),
    inicio_sono      TIMESTAMP NOT NULL,          -- UTC
    fim_sono         TIMESTAMP NOT NULL,          -- UTC, > inicio_sono
    duracao_minutos  INTEGER NOT NULL,            -- 15 a 1440, calculado pelo servidor
    qualidade_sono   SMALLINT NOT NULL CHECK (qualidade_sono BETWEEN 1 AND 5),
    observacoes      VARCHAR(500),
    created_at       TIMESTAMP NOT NULL DEFAULT now(),
    updated_at       TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX sono_user_id_idx ON sono (user_id);
-- RLS: leitura e escrita somente onde user_id = usuário do token
```

## ADDED Requirements

### Requirement: Tela Sono na área logada
A rota `/sono` SHALL ser privada, seguir as mesmas regras de sessão e onboarding das demais rotas privadas e exibir a navbar com o item "Sono" ativo (`aria-current="page"`). A tela SHALL exibir um cabeçalho com ícone de lua em badge circular, o título "Sono" e o subtítulo "Registre início, fim e qualidade do sono. Esses dados alimentam as recomendações de recuperação e de intensidade de treino.". Abaixo, SHALL exibir o card do formulário e, depois dele, a área de registros. A tela SHALL NOT mostrar o aviso de "em construção".

#### Scenario: Acesso autenticado
- **WHEN** um usuário com sessão válida e onboarding concluído abre `/sono`
- **THEN** a navbar mostra "Sono" com `aria-current="page"`, e o cabeçalho, o formulário e a área de registros são exibidos

#### Scenario: Acesso sem sessão
- **WHEN** uma pessoa sem sessão abre `/sono`
- **THEN** é redirecionada para `/login` e nenhum registro de sono é exibido

### Requirement: Formulário de registro de sono
O card do formulário SHALL conter, nesta ordem: "Início do sono" e "Fim do sono" lado a lado (campos de data e hora); "Qualidade do sono" como uma escala numérica de 5 opções de seleção única (1 Muito ruim, 2 Ruim, 3 Regular, 4 Bom, 5 Muito bom), cada uma com estrela, número e rótulo; e "Observações (opcional)", texto livre de até 500 caracteres com o placeholder "Acordou cansado? Sonhos, interrupções, cafeína à noite…". O rodapé do card SHALL mostrar "Duração: <valor>" à esquerda e o botão "Salvar sono" à direita. Data e hora são livres: ao abrir a tela, início, fim e qualidade SHALL vir vazios. Ao clicar em Início ou Fim do sono, o sistema SHALL abrir o calendário com as opções de hora e minuto. Campos ainda não preenchidos SHALL NOT exibir mensagem de erro antes de uma tentativa de salvar.

#### Scenario: Valores iniciais
- **WHEN** o usuário abre `/sono`
- **THEN** início e fim estão vazios, nenhuma qualidade está selecionada, a duração mostra "—" e nenhuma mensagem de erro aparece

#### Scenario: Calendário ao clicar
- **WHEN** o usuário clica no campo Início do sono
- **THEN** abre um calendário para escolher a data, com as opções de hora e minuto

#### Scenario: Seleção única de qualidade
- **WHEN** o usuário seleciona "4 Bom" e depois "2 Ruim"
- **THEN** apenas "2 Ruim" fica selecionada, com a estrela preenchida e o estado de selecionada exposto à tecnologia assistiva

#### Scenario: Limite de observações
- **WHEN** o usuário tenta digitar mais de 500 caracteres em Observações
- **THEN** o campo não aceita além de 500 caracteres

### Requirement: Duração calculada
A duração SHALL ser calculada como fim − início, não SHALL ser editável e SHALL ser atualizada sempre que o início ou o fim mudarem. O formato SHALL ser "<h>h" para horas cheias, "<h>h <m>min" para horas com minutos e "<m>min" abaixo de 1 hora. Quando o início ou o fim estiverem vazios, inválidos, ou o fim não for posterior ao início, a duração SHALL mostrar "—".

#### Scenario: Horas cheias
- **WHEN** o início é 23:00 e o fim é 07:00 do dia seguinte
- **THEN** a duração mostra "8h"

#### Scenario: Horas e minutos
- **WHEN** o início é 23:30 e o fim é 07:00 do dia seguinte
- **THEN** a duração mostra "7h 30min"

#### Scenario: Menos de uma hora
- **WHEN** o início é 14:00 e o fim é 14:45 do mesmo dia
- **THEN** a duração mostra "45min"

#### Scenario: Valores inválidos
- **WHEN** o fim é anterior ou igual ao início, ou um dos campos está vazio
- **THEN** a duração mostra "—"

### Requirement: Validação do registro
Antes de salvar, o sistema SHALL validar e, se houver erro, SHALL exibir a mensagem abaixo do campo correspondente, ligada a ele via `aria-describedby`, sem enviar nada ao servidor:
- início e fim obrigatórios ("Informe o início do sono." / "Informe o fim do sono.");
- fim posterior ao início ("O fim do sono precisa ser depois do início.");
- duração mínima de 15 minutos ("O registro precisa ter pelo menos 15 minutos.") e máxima de 24 horas ("O registro pode ter no máximo 24 horas.");
- fim não futuro ("O fim do sono não pode estar no futuro.");
- qualidade obrigatória entre 1 e 5 ("Selecione a qualidade do sono.");
- observações com no máximo 500 caracteres.
O botão "Salvar sono" SHALL ficar desabilitado enquanto início, fim ou qualidade não forem válidos. O servidor SHALL repetir essas validações e rejeitar dados inválidos, mesmo que o app seja contornado.

#### Scenario: Botão desabilitado sem qualidade
- **WHEN** início e fim são válidos e nenhuma qualidade está selecionada
- **THEN** o botão "Salvar sono" está desabilitado

#### Scenario: Botão habilitado com dados válidos
- **WHEN** início e fim são válidos (fim no passado, duração entre 15 min e 24 h) e uma qualidade está selecionada
- **THEN** o botão "Salvar sono" está habilitado

#### Scenario: Fim antes do início
- **WHEN** o fim é anterior ao início
- **THEN** a mensagem "O fim do sono precisa ser depois do início." aparece abaixo do Fim do sono e o botão fica desabilitado

#### Scenario: Fim no futuro
- **WHEN** o fim está depois do momento atual
- **THEN** a mensagem "O fim do sono não pode estar no futuro." aparece abaixo do Fim do sono e o botão fica desabilitado

#### Scenario: Duração fora da faixa
- **WHEN** a duração é de 10 minutos ou de 25 horas
- **THEN** a mensagem correspondente de mínimo ou de máximo aparece e o botão fica desabilitado

#### Scenario: Validação no servidor
- **WHEN** uma requisição ao servidor chega com qualidade 7 ou com fim antes do início
- **THEN** o servidor rejeita a requisição como entrada inválida e nada é gravado

### Requirement: Períodos sem sobreposição
O sistema SHALL impedir que um registro de sono se sobreponha a outro registro do mesmo usuário. Dois períodos se sobrepõem quando o início de um é anterior ao fim do outro e vice-versa; períodos apenas encostados (fim de um igual ao início do outro) não se sobrepõem. Ao editar, o próprio registro SHALL ser ignorado na checagem. A checagem SHALL acontecer no servidor (fonte da verdade) e também no app com os registros já carregados. Em caso de conflito, SHALL ser exibida a mensagem "Já existe um registro de sono nesse período (<data> <início> → <fim>). Ajuste os horários." e nada SHALL ser gravado. Registros de outros usuários SHALL NOT influenciar a checagem.

#### Scenario: Conflito com registro existente
- **WHEN** já existe um registro de 20/10 23:00 a 21/10 07:00 e o usuário tenta salvar 21/10 06:00 a 21/10 08:00
- **THEN** o registro não é salvo e a mensagem de conflito citando o período existente é exibida

#### Scenario: Períodos encostados
- **WHEN** já existe um registro que termina às 07:00 e o usuário salva outro que começa às 07:00
- **THEN** o registro é salvo normalmente

#### Scenario: Edição do próprio período
- **WHEN** o usuário edita um registro e altera apenas a qualidade
- **THEN** a checagem de sobreposição ignora o próprio registro e a edição é salva

#### Scenario: Registro de outro usuário
- **WHEN** outro usuário tem um registro no mesmo período
- **THEN** o registro do usuário atual é salvo normalmente

### Requirement: Salvar registro de sono
Ao acionar "Salvar sono" com dados válidos, o sistema SHALL gravar o registro vinculado ao usuário do token, com início e fim em UTC, a duração em minutos calculada pelo servidor, a qualidade (1–5), as observações (sem espaços nas pontas, vazio vira nulo), `created_at` e `updated_at`. Durante o envio, o botão SHALL mostrar carregamento e ignorar cliques repetidos. No sucesso, o sistema SHALL mostrar o aviso "Sono registrado com sucesso", inserir o registro no topo da lista com a animação de entrada, esconder o estado vazio, limpar qualidade e observações e deixar início e fim vazios. Na falha, SHALL mostrar uma mensagem de erro sem detalhes técnicos, com a opção "Tentar novamente", preservando o que foi digitado. Se a sessão expirar, SHALL redirecionar para `/login`.

#### Scenario: Primeiro registro
- **WHEN** o usuário sem registros salva um sono válido
- **THEN** aparece "Sono registrado com sucesso", o estado vazio some, o registro aparece no topo da lista e o formulário fica vazio de novo

#### Scenario: Clique duplo
- **WHEN** o usuário clica duas vezes seguidas em "Salvar sono"
- **THEN** apenas um registro é criado

#### Scenario: Falha do servidor
- **WHEN** o servidor está indisponível ao salvar
- **THEN** uma mensagem de erro com "Tentar novamente" é exibida, os campos preenchidos são mantidos e nenhum registro aparece na lista

#### Scenario: Sessão expirada
- **WHEN** o servidor responde que o token não é mais válido
- **THEN** a sessão local é descartada e o usuário é redirecionado para `/login`

### Requirement: Lista de registros de sono
A área de registros SHALL listar somente os registros do usuário autenticado, do mais recente para o mais antigo (por início do sono). Cada item SHALL mostrar a data (do fim do sono, no fuso do usuário), o intervalo "HH:MM → HH:MM", a duração no formato da tela, a qualidade (estrelas e rótulo) e as observações, quando houver. Enquanto carrega, SHALL exibir um skeleton da lista. Sem registros, SHALL exibir o estado vazio com ícone de lua, o título "Nenhum registro de sono ainda" e o texto "Preencha o horário de início e de fim do sono para começar.". Se o carregamento falhar, SHALL exibir uma mensagem de erro com o botão "Tentar novamente", que refaz a busca.

#### Scenario: Ordem da lista
- **WHEN** o usuário tem registros das noites de 18/10, 20/10 e 19/10
- **THEN** a lista mostra 20/10, 19/10 e 18/10, nessa ordem

#### Scenario: Estado vazio
- **WHEN** o usuário não tem registros de sono
- **THEN** a área mostra "Nenhum registro de sono ainda" e "Preencha o horário de início e de fim do sono para começar."

#### Scenario: Erro ao carregar
- **WHEN** a busca dos registros falha
- **THEN** a área mostra uma mensagem de erro e o botão "Tentar novamente"; ao clicar nele, a busca é refeita

#### Scenario: Privacidade
- **WHEN** dois usuários têm registros de sono
- **THEN** cada um vê apenas os próprios registros, e um pedido para ler, editar ou excluir o registro de outro usuário é respondido como "não encontrado"

### Requirement: Editar registro de sono
Cada item da lista SHALL ter a ação "Editar". Ela SHALL carregar o registro no mesmo formulário, que passa a indicar o modo de edição, troca o botão para "Salvar alterações" e oferece "Cancelar edição". Salvar SHALL aplicar as mesmas validações (ignorando o próprio registro na sobreposição), atualizar `updated_at`, atualizar o item na lista na posição correta e mostrar "Registro de sono atualizado". Cancelar SHALL deixar o formulário vazio de novo sem alterar nada.

#### Scenario: Editar qualidade
- **WHEN** o usuário clica em "Editar" num registro, muda a qualidade para "5 Muito bom" e salva
- **THEN** o item da lista passa a mostrar "Muito bom" sem recarregar a página e o formulário volta ao modo de novo registro

#### Scenario: Cancelar edição
- **WHEN** o usuário clica em "Editar" e depois em "Cancelar edição"
- **THEN** o registro não é alterado e o formulário fica vazio de novo

### Requirement: Excluir registro de sono
Cada item da lista SHALL ter a ação "Excluir", que abre uma confirmação ("Excluir registro de sono?") com "Cancelar" e "Excluir". Confirmando, o sistema SHALL excluir o registro no servidor, removê-lo da lista sem recarregar a página e mostrar "Registro de sono excluído". Se era o último registro, SHALL exibir o estado vazio. Se o registro em edição for excluído, o formulário SHALL voltar ao modo de novo registro.

#### Scenario: Confirmar exclusão
- **WHEN** o usuário clica em "Excluir" e confirma
- **THEN** o registro some da lista e o aviso "Registro de sono excluído" é exibido

#### Scenario: Desistir da exclusão
- **WHEN** o usuário clica em "Excluir" e depois em "Cancelar"
- **THEN** nada é excluído

### Requirement: Fuso horário
Os horários SHALL ser digitados e exibidos no horário de Brasília (UTC−3) para todos os usuários, independentemente do fuso do navegador, e SHALL ser gravados em UTC. O dia SHALL virar às 00:00 de Brasília: um período que passa da meia-noite SHALL ser exibido com as duas datas.

#### Scenario: Conversão para UTC
- **WHEN** o usuário registra o início às 23:00 de 20/10
- **THEN** o servidor recebe o início como 21/10 02:00 UTC e a lista exibe 23:00

#### Scenario: Período que passa da meia-noite
- **WHEN** o registro vai de 20/10 23:00 a 21/10 07:00
- **THEN** a lista exibe "20/10 23:00 → 21/10 07:00" e a data do item é 21/10/2026

#### Scenario: Período no mesmo dia
- **WHEN** o registro vai de 21/10 14:00 a 21/10 14:45
- **THEN** a lista exibe "14:00 → 14:45"

### Requirement: Resumo de sono para recomendações e relatórios
O sistema SHALL oferecer, para outros módulos e sem depender da tela, um resumo das últimas N noites do usuário com: quantidade de registros, duração média em minutos, qualidade média e a lista das noites (data, duração em minutos e qualidade), ordenada da mais recente para a mais antiga. Sem registros, o resumo SHALL informar quantidade 0 e médias nulas. A lógica de recomendação SHALL NOT ficar na tela Sono.

#### Scenario: Resumo das últimas 7 noites
- **WHEN** o usuário tem 10 registros e o resumo é pedido para 7 noites
- **THEN** o resumo considera apenas os 7 registros mais recentes e devolve as médias de duração e de qualidade

#### Scenario: Sem registros
- **WHEN** o usuário não tem registros
- **THEN** o resumo devolve quantidade 0 e médias nulas

### Requirement: Responsividade e acessibilidade
A tela SHALL usar os mesmos breakpoints da tela de Refeições. Em telas de até 640px, início e fim SHALL ficar empilhados, as opções de qualidade SHALL quebrar linha e o botão de salvar SHALL ocupar a largura total, sem rolagem horizontal. Todos os campos SHALL ter rótulo associado e foco visível. O grupo de qualidade SHALL ser operável por teclado e expor o estado selecionado. Os alvos de toque SHALL ter no mínimo 44px em dispositivos de toque.

#### Scenario: Celular
- **WHEN** a tela é exibida com 360px de largura
- **THEN** início e fim aparecem um abaixo do outro, o botão "Salvar sono" ocupa a largura total e não há rolagem horizontal

#### Scenario: Teclado
- **WHEN** o usuário navega com Tab até as opções de qualidade e pressiona Enter ou Espaço
- **THEN** a opção focada é selecionada e o foco é visível
