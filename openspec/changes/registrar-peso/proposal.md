## Objetivo

Permitir que o usuário autenticado registre o próprio peso corporal (data, horário e peso), veja um resumo (peso atual e variação desde o primeiro registro) e o histórico, e exclua registros — sem inventar valores e com cada usuário acessando apenas os próprios dados.

## Why

A rota `/peso` é hoje só um placeholder. A tabela `Registro_Peso` do Xano não tem dono e seus 5 CRUDs são públicos: qualquer pessoa, sem login, lista ou apaga os pesos de todos. Com sessão, Perfil e Refeições prontos, dá para ligar o peso ao usuário com privacidade, no mesmo padrão de Refeições.

## Escopo

**Incluído**
- Xano (feito pela usuária no site, depois sincronizado com `xano workspace pull`): `Registro_Peso` ganha `user_id` → `user` (+ índice); campos renomeados para `peso` e `data_horario`; endpoints autenticados `GET/POST registro_peso/me` e `DELETE registro_peso/me/{registro_peso_id}`; remoção dos 5 CRUDs públicos.
- Página `/peso` (rota privada) com cabeçalho, card do formulário (Data, Horário, Peso), 3 cartões de resumo ("Peso atual", "Desde o 1º registro", "Falta para a meta" = "—"), lista mais recente primeiro, estados vazio/carregando/erro.
- Exclusão com confirmação e toasts.
- Delta do `docs/domain-model.md` para a entidade de peso.

**Fora do escopo**
- IA/Gemini e cálculo de "falta para a meta" (só `# TODO: integração futura com IA (falta para a meta)`); não existe peso-alvo no schema — a integração futura vai exigir um campo como `peso_meta` (decimal).
- Medidas corporais: não existe tabela; um delta futuro do `domain-model.md` precisa criar `MedidaCorporal` (dono, `peso_id` opcional, cintura/quadril/peito/braço/coxa/panturrilha em cm, `data`).
- Gráficos (ficam em Relatórios), edição, filtros, paginação, campo `observacoes`.

## What Changes

- **BREAKING** (Xano): removidos `GET/POST registro_peso` e `GET/PATCH/DELETE registro_peso/{registro_peso_id}` públicos.
- **BREAKING** (Xano): campos `Peso` → `peso` e `Data_Horario` → `data_horario`. Registros antigos não têm dono e nunca aparecem para nenhum usuário.
- Novos módulos Reflex: lógica pura de peso (validação, conversão de fuso, peso atual, variação), `PesoState`, página de Peso; cliente Xano ganha `list_registros_peso`, `create_registro_peso`, `delete_registro_peso`.

## Capabilities

### New Capabilities
- `registro-peso`: registro, listagem, resumo e exclusão dos registros de peso do usuário autenticado, com privacidade por usuário e sem valores inventados.

### Modified Capabilities
- `navegacao-autenticada`: `/peso` deixa de ser placeholder.

## Impact

- **Xano**: `xano/table/registro_peso.xs`, `xano/api/lunas_workspace/registro_peso/me_GET.xs`, `me_POST.xs`, `me/registro_peso_id_DELETE.xs`; CRUDs públicos removidos.
- **Reflex**: `projetofacul/logic/peso.py`, `projetofacul/states/peso_state.py`, `projetofacul/pages/peso_page.py`, `projetofacul/services/xano_client.py`, `projetofacul/projetofacul.py`, `projetofacul/pages/placeholder_page.py` (sai `/peso`).
- **Dependências**: nenhuma nova (fuso fixo UTC−03:00 com a biblioteca padrão).
- **Testes**: lógica de peso, State com Xano simulado, página/rotas; validação no navegador.
- **Docs**: `docs/domain-model.md` (RegistroDePeso).
