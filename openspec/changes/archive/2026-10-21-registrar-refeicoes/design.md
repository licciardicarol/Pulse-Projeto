## Context

Ver `proposal.md`. Depende da sessão (`SessaoState.ensure_session`), da navbar/`app_shell` e do cliente Xano criados em `completar-perfil-onboarding`. O push de endpoints pelo CLI do Xano falha no servidor; endpoints são criados no site e sincronizados por pull. A parte Xano desta change já foi aplicada e testada (15/15 verificações com duas contas).

## Goals / Non-Goals

**Goals:**
- Toda regra de negócio (validação, tipo sugerido, ordenação, totais, "aguardando análise") em `logic/refeicoes.py`, pura e testada.
- O app nunca envia nem calcula valores nutricionais.

**Non-Goals:**
- Paginação (o volume por usuário é pequeno nesta fase), cache local, atualização em tempo real.

## Decisions

### D1. "Analisada" = `analise_ia` preenchido
O Xano devolve decimais vazios como `0`, então `calorias == 0` não distingue "sem análise" de "0 kcal". A futura integração com IA grava `analise_ia` junto com os valores; até lá toda refeição está "aguardando análise". Totais somam apenas refeições de hoje analisadas.
- *Alternativa:* tratar `calorias > 0` como analisada → erra para alimentos de ~0 kcal e depende de um efeito colateral do Xano.

### D2. Data e hora do navegador
"Hoje" (padrão da data, limite de data futura e filtro dos totais) e a hora usada para sugerir o tipo vêm do navegador, via `rx.call_script` no carregamento da página e na abertura do modal. O servidor do Reflex pode estar em outro fuso.
- O Xano também recusa datas futuras (comparação com `now` em UTC; como a data local nunca é posterior à data UTC no Brasil, não há falso positivo).

### D3. Ordenação no app
`GET refeicoes/me` devolve a lista sem ordem; `sort_refeicoes` ordena por `data_refeicao` desc e `created_at` desc. Evita depender da sintaxe de ordenação do XanoScript.

### D4. Modal com `rx.dialog` (Radix)
Radix Dialog já entrega foco preso, Esc, clique no overlay, `aria-labelledby` e retorno do foco ao gatilho. Fechar não limpa o formulário (o texto digitado é mantido); só o sucesso limpa.

### D5. Tipo com `rx.select` (Radix)
O spec pede item selecionado com fundo azul translúcido e check no dropdown, o que um `<select>` nativo não permite estilizar. O Radix Select tem rótulo associado via `id` no trigger.

### D6. Cor de destaque global
`rx.App(theme=rx.theme(appearance="dark", accent_color="blue"))` e, no CSS do `app_shell`, sobrescrita das variáveis `--accent-*` do Radix para a escala do `#2B8CFF`. Corrige também switch/selects de outras telas.

### D7. Confirmação de exclusão com `rx.alert_dialog`
Mesmo padrão acessível do Radix; o id da refeição a excluir fica no State até confirmar ou cancelar.

### D8. Ponto de extensão da IA
`RefeicoesState.save_meal` recebe o comentário `# TODO: integração futura com IA` logo após o POST bem-sucedido. Nenhum serviço, endpoint ou função de análise é criado.

### D9. Toasts
`rx.toast.success(..., position="top-right", duration=3000)`; o Sonner do Reflex já usa `role="status"`.

### D10. Limite de requisições do Xano (10 a cada 20 s)
O plano gratuito do Xano responde 429 acima de 10 requisições em 20 s, e cada navegação gastava 2 chamadas só para confirmar a sessão. `SessaoState.load_session` passa a reaproveitar a última confirmação por 60 s quando o token é o mesmo (`_token_verificado`, `_verificada_em` só no servidor); `clear_session` zera esse cache. O 429 vira o tipo `limite_requisicoes` no cliente, com a mensagem "Muitas ações em pouco tempo. Aguarde alguns segundos e tente novamente.", e a tela de erro da sessão ganha o botão "Tentar novamente", que recarrega a página para refazer todos os `on_load`.
- *Alternativa descartada:* upgrade do plano do Xano (custo) ou só a mensagem (o erro continuaria frequente).

## Risks / Trade-offs

- [Cache de 60 s da sessão] → um token revogado em outro lugar continua aceito por até 60 s no Reflex; o Xano recusa qualquer chamada de dados com 401, que descarta a sessão e leva ao `/login`.
- [Data do navegador manipulável] → o Xano também valida data futura; os totais só afetam a visão do próprio usuário.
- [Lista sem paginação cresce] → aceitável no MVP; paginação fica para uma change futura.
- [Sobrescrever `--accent-*` do Radix pode mudar outras telas] → verificar Perfil e autenticação nas capturas da validação final.

## Migration Plan

1. Xano: aplicado (campos, índice, 3 endpoints, CRUDs públicos removidos) e sincronizado em `xano/`.
2. Código Reflex nesta branch → `pytest` → validação no navegador → PR.
- **Rollback:** reverter o commit do Reflex; no Xano, os endpoints públicos podem ser recriados a partir do histórico do Git.
