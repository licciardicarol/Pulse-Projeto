## Context

`Registro_Peso` no Xano tinha só `Peso` (decimal) e `Data_Horario` (timestamp), sem dono, com CRUDs públicos. A navbar já tem "Peso" (ícone `scale`) e não tem "Social". Sessão (`SessaoState`, com confirmação reaproveitada por 60 s), `app_shell`, toasts e o padrão de Refeições (`logic/` + `State` + `pages/`) já existem.

## Goals / Non-Goals

**Goals:** registrar, listar, resumir e excluir pesos do próprio usuário; horário exibido sem deslocamento de fuso; nenhum valor inventado.

**Non-Goals:** IA, meta de peso, gráficos, edição, medidas corporais, `observacoes`.

## Decisions

### D1. Dono = `user_id` → `user`
Igual a Refeições: o endpoint usa `$auth.id` direto, sem buscar o Perfil. O `domain-model.md` registra a exceção (o modelo original dizia `profile_id`).
- *Alternativa descartada:* `profile_id` → `Perfil` (consulta extra a cada chamada).

### D2. Campos em minúsculas
`Peso` → `peso` e `Data_Horario` → `data_horario`, no padrão das outras tabelas. O nome da tabela continua `Registro_Peso`.

### D3. Fuso fixo UTC−03:00 (horário de Brasília)
O Xano guarda `timestamp` como milissegundos em UTC. O Reflex junta Data + Horário com `timezone(timedelta(hours=-3))` e envia milissegundos (sem ambiguidade de formato); ao exibir, converte os milissegundos de volta para UTC−03:00. O Brasil não tem horário de verão desde 2019. A data/hora padrão do formulário também é "agora" em UTC−03:00, calculada no servidor.
- *Alternativa descartada:* `zoneinfo("America/Sao_Paulo")` — no Windows exige o pacote `tzdata` (biblioteca nova).

### D4. Validação do peso
Aceita vírgula ou ponto; obrigatório; numérico; entre 20 e 400 kg; no máximo 2 casas decimais (cabe em decimal(5,2)). Data e horário obrigatórios, e a combinação não pode estar no futuro. Mais de um registro por dia é permitido. O Xano repete faixa, casas e data futura.

### D5. Resumo
- **Peso atual:** registro com maior `data_horario` (empate: maior `created_at`), não a ordem de criação.
- **Desde o 1º registro:** peso atual − peso do registro com menor `data_horario`, com sinal ("-1,2 kg", "+0,8 kg", "0,0 kg"); "—" com um único registro. Sem cor de bom/ruim.
- **Falta para a meta:** sempre "—" com "Disponível em breve"; `# TODO: integração futura com IA (falta para a meta)` onde o cartão é montado.
- Formato pt-BR com 1 casa decimal, ou 2 quando o valor tem centésimos (70,0 kg; 70,25 kg).

### D6. Formulário fixo na página (sem modal)
Card com Data (`input type=date`, máx. hoje), Horário (`input type=time`) e Peso (`inputmode="decimal"`), botão "Salvar registro". Ao salvar, limpa só o Peso e atualiza Data/Horário para agora.

### D7. Exclusão e toasts
Mesmo padrão de Refeições: `rx.alert_dialog` "Excluir este registro?", toasts verdes "Peso registrado"/"Registro excluído" no canto superior direito (~3 s) e mensagem própria para o limite do Xano (429).

## Risks / Trade-offs

- [Horário de verão voltar no Brasil] → trocar a constante de fuso por `zoneinfo` (+ `tzdata`) numa change futura.
- [Registros antigos sem dono] → ficam invisíveis; podem ser apagados na tabela pela usuária.
- [Lista sem paginação] → aceitável no MVP.

## Migration Plan

1. Xano (usuária, no site): criar `user_id` (referência a `user`) + índice, renomear campos, criar os 3 endpoints `/me`, apagar os 5 CRUDs públicos; `xano workspace pull`.
2. Código Reflex nesta branch → `pytest` → validação no navegador → PR.
- **Rollback:** reverter o commit do Reflex; CRUDs públicos podem ser recriados pelo histórico do Git.
