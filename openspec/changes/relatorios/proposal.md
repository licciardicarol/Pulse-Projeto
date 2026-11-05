## Objetivo

Entregar a tela **Relatórios** (`/relatorios`) para o usuário autenticado acompanhar a própria evolução em gráficos calculados a partir dos registros que ele já faz no Pulse: frequência de treinos, horas de sono, evolução do peso e calorias ingeridas. Cada relatório pode ser visto em colunas ou em linhas, à escolha do usuário.

## Why

A rota `/relatorios` ainda é um placeholder "em construção". Com Treinos, Sono, Peso e Refeições já registrando dados por usuário no Xano, falta a visão de evolução no tempo, que é a proposta central do Pulse ("Evolução visível" na landing page). Os quatro registros já existem na branch de trabalho; nenhum dado novo precisa ser coletado.

## Escopo

**Incluído**
- Página `/relatorios` (rota privada) com cabeçalho e 4 cards, nesta ordem:
  1. **Frequência de treinos (últimas 8 semanas)**: quantidade de treinos por semana.
  2. **Horas de sono (últimos 30 registros)**: horas dormidas em cada noite registrada.
  3. **Evolução do peso**: peso de cada registro, em ordem cronológica.
  4. **Calorias ingeridas x gastas (últimos 14 dias)**: total diário de calorias das refeições já analisadas.
- Em cada card, seletor de tipo de gráfico com **Colunas** e **Linhas**. A escolha é lembrada **no navegador** (por relatório), sem alteração no Xano.
- Estado vazio "Ainda não há dados suficientes." quando o relatório não tem dados para desenhar; estados de carregamento e erro com "Tentar novamente".
- Card de calorias "aguardando a IA": mostra as calorias ingeridas assim que as refeições tiverem calorias estimadas e informa que as calorias gastas dependem da estimativa por IA dos treinos.
- Tabela acessível com os mesmos dados de cada gráfico (para leitores de tela) e tooltip ao passar o mouse.
- Cálculos em lógica pura (`logic/relatorios.py`) com testes unitários.

**Fora do escopo**
- Gráficos de Pizza e Rosca (descartados em 2026-11-04: servem para partes de um todo, não para evolução no tempo).
- Calorias gastas: a tabela `treinos` não tem campo de calorias; a estimativa por IA dos treinos e das refeições pertence à change `sugestoes-ia`.
- Salvar a preferência de gráfico na conta (Xano), filtros de período, exportação, comparação entre usuários.
- Qualquer alteração de schema ou endpoint no Xano.

## What Changes

- Nova página de Relatórios com 4 gráficos de série única (barras ou linha), usando os componentes Recharts que já vêm com o Reflex.
- Novo `RelatoriosState`: carrega as listas de treinos, sono, peso e refeições do usuário autenticado (endpoints `*/me` já existentes) e guarda o tipo de gráfico de cada relatório em `rx.LocalStorage`.
- Nova lógica pura de séries dos relatórios (agrupamento por semana e por dia no fuso de Brasília, ordem cronológica, critérios de "dados suficientes").
- `/relatorios` deixa de ser placeholder; sobra apenas `/inicio` como área em construção.

## Capabilities

### New Capabilities
- `relatorios`: tela de relatórios do usuário autenticado: quais relatórios existem, como cada série é calculada a partir dos registros, escolha e memória do tipo de gráfico, estados vazio/carregando/erro, privacidade e acessibilidade.

### Modified Capabilities
- `navegacao-autenticada`: `/relatorios` deixa de ser placeholder e passa a seguir a capability `relatorios`.

## Impact

- **Reflex**: novos `projetofacul/logic/relatorios.py`, `projetofacul/states/relatorios_state.py`, `projetofacul/pages/relatorios_page.py`; alterados `projetofacul/projetofacul.py` (rota com `on_load`) e `projetofacul/pages/placeholder_page.py` (sai `/relatorios`).
- **Xano**: nenhuma mudança; usa `GET treinos/me`, `GET sono/me`, `GET registro_peso/me` e `GET refeicoes/me`. São 4 leituras por abertura da tela, dentro do limite de 10 requisições / 20 s do plano gratuito.
- **Dependências**: nenhuma nova biblioteca Python. Os gráficos usam `rx.recharts`, que já vem com o Reflex; o pacote `recharts` do front-end passa a ser instalado pelo próprio Reflex na compilação (atualiza `reflex.lock/`).
- **Ordem de arquivamento**: depende de `registrar-treinos`, `registro-sono` e `registrar-peso`, que também alteram o requisito "Páginas placeholder"; arquivar esta change depois delas.
- **Testes**: lógica das séries, State com Xano simulado, página e rotas.
