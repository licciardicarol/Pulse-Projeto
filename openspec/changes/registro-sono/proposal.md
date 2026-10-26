## Why

A rota `/sono` hoje é só um placeholder "em construção". Sem registros de sono confiáveis, as futuras recomendações de recuperação e de intensidade de treino (capability `sugestoes`) e os Relatórios não têm dados de descanso para usar. Além disso, a tabela `Sono` do Xano não tem dono (`user_id`), observações nem duração, e os endpoints atuais (`sono`, `sono/{id}`) são CRUDs públicos sem isolamento por usuário.

## Objetivo

Entregar a tela **Sono** (`/sono`) para o usuário autenticado registrar, listar, editar e excluir as próprias noites de sono (início, fim, qualidade 1–5 e observações), com duração calculada automaticamente e validações que garantem dados consistentes para recomendações e relatórios.

## Escopo

**Dentro:**
- Tela `/sono` dentro do `app_shell` (navbar com item Sono ativo), no mesmo padrão visual e de código da tela de **Refeições**, que é a referência principal.
- Reuso do CSS e dos helpers de feedback de Refeições por import, sem alterar nenhum arquivo de Refeições.
- Formulário em card com Início do sono, Fim do sono (`datetime-local`), Qualidade (5 chips de seleção única com estrela) e Observações (até 500 caracteres).
- Data e hora livres (campos vazios ao abrir), calendário com hora ao clicar e horário de Brasília fixo, com o dia virando às 00:00.
- Duração calculada em tempo real ("8h", "7h 30min", "45min" ou "—").
- Validações: fim posterior ao início, duração entre 15 min e 24 h, fim não futuro, qualidade obrigatória e sem sobreposição com outros registros do mesmo usuário.
- Lista do mais recente para o mais antigo, com editar (reaproveita o formulário) e excluir (com confirmação), mais os estados vazio, carregando e erro.
- Backend Xano: ajuste da tabela `Sono` e novos endpoints autenticados `sono/me` (GET/POST) e `sono/me/{sono_id}` (PATCH/DELETE), no padrão de `refeicoes/me`.
- Função pura de resumo das últimas noites (duração e qualidade), para uso futuro por recomendações e Relatórios.

**Fora:**
- Wearables, fases do sono e as regras internas de recomendação de treino.
- Campo `tipo_sono` (Principal/Soneca) do `domain-model.md`: fica para uma change futura. A regra de não sobreposição já permite sonecas em horários distintos.
- Tela de Relatórios e a integração com o Gemini: apenas consomem o resumo depois.
- Picker de data/hora customizado: o calendário é o nativo do navegador.

## What Changes

- **BREAKING (Xano)**: `Sono.qualidade_sono` deixa de ser enum de textos ("Muito ruim" … "Muito bom") e passa a ser inteiro de 1 a 5. Os rótulos ficam no app: Muito ruim, Ruim, Regular, Bom, Muito bom.
- Tabela `Sono` ganha `user_id`, `duracao_minutos`, `observacoes` e `updated_at`, além de índice por `user_id`.
- Novos endpoints autenticados `sono/me` e `sono/me/{sono_id}`. Os CRUDs públicos antigos (`sono`, `sono/{sono_id}`) são removidos.
- Novo `SonoState`, novo módulo de lógica `logic/sono_registro.py` (validação, duração, sobreposição, formatação e resumo) e novas funções no `xano_client`.
- Nova página `pages/sono_page.py`. `/sono` deixa de usar a página placeholder.

## Capabilities

### New Capabilities
- `registro-sono`: registro, listagem, edição e exclusão de noites de sono do usuário autenticado, com duração calculada, validações e resumo para recomendações e relatórios.

### Modified Capabilities
- `navegacao-autenticada`: `/sono` sai da lista de páginas placeholder.

## Impact

- **Código**: `projetofacul/pages/sono_page.py` (novo, usa `REFEICOES_PAGE_CSS`), `projetofacul/states/sono_state.py` (novo), `projetofacul/logic/sono_registro.py` (novo), `projetofacul/services/xano_client.py`, `projetofacul/pages/placeholder_page.py` (remove `/sono`), `projetofacul/projetofacul.py` (rota), `docs/domain-model.md` (Sono por `user_id` e qualidade 1–5).
- **Xano**: `xano/table/sono.xs` alterado; `xano/api/lunas_workspace/sono/me_*.xs` e `sono/me/sono_id_*.xs` novos; `sono_GET/POST` e `sono/sono_id_*` removidos. Como o push de endpoints pelo CLI falha, a pessoa responsável cria/publica no site do Xano e sincroniza por pull antes do teste ponta a ponta.
- **Testes**: `tests/test_sono_registro.py`, `tests/test_sono_state.py`, `tests/test_sono_page.py`, além de ajustes em `tests/test_xano_client.py` e `tests/test_routes.py`. Nenhum arquivo de Refeições é alterado.
- **Dependências**: nenhuma nova biblioteca.
- **Base**: branch `feat/registro-sono`, a partir de `32ef17c` (já contém a tela de Refeições).
