## Context

Ver `proposal.md` (Why/Escopo) e `specs/relatorios/spec.md` (regras de cada série). Estado relevante na branch `feat/relatorios` (criada a partir de `feat/registrar-peso`, que já reúne Peso, Sono, Treinos e Refeições):

- O `xano_client` já tem `list_treinos`, `list_sono`, `list_registros_peso` e `list_refeicoes`, todos por token (`*/me`). Erros chegam como `XanoError(tipo)`, incluindo `limite_requisicoes` (HTTP 429), e `get_failure_message` traduz o limite.
- `SessaoState.ensure_session` reaproveita a confirmação da sessão por 60 s; as telas usam `on_load=[SessaoState.ensure_session, <State>.start_page]` e `start_page` sai cedo se `sessao_verificada` for falso.
- Já existem auxiliares puros por área: `logic/treinos.py` (`get_today_sao_paulo`), `logic/sono_registro.py` (`sort_sono`, `get_duration_minutes`, `from_utc_ms`), `logic/peso.py` (`FUSO_BRASILIA`, `get_timestamp`, `get_weight`, `from_milliseconds`) e `logic/refeicoes.py` (`is_analyzed`, `get_number`).
- O Xano devolve decimais vazios como `0`; em refeições, só `analise_ia` preenchido indica que a refeição foi analisada (`is_analyzed`).
- `rx.recharts` (Recharts) já vem com o Reflex 0.9.10 (`bar_chart`, `line_chart`, `x_axis`, `y_axis`, `cartesian_grid`, `graphing_tooltip`, `responsive_container`).
- Plano gratuito do Xano: 10 requisições a cada 20 s.

## Goals / Non-Goals

**Goals:**
- Séries calculadas por funções puras e testáveis, sem Reflex e sem rede, reaproveitando os auxiliares de cada área em vez de reimplementar datas, fuso e conversões.
- Um componente de card de relatório reutilizado pelos 4 relatórios (título, seletor, gráfico, tabela acessível, estados).
- Falha de uma fonte não derruba os outros cards.

**Non-Goals:**
- Cache das listas entre páginas ou atualização em tempo real.
- Segunda série no gráfico de calorias (gastas) e paleta categórica: ficam para a change da IA.

## Decisions

### D1. Lógica pura em `logic/relatorios.py`
Uma função por relatório, todas devolvendo `list[dict]` no formato `{"rotulo": "dd/mm", "valor": float | None, "texto": "…"}`, em ordem cronológica, mais uma função `has_enough_data(relatorio, pontos)`:
- `build_weekly_workouts(treinos, hoje)` → 8 semanas (segunda a domingo) terminando na semana de `hoje`; conta treinos por `data` (`DATE`, sem conversão de fuso) e descarta datas fora da janela ou futuras.
- `build_sleep_hours(registros, quantidade=30)` → `sort_sono` (mais recentes pelo início), pega 30, inverte para cronológico; horas = `get_duration_minutes / 60` com 1 casa; rótulo = data local do `fim_sono`, como em `summarize_recent_sleep`.
- `build_weight_evolution(registros)` → ordena por `get_timestamp` (e `created_at` no empate) crescente; descarta peso inválido; rótulo pela data local da pesagem.
- `build_daily_calories(refeicoes, hoje)` → 14 dias até `hoje`; soma `calorias` só de refeições com `is_analyzed`; dia sem refeição analisada recebe `valor=None`.
- `hoje` é sempre parâmetro (os States passam `get_today_sao_paulo()`), para os testes fixarem a data.
- `texto` já vem formatado no padrão brasileiro com unidade ("3 treinos", "7,5 h", "71,8 kg", "1.850 kcal", "—" para `None`); a UI só exibe.
- *Alternativa:* calcular no front com Var operations → descartada: lógica de negócio não testável e espalhada nos componentes.

### D2. `RelatoriosState` carrega as 4 listas e guarda pontos prontos
- `start_page` (on_load após o guarda) busca as 4 listas **em sequência** e grava, por relatório, `pontos_<relatorio>: list[dict]` e `erro_<relatorio>: str`. Uma falha só preenche o erro daquele card; `nao_autorizado` em qualquer leitura limpa a sessão e redireciona a `/login`.
- `carregando` cobre a tela inteira até as 4 leituras terminarem (sem gráficos parciais); "Tentar novamente" chama `start_page` de novo.
- *Alternativa:* `asyncio.gather` das 4 leituras → menos espera, mas dispara 4 requisições no mesmo instante, logo após as 2 do guarda; em sequência fica mais longe do limite de rajada do Xano. A diferença de tempo (4 leituras pequenas) é aceitável.
- *Alternativa:* um State por relatório → 4 on_load e 4 States para uma única tela; a convenção é um State por área funcional.

### D3. Preferência de gráfico em `rx.LocalStorage`
- Quatro vars `rx.LocalStorage` (`pulse_grafico_treinos`, `pulse_grafico_sono`, `pulse_grafico_peso`, `pulse_grafico_calorias`) com valores `"colunas"`/`"linhas"`; um evento `set_chart_type(relatorio, tipo)` valida o relatório e o tipo antes de gravar.
- O tipo efetivo é uma var computada por relatório que cai no padrão (requisito "Escolha do tipo de gráfico": colunas, exceto peso = linhas) quando o valor salvo é vazio ou inválido; `normalize_chart_type(valor, relatorio)` fica em `logic/relatorios.py` e é testada.
- *Alternativa:* salvar no Perfil do Xano → descartada pela usuária em 2026-11-04 (exigiria campo e endpoint novos).

### D4. Um card genérico com `rx.recharts`
`report_card(titulo, relatorio, pontos, tipo, unidade, nota=None)` monta: título (`h2`), seletor (`role="group"`, dois `button` com `aria-pressed`), e o corpo por `rx.cond` (carregando → spinner; erro → mensagem + "Tentar novamente"; sem dados → "Ainda não há dados suficientes."; senão → gráfico + tabela).
- Gráfico: `responsive_container` (altura fixa ~240px) com `bar_chart` **ou** `line_chart` via `rx.cond(tipo == "linhas", …)`; `data_key="valor"`, eixo X em `rotulo`.
- Marcas pela skill de visualização: série única na cor da marca `#2B8CFF` (validada: passa contraste ≥ 3:1 sobre `#111B2E` no modo escuro), barras finas com topo arredondado de 4px, linha de 2px com marcadores ≥ 8px, grade e eixos discretos (`text_muted`), sem legenda (série única; o título nomeia a série), tooltip ao passar o mouse com o `texto` formatado.
- Colunas sempre com eixo Y a partir de 0; em linhas, o peso usa domínio ajustado aos dados (`dataMin`/`dataMax` com folga), para a variação de poucos kg ser visível.
- `valor=None` vira lacuna (barra ausente; linha sem conectar o ponto), nunca 0.
- Tabela: `<table>` visualmente oculta (classe `sr-only`) com `rotulo` e `texto` de cada ponto, ligada ao card por `aria-describedby`.
- Animação do Recharts desligada em todas as séries (`is_animation_active=False`): ela é controlada por JavaScript, não por CSS, então `prefers-reduced-motion` não a alcança; desligar sempre é a forma simples de cumprir o requisito.
- *Alternativa:* gráficos em SVG/HTML próprios → mais controle, mas reimplementa eixos, escalas e tooltip; Recharts já vem no Reflex.

### D5. Layout e estilo
Mesmo `app_shell` das outras áreas, CSS em string com `apply_theme_tokens` (padrão de Perfil). Cards empilhados com 32px de espaço, largura máxima ~960px (gráficos precisam de largura), raio 20px, gradiente de superfície igual ao Perfil; seletor como "pílulas" compactas no canto superior direito do card, indo para baixo do título em ≤ 520px. Notas do card de calorias em `text_secondary`, com ícone de informação.

## Risks / Trade-offs

- [Muitas leituras ao abrir a tela (2 do guarda + 4 listas)] → guarda reaproveita a sessão por 60 s; leituras em sequência; 429 vira "Muitas ações em pouco tempo. Aguarde alguns segundos…" no card afetado.
- [Listas crescem sem paginação (todos os registros do usuário)] → aceitável no volume de um usuário; filtros/paginação ficam para quando houver endpoint de período.
- [Recharts ainda não instalado no front-end] → a primeira compilação instala `recharts` e altera `reflex.lock/`; commitar junto e citar no PR.
- [Peso em colunas a partir de 0 achata variações pequenas] → é a forma honesta para barras; o padrão do peso é Linhas, com domínio ajustado.
- [Sem animação nos gráficos para respeitar movimento reduzido] → perda estética pequena; o fade-in dos cards continua e é desligado por `prefers-reduced-motion`.
- [Change depende de `registrar-treinos`, `registro-sono` e `registrar-peso` ainda não arquivadas] → arquivar depois delas; o delta de `navegacao-autenticada` assume as três aplicadas.

## Migration Plan

Sem migração de dados nem mudança no Xano. Publicar o código Reflex; rollback = reverter o commit (a rota volta ao placeholder).
