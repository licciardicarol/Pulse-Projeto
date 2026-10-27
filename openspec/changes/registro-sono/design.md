## Context

- A área logada (navbar, `app_shell`, `SessaoState`, `xano_client`) e a tela de **Refeições** (`pages/refeicoes_page.py`, `states/refeicoes_state.py`, `logic/refeicoes.py`) já existem nesta branch. **Refeições é a referência de padrão**: layout (`ref-page` com 1200px, cabeçalho com badge circular + título + subtítulo), card (`ref-item`/`ref-total`), input (`ref-input`, inclusive data nativa com `color-scheme: dark`), contador, erro por campo (`ref-error-text` + `aria-describedby`), erro geral (`ref-global-error`), botões (`ref-button`, `ref-button-secondary`, `ref-button-danger`), skeleton (`ref-skeleton`), estado vazio (`ref-empty`), erro da lista (`ref-error` + "Tentar novamente"), item com animação `ref-fade-in`, confirmação com `rx.alert_dialog` (`ref-alert`) e toasts `rx.toast` com `ESTILO_TOAST_SUCESSO`.
- Padrão de dados de Refeições: `start_page` (após `ensure_session`) chama `rx.call_script` para obter dados do navegador e o callback `load_*` busca a lista; a ordenação é feita no app; `XanoError(tipo)` sem texto do servidor, `nao_autorizado` → limpa sessão e vai para `/login`, `limite_requisicoes` → mensagem própria (`get_failure_message`).
- A tabela `Sono` atual não tem `user_id`, `observacoes`, `duracao_minutos` nem `updated_at`, e a qualidade é enum de textos. Os endpoints `sono` e `sono/{id}` são CRUDs públicos.
- O push de endpoints pelo CLI do Xano falha no servidor; endpoints são criados no site e sincronizados por pull (mesma situação de Refeições).

## Goals / Non-Goals

**Goals:**
- Tela `/sono` visualmente indistinguível em padrão de Refeições, usando os mesmos componentes e classes, sem cores ou medidas fora das já usadas.
- Validação única em Python puro (`logic/sono_registro.py`), usada pelo State e coberta por pytest. O Xano repete as regras críticas.
- Resumo das últimas noites exposto por função pura, desacoplado da tela.

**Non-Goals:**
- Editar refeições (Refeições continua sem edição; só Sono ganha).
- Picker de data/hora customizado em JS.
- Unificar o CSS de Perfil com o de Refeições.

## Decisions

1. **Reusar Refeições sem alterá-la (decisão da pessoa responsável).** `sono_page.py` importa `REFEICOES_PAGE_CSS` e o injeta antes de `SONO_PAGE_CSS` no `app_shell`, usando as mesmas classes `ref-*` (página, cabeçalho, botões, input, campo, erro, skeleton, vazio, erro da lista, item, alerta). As funções de componente de Refeições são locais e presas ao `RefeicoesState`, então Sono tem as suas próprias (`page_header`, `empty_state`, `list_error`, `field_error`, `delete_dialog`), com a mesma estrutura e as mesmas classes.
   - *Alternativa descartada (por ora):* extrair tudo para `components/registro_ui.py`, o que mudaria `refeicoes_page.py`. Fica para uma change de limpeza.

2. **Feedback reaproveitado por import.** `sono_state.py` importa `ESTILO_TOAST_SUCESSO` e `get_failure_message` de `refeicoes_state.py`, sem alterar esse arquivo.

3. **Nomes de campos seguem o `domain-model.md` e o padrão do Xano, não o briefing.** `inicio_sono`, `fim_sono`, `qualidade_sono`, `observacoes`, `duracao_minutos`, `created_at` e `updated_at`, com dono por `user_id` (mesmo padrão de `Refeicoes.user_id`, decisão de 2026-10-20). Alternativa descartada: `inicio`/`fim`/`criado_em`, que diverge da tabela e do restante do Xano.

4. **`qualidade_sono` vira `int` 1–5.** O número facilita médias para recomendações e relatórios. Os rótulos (Muito ruim, Ruim, Regular, Bom, Muito bom) ficam em `logic/sono_registro.py`.

5. **Endpoints `sono/me` no padrão de `refeicoes/me`.**
   - `GET sono/me`: registros do `$auth.id`, sem ordem (o app ordena por `inicio_sono` desc, como em Refeições).
   - `POST sono/me`: inputs `inicio_sono`, `fim_sono` (timestamp em ms UTC), `qualidade_sono` (int, min 1, max 5) e `observacoes` (text, trim, max 500, opcional).
   - `PATCH sono/me/{sono_id}`: mesmos inputs, só sobre registro próprio.
   - `DELETE sono/me/{sono_id}`: só sobre registro próprio, com 404 para registro inexistente ou de outro usuário (igual a `refeicoes/me/{refeicao_id}`).
   - Preconditions: `fim > inicio`, duração entre 15 e 1440 min, `fim <= now` e nenhuma sobreposição (`db.query` com `user_id == $auth.id && inicio_sono < $input.fim_sono && fim_sono > $input.inicio_sono && id != sono_id`). A duração é calculada no servidor. Os CRUDs públicos antigos são removidos.

6. **Conflito de sobreposição: checagem local mais rede de segurança no servidor.** O app tem a lista completa do usuário e checa a sobreposição antes de enviar, para mostrar a mensagem exata com o período em conflito. O conflito no servidor volta como `inputerror` (400 → `XanoError("invalido")`). Como o app já validou tudo localmente, um `invalido` no salvar é tratado como conflito vindo de outro dispositivo: mostra "Já existe um registro de sono nesse período. Atualize a lista e ajuste os horários." e recarrega a lista.

7. **Horário de Brasília fixo, virada do dia às 00:00 (decisão de 2026-10-26).** Todo horário é digitado e exibido em UTC−3, para qualquer usuário, e gravado em UTC. A conversão usa `timezone(timedelta(hours=-3))` (o Brasil não tem horário de verão desde 2019; sem `tzdata`). Períodos que passam da meia-noite mostram as duas datas ("20/10 23:00 → 21/10 07:00"). "Agora" (fim não futuro e limite do calendário) vem do relógio do servidor. Substitui a leitura do fuso do navegador.

8. **Campos de data/hora nativos.** `<input type="datetime-local">` com a classe `ref-input` (a mesma do campo de data de Refeições). O clique em qualquer parte do campo chama `showPicker()` (via `rx.call_script`, no próprio navegador), abrindo o calendário com as colunas de hora e minuto; o navegador fornece "Limpar", "Hoje" e o formato `dd/mm/aaaa hh:mm`. Os campos começam vazios (data e hora livres) e "campo obrigatório" só aparece depois de uma tentativa de salvar.

9. **Formulário em card na própria página (não modal).** O briefing pede o formulário visível em card; Refeições usa modal. O card usa a mesma superfície, borda e raio de `ref-item`/`ref-total`, o grid 50/50 é `ref-form-grid`, os campos são `ref-field`/`ref-label`/`ref-input`, e o rodapé reaproveita o divisor do `ref-dialog-footer`. Só o que não tem equivalente em Refeições fica em `SONO_PAGE_CSS` (prefixo `sono-`): o card do formulário, o rodapé com a duração, os chips de qualidade (mesmos valores de `.perfil-chip` e `.ref-chip`) e o botão de ícone "Editar" (mesmo formato de `.ref-delete`, cor neutra de `.ref-close`).

10. **Validação ao vivo no State.** Cada `on_change` chama `validate_sono(...)` com `agora` injetado e atualiza `duracao_texto`, `erros` e `pode_salvar`. O erro de qualidade só aparece após uma tentativa de salvar, já que o botão fica desabilitado sem qualidade.

11. **Erro ao salvar.** Mesmo padrão de `ref-global-error` do modal de Refeições, acrescido do botão secundário "Tentar novamente", que refaz o envio com os dados preservados. Falhas ao excluir usam `rx.toast.error`, como em Refeições.

12. **Resumo para outros módulos.** `summarize_recent_sleep(registros, quantidade)` em `logic/sono_registro.py` recebe registros brutos do Xano e devolve `{quantidade, duracao_media_minutos, qualidade_media, noites[]}`. Recomendações e Relatórios chamam `xano_client.list_sono(token)` e essa função, sem importar nada da página.

## Risks / Trade-offs

- [Sono depende do CSS de Refeições] → uma mudança em `REFEICOES_PAGE_CSS` afeta Sono também, o que é desejado (mesmo padrão); `tests/test_sono_page.py` verifica que o CSS de Refeições é injetado. Extração para `components/` fica para uma change futura.
- [Funções de componente parecidas nas duas páginas] → são curtas e presas ao State de cada tela; a duplicação é aceita até a extração.
- [Offset fixo erra horários antigos em fusos com horário de verão] → o offset é lido no momento do uso e o Brasil não tem horário de verão atualmente.
- [Mudança de tipo de `qualidade_sono` quebra registros antigos] → os registros existentes são de teste, sem dono. A migração é feita limpando a tabela (ver Migration Plan).
- [Corrida entre dispositivos na sobreposição] → a precondition no Xano é a fonte da verdade, e o app recarrega a lista ao receber o conflito.
- [`datetime-local` nativo varia entre navegadores] → o campo continua digitável e a validação cobre valores vazios ou inválidos.

## Migration Plan

1. No Xano, apagar os registros de teste da tabela `Sono`, aplicar `xano/table/sono.xs`, criar os quatro endpoints `sono/me*` no site, remover `sono` e `sono/{sono_id}` e sincronizar por pull.
2. Fazer o deploy do app. Rollback: reverter a branch, voltando `/sono` ao placeholder. Os endpoints novos podem ficar publicados sem impacto.
