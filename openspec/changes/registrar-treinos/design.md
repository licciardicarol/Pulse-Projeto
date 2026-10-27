## Context

Ver `proposal.md`. Depende da sessão (`SessaoState.ensure_session`), da navbar/`app_shell`, do cliente Xano e do tema azul criados em `completar-perfil-onboarding` e `registrar-refeicoes`. O push de endpoints pelo CLI do Xano falha no servidor: tabela e endpoints são alterados no site e sincronizados por pull.

## Goals / Non-Goals

**Goals:**
- Toda regra de negócio (validação, "hoje" em SP, ordenação, formatação) em `logic/treinos.py`, pura e testada.
- Nenhum campo, opção ou valor além do schema do Xano.

**Non-Goals:**
- Edição, filtros, paginação, métricas, exercícios.

## Decisions

### D1. Dono por `user_id` → `user`
Mesmo padrão aprovado em Refeições: os endpoints `treinos/me` usam `$auth.id` do token. Não há `profile_id` no Xano.
- *Alternativa:* `profile_id` → `Perfil`, como no domain-model antigo; exigiria uma consulta extra ao Perfil em cada chamada.

### D2. Categoria e Intensidade em texto livre, com limite
O servidor já tem `categoria` e `intensidade` como `text` (trim). A UI usa inputs de texto com os placeholders da referência ("Musculação, corrida..." e "Leve, moderada, alta"); categoria até 40 e intensidade até 20 caracteres, validados no app e no endpoint. Como não há select, não há destaque do Radix a sobrescrever nesses campos. O enum legado `tipo` não é usado.
- *Alternativa descartada:* converter para enum (alteraria campos já criados no servidor).

### D3. Índice em `user_id`
Toda listagem filtra por `user_id`; o índice btree segue o padrão de `Refeicoes`. Não é um campo novo.

### D4. Duração em minutos (`duracao_minutos`), não derivada de `inicio`/`fim`
A tela pede só a duração. `inicio`/`fim` ficam intocados.

### D5. "Hoje" em America/Sao_Paulo com UTC−3 fixo
`logic/treinos.get_today_sao_paulo(agora_utc)` usa `timezone(timedelta(hours=-3))`: o Brasil não tem horário de verão desde 2019, e `zoneinfo` no Windows exigiria instalar `tzdata` (biblioteca nova). O valor é calculado no State (servidor), então não depende do fuso do navegador. O endpoint `POST treinos/me` também recusa datas posteriores ao dia atual em SP (`"now"|format_timestamp:"Y-m-d":"America/Sao_Paulo"`).
- *Risco:* se o Brasil voltar a ter horário de verão, a constante precisa mudar (um ponto só, coberto por teste).

### D6. Ordenação no app
`GET treinos/me` devolve a lista sem ordem; `sort_treinos` ordena por `data` desc e `id` desc (`created_at` é privado e não volta na API).

### D7. Componentes reaproveitados de Refeições
`rx.dialog` (foco preso, Esc, overlay, retorno do foco), `rx.alert_dialog` para exclusão, `rx.toast.success(position="top-right", duration=3000)`. Fechar o modal não limpa o formulário; só o sucesso limpa.

## Risks / Trade-offs

- [Campos opcionais no banco] → obrigatoriedade garantida nos inputs do endpoint e no app.
- [Lista sem paginação] → aceitável no MVP.
- [Limite de 10 req/20 s do Xano] → reaproveita o cache de sessão e a mensagem de 429 de Refeições.

## Migration Plan

1. Xano: índice em `Treinos.user_id`, 3 endpoints `treinos/me`, remoção dos 5 CRUDs públicos → pull para `xano/`.
2. Código Reflex nesta branch → `pytest` → validação no navegador e RLS com duas contas → PR.
- **Rollback:** reverter o commit do Reflex; os endpoints públicos podem ser recriados a partir do histórico do Git; os campos novos são opcionais e não quebram nada.
