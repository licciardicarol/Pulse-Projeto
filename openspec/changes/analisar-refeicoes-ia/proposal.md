## Objetivo

Fazer a IA (Google Gemini) analisar cada refeição registrada em `/refeicoes` e estimar **calorias, proteínas, carboidratos e gorduras** a partir da descrição em texto. Com isso, os 4 cards do topo da tela (**CALORIAS HOJE, PROTEÍNAS, CARBOIDRATOS e GORDURAS**) passam a mostrar os totais do dia, e cada refeição da lista mostra seus valores e um resumo curto do que a IA identificou.

## Why

Hoje toda refeição fica para sempre "Aguardando análise" e os 4 cards mostram sempre 0: a spec `registro-refeicoes` proíbe estimar valores porque a IA ainda não existia, e o subtítulo da página promete "Em breve a IA estimará calorias e macronutrientes automaticamente". O usuário só descreve o que comeu ("2 ovos, pão integral e café"); sem a estimativa, o registro não vira informação útil, e o card de calorias da tela Relatórios também fica vazio. A tabela `refeicoes` do Xano já tem `calorias`, `proteinas`, `carboidratos`, `gorduras` e `analise_ia`; falta só quem os preencha.

## Escopo

**Incluído**
- Análise **logo ao salvar** (decisão da usuária em 2026-11-10): o modal fecha como hoje, a refeição aparece com "Analisando…" e, quando a IA responde, a refeição e os 4 cards se atualizam sozinhos.
- Botão **"Analisar"** em cada refeição ainda sem análise (falha da IA, IA indisponível ou refeições registradas antes desta change), para tentar de novo.
- Selo **"Estimado por IA"** e **resumo curto** da IA em cada refeição analisada (ex.: "2 ovos (~140 kcal), 1 fatia de pão integral (~70 kcal), café sem açúcar").
- Aviso fixo na tela de que os valores são **estimativas geradas por IA** e **não substituem a orientação de um nutricionista**.
- Descrições sem alimentos reconhecíveis ("asdf", "nada") não recebem números: a refeição continua sem análise e mostra o motivo.
- Endpoint novo no Xano para gravar a análise, aceito só com o **token do usuário + uma chave secreta de serviço** que apenas o backend do Pulse conhece (decisão da usuária em 2026-11-10).
- Chamada ao Gemini só no backend (State do Reflex), com a chave em variável de ambiente.

**Fora do escopo**
- Editar manualmente calorias ou macros de uma refeição.
- Analisar refeições antigas em lote ou automaticamente ao abrir a tela (cada uma é analisada pelo botão "Analisar", para não estourar limites de requisição).
- Fotos de refeições, código de barras, tabela nutricional própria.
- Calorias gastas nos treinos e sugestões de dieta (change `sugestoes-ia`).
- Qualquer recomendação nutricional ou médica: a IA só estima valores.

## What Changes

- **BREAKING (spec)**: o requisito "Nenhum valor nutricional inventado" de `registro-refeicoes` é substituído. Valores nutricionais deixam de ser proibidos e passam a vir **somente** da análise por IA, gravada pelo backend do Pulse por um endpoint protegido. O endpoint de criação continua aceitando apenas data, tipo e descrição.
- Novo serviço de backend que monta o pedido ao Gemini (só tipo + descrição da refeição, nada que identifique o usuário), pede resposta em JSON estruturado e valida o resultado antes de gravar.
- Nova lógica pura para montar o pedido e validar/normalizar a resposta (faixas plausíveis, arredondamento, resumo).
- Novo endpoint no Xano `PATCH refeicoes/me/{refeicao_id}/analise` (dono pelo token + chave secreta de serviço).
- `RefeicoesState` passa a disparar a análise depois de salvar, controlar quais refeições estão "Analisando…" e expor o botão "Analisar".
- Página de Refeições: novo subtítulo, aviso de IA junto aos totais, selo "Estimado por IA", resumo, estados "Analisando…" e "Analisar".

## Capabilities

### New Capabilities
- `analise-refeicoes-ia`: estimativa nutricional por IA de cada refeição: quando acontece, quais dados vão para a IA, formato e validação da resposta, gravação protegida no Xano, tratamento de falhas e avisos de que o conteúdo é gerado por IA.

### Modified Capabilities
- `registro-refeicoes`: o requisito "Nenhum valor nutricional inventado" passa a permitir valores vindos só da análise por IA; "Página de Refeições" troca o subtítulo; "Totais do dia" ganha o aviso de IA; "Lista de refeições" ganha selo, resumo, "Analisando…" e "Analisar"; "Registrar refeição pelo modal" passa a iniciar a análise após salvar.

## Impact

- **Reflex**: novos `projetofacul/logic/analise_refeicao.py` e `projetofacul/services/gemini_client.py`; alterados `projetofacul/services/xano_client.py` (gravar análise), `projetofacul/states/refeicoes_state.py`, `projetofacul/pages/refeicoes_page.py` e `projetofacul/logic/refeicoes.py` (dados de exibição).
- **Xano**: novo endpoint `xano/api/lunas_workspace/refeicoes/me/refeicao_id/analise_PATCH.xs` e variável de ambiente `PULSE_ANALISE_SECRET` no workspace. Sem mudança de tabela. Cada registro passa a fazer 3 chamadas ao Xano (criar, gravar análise, listar), dentro do limite de 10 requisições / 20 s do plano gratuito.
- **Google Gemini**: dependência externa nova (API REST `generateContent`). Requer `GEMINI_API_KEY` no `.env` (fora do Git); modelo configurável em `GEMINI_MODEL`, padrão `gemini-3.5-flash-lite` (estável e mais barato segundo a documentação do Google em 2026-11-10).
- **Configuração**: `.env.example` ganha `GEMINI_API_KEY`, `GEMINI_MODEL` e `PULSE_ANALISE_SECRET` (só os nomes, sem valores). Sem chave configurada, a tela funciona e as refeições ficam "Aguardando análise".
- **Dependências**: nenhuma biblioteca nova; a chamada usa `httpx`, que já vem com o Reflex e já é usado no cliente do Xano.
- **Relatórios**: o card de calorias da change `relatorios` passa a ter dados assim que houver refeições analisadas, sem alteração de código.
- **Testes**: lógica de pedido/validação, cliente do Gemini com HTTP simulado, State com Xano e Gemini simulados, página e cliente do Xano.
