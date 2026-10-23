## Objetivo

Permitir que o usuário autenticado registre o que comeu (data, tipo e descrição em texto), veja o histórico das próprias refeições e os totais nutricionais do dia, e exclua registros — sem inventar valores nutricionais enquanto a análise por IA não existe.

## Why

A rota `/refeicoes` é hoje só um placeholder. A tabela `Refeicoes` não tinha dono, os macros eram texto e os CRUDs eram públicos (qualquer pessoa listava ou apagava refeições de todos). Com a sessão e o Perfil prontos (`completar-perfil-onboarding`), dá para ligar a alimentação ao usuário com privacidade e preparar o terreno para a análise por IA (capability futura `sugestoes`).

## Escopo

**Incluído**
- Xano (já aplicado e testado): `Refeicoes` com `user_id` → `user` (+ índice), `descricao` (texto), `gorduras` e `analise_ia`, macros `proteinas`/`carboidratos` migrados de texto para decimal; endpoints autenticados `GET/POST refeicoes/me` e `DELETE refeicoes/me/{refeicao_id}`; remoção dos 5 CRUDs públicos.
- Página `/refeicoes` (rota privada) com cabeçalho, botão "+ Nova refeição", 4 cards de totais do dia, nota de refeições aguardando análise, lista (mais recentes primeiro), estados vazio/carregando/erro.
- Modal "Nova refeição" (Data, Tipo, Descrição) com validação, salvar com toast e um ponto de extensão `# TODO: integração futura com IA`.
- Exclusão com confirmação e toast.
- Cor de destaque dos componentes Radix trocada para o azul do projeto (`#2B8CFF`) em todo o app.
- Delta do `domain-model.md` para a entidade Refeição.
- Mitigação do limite do Xano (10 requisições a cada 20 s): confirmação da sessão reaproveitada por 60 s, mensagem própria para o erro 429 e botão "Tentar novamente" na tela de erro da sessão.

**Fora do escopo**
- Chamada ao Gemini, cálculo ou estimativa de calorias/macros, serviço ou função "fake" de análise.
- Edição de refeição, filtros, paginação.
- Item "Social" na navbar (já ausente).

## What Changes

- **BREAKING** (Xano): removidos `GET/POST refeicoes` e `GET/PATCH/DELETE refeicoes/{refeicoes_id}` públicos.
- **BREAKING** (Xano): `proteinas` e `carboidratos` passam de texto para decimal (tabela estava vazia; sem migração de dados).
- Novos módulos Reflex: lógica pura de refeições (validação, tipo sugerido pelo horário, ordenação, totais do dia), `RefeicoesState`, página de Refeições; cliente Xano ganha `list_refeicoes`, `create_refeicao`, `delete_refeicao`.
- `rx.App` passa a usar tema com destaque azul.

## Capabilities

### New Capabilities
- `registro-refeicoes`: registro, listagem, totais do dia e exclusão das refeições do usuário autenticado, com privacidade por usuário e sem valores nutricionais inventados.

### Modified Capabilities
- `navegacao-autenticada`: novo requisito de reaproveitamento da sessão e tratamento do limite de requisições do Xano.

## Impact

- **Xano**: `xano/table/refeicoes.xs`, `xano/api/lunas_workspace/refeicoes/me_GET.xs`, `me_POST.xs`, `me/refeicao_id_DELETE.xs`; CRUDs públicos removidos.
- **Reflex**: `projetofacul/logic/refeicoes.py`, `projetofacul/states/refeicoes_state.py`, `projetofacul/pages/refeicoes_page.py`, `projetofacul/services/xano_client.py`, `projetofacul/projetofacul.py`, `projetofacul/pages/placeholder_page.py` (sai `/refeicoes`).
- **Dependências**: nenhuma nova.
- **Testes**: lógica de refeições, State com Xano simulado, página/rotas; validação ponta a ponta no navegador.
- **Docs**: `docs/domain-model.md` (Refeição).
