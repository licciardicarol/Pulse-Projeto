## Objetivo

Permitir que o usuário autenticado registre suas sessões de treino (data, duração, nome, categoria, intensidade e observações), veja o histórico dos próprios treinos e exclua registros, com cada usuário acessando apenas os próprios dados.

## Why

A rota `/treinos` hoje é só um placeholder. A tabela `Treinos` do Xano já tem os campos da tela e o dono (`user_id`), mas os CRUDs de treino não filtram pelo dono: qualquer pessoa lista, altera ou apaga os treinos de todos. Com a sessão, a navbar e o padrão de RLS prontos (`completar-perfil-onboarding`, `registrar-refeicoes`), dá para ligar os treinos ao usuário com privacidade.

## Escopo

**Incluído**
- Xano: usar os campos que já existem no servidor em `Treinos` — `user_id` → `user`, `nome`, `duracao_minutos`, `categoria` (texto livre), `intensidade` (texto livre) e `observacoes` — sem criar campos; apenas o índice em `user_id` é adicionado. O enum legado `tipo` não é usado. Criação dos endpoints autenticados `GET/POST treinos/me` e `DELETE treinos/me/{treino_id}`; remoção dos 5 CRUDs públicos de treino.
- Página `/treinos` (rota privada) com cabeçalho, botão "+ Novo treino", lista (mais recentes primeiro) e estados vazio, carregando e erro.
- Modal "Novo treino" (Data, Duração, Nome, Categoria, Intensidade, Observações) com validação, salvar com toast.
- Exclusão com confirmação e toast.
- "Hoje" calculado no fuso America/Sao_Paulo (padrão da data, bloqueio de data futura).
- Delta do `domain-model.md` para a entidade Treino (já aplicado) e marcação de `Exercicio` como planejada.

**Fora do escopo**
- Edição de treino, filtros, paginação, gráficos, métricas.
- Cadastro de exercícios dentro do treino (tabela `Exercicio` não existe no Xano).
- Uso de `tipo`, `inicio`, `fim`, `carga` e `repeticoes` (campos legados mantidos sem alteração).
- Item "Social" na navbar (já ausente).

## What Changes

- **BREAKING** (Xano): removidos `GET/POST treino` e `GET/PATCH/DELETE treino/{treino_id}` públicos.
- Xano: índice em `Treinos.user_id`; obrigatoriedade e limites garantidos nos inputs do endpoint de criação (no banco os campos são opcionais).
- Novos módulos Reflex: `logic/treinos.py` (validação, data de hoje em SP, ordenação, formatação), `states/treinos_state.py`, `pages/treinos_page.py`; o cliente Xano ganha `list_treinos`, `create_treino`, `delete_treino`.
- `/treinos` sai das páginas placeholder.
- Subtítulo da página: "Registre suas sessões de treino e acompanhe seu histórico." (exercícios fora do MVP).

## Capabilities

### New Capabilities
- `registro-treinos`: registro, listagem e exclusão das sessões de treino do usuário autenticado, com privacidade por usuário.

### Modified Capabilities
- `navegacao-autenticada`: `/treinos` deixa de ser placeholder.

## Impact

- **Xano**: `xano/table/treinos.xs`; `xano/api/lunas_workspace/treinos/me_GET.xs`, `me_POST.xs`, `me/treino_id_DELETE.xs`; CRUDs públicos `treino*` removidos. Os endpoints são criados no site do Xano e sincronizados por pull (o push de endpoints pelo CLI falha).
- **Reflex**: `projetofacul/logic/treinos.py`, `projetofacul/states/treinos_state.py`, `projetofacul/pages/treinos_page.py`, `projetofacul/services/xano_client.py`, `projetofacul/projetofacul.py`, `projetofacul/pages/placeholder_page.py`.
- **Dependências**: nenhuma nova.
- **Testes**: lógica de treinos, State com Xano simulado, página e rotas; validação ponta a ponta no navegador e RLS com duas contas.
- **Docs**: `docs/domain-model.md` (Treino, Exercício, relacionamentos e regras).
