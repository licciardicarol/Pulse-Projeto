## Objetivo

Transformar a tela **Início** (`/inicio`) no lugar onde o usuário descobre **como treinar hoje**. Um card **"Recomendação de hoje"** junta o que ele registrou (sono, refeições, treinos e perfil) e a IA (Google Gemini) sugere a intensidade do treino do dia (**Leve, Moderado ou Intenso**), uma nota de **recuperação de 0 a 100**, uma explicação curta e um resumo de como a **alimentação** pesou na decisão.

## Why

Hoje `/inicio` é só um aviso "Seu resumo do dia vai aparecer aqui.", embora seja a primeira tela depois do login. Os dados que respondem "posso treinar forte hoje?" já existem no Pulse: sono com duração e qualidade, refeições com calorias e macros estimados por IA, treinos com duração e intensidade, e perfil com objetivo e nível físico. Mas eles estão espalhados em telas separadas e o usuário precisa cruzá-los sozinho. A integração com o Gemini já existe (change `analisar-refeicoes-ia`), então dá para entregar a recomendação reaproveitando a mesma base.

## Escopo

**Incluído**
- Card **"Recomendação de hoje"** em `/inicio`, conforme o desenho da usuária:
  - manchete e parágrafo curto;
  - três caixas: **Recuperação** (nn/100), **Treino sugerido** (Leve/Moderado/Intenso + motivo) e **Alimentação**. A caixa "Massa magra" do desenho foi trocada por "Alimentação" (decisão da usuária em 2026-11-12), para não comentar composição corporal sem medição.
- A IA decide a intensidade a partir dos registros. Os exemplos da usuária servem de **orientação**, não de regra fixa, e a última palavra é da IA:
  - **Leve:** noite de sono muito ruim, alimentação ruim e treino ruim no dia anterior.
  - **Moderado:** sono bom, mas alimentação fraca e treino anterior com pouco rendimento.
  - **Intenso:** ótima noite de sono, boa alimentação e treino leve no dia anterior.
- **Geração automática 1 vez por dia** na primeira visita ao Início, mais um botão **"Atualizar"** para gerar de novo (por exemplo, depois de registrar o sono). Decisão da usuária em 2026-11-12.
- **Guardar no Xano** cada recomendação gerada, numa tabela nova `recomendacoes`. A recomendação do dia aparece igual em qualquer aparelho e fica um histórico. Decisão da usuária em 2026-11-12.
- **Sem registros recentes** (nenhum sono, refeição ou treino nos últimos 7 dias): mensagem fixa, **sem chamar a IA**, com atalhos para Sono, Refeições e Treinos. Decisão da usuária em 2026-11-12.
- Aviso fixo de que a recomendação é **gerada por IA** e **não substitui** a orientação de um profissional de saúde ou de educação física.
- Gravação protegida pelo token do usuário mais a mesma chave de serviço da análise de refeições: só o backend do Pulse grava recomendações.

**Fora do escopo**
- Tela de histórico de recomendações. O histórico só fica guardado no Xano.
- Plano de treino detalhado (exercícios, séries, cargas), dieta ou qualquer prescrição médica ou nutricional.
- Comentários sobre massa magra, gordura corporal ou outras medidas do corpo.
- Outros conteúdos do Início (atalhos, metas da semana, gráficos).
- Notificações ou geração em horário agendado. A geração só acontece quando o usuário abre o Início.

## What Changes

- `/inicio` deixa de ser placeholder e passa a mostrar o card "Recomendação de hoje" e seus estados: preparando, pronta, sem registros e erro.
- Novo módulo de lógica pura para:
  - montar o resumo dos registros recentes enviado à IA;
  - decidir se há registros suficientes;
  - validar a resposta da IA (faixas, intensidade permitida, tamanhos);
  - preparar os dados de exibição.
- O cliente do Gemini ganha uma função genérica de geração em JSON estruturado. A análise de refeições passa a usá-la, sem mudar o comportamento dela.
- Nova tabela `recomendacoes` no Xano e dois endpoints: buscar a recomendação de hoje e salvar uma nova (token + chave de serviço).
- Novo `InicioState`, que carrega a recomendação do dia, gera em segundo plano quando ainda não existe e atende ao botão "Atualizar".
- **Relação com `sugestoes`:**
  - **O que muda:** esta change entrega a primeira sugestão por IA do Pulse e segue as regras da capability `sugestoes`: não chamar a IA sem dados, não enviar dados inventados, isolar os dados por usuário, guardar o resultado e mostrar o aviso de IA.
  - **O que fica para outra change:** a spec `openspec/specs/sugestoes/spec.md` não segue o formato do OpenSpec (falha no `openspec validate`) e descreve um esquema que o Xano não usa (`profile_id` UUID, tabela `sugestao`). Por isso esta change cria uma capability própria em vez de alterar aquela, e corrigir ou remover `sugestoes` fica para uma change de limpeza.
  - **Change antiga:** a change aberta `sugestoes-ia`, que tem só proposta e tarefas, é substituída por esta. Cabe ao time fechá-la.

## Capabilities

### New Capabilities
- `recomendacao-do-dia`: recomendação diária de intensidade de treino gerada por IA na tela Início. Cobre:
  - quando é gerada e quando é reaproveitada;
  - quais dados vão para a IA;
  - formato e validação da resposta;
  - gravação protegida no Xano;
  - estados do card;
  - falhas;
  - avisos de conteúdo gerado por IA.

### Modified Capabilities
- `navegacao-autenticada`: o requisito "Páginas placeholder" é removido e substituído por "Rotas privadas sem área em construção", porque `/inicio`, a última área em construção, passa a seguir `recomendacao-do-dia`.

## Impact

- **Reflex:**
  - novos `projetofacul/logic/recomendacao.py`, `projetofacul/states/inicio_state.py` e `projetofacul/pages/inicio_page.py`;
  - alterados `projetofacul/services/gemini_client.py` (geração genérica), `projetofacul/services/xano_client.py` (buscar e salvar recomendação), `projetofacul/projetofacul.py` (rota `/inicio` com `on_load` próprio) e `projetofacul/pages/placeholder_page.py` (sem áreas em construção).
- **Xano:**
  - nova tabela `recomendacoes` e endpoints `GET recomendacoes/me/hoje` e `POST recomendacoes/me`;
  - reaproveita a variável de ambiente `PULSE_ANALISE_SECRET`, sem configuração nova;
  - a tabela e os endpoints precisam ser criados no site do Xano e depois baixados com `xano workspace pull`, porque o `push` da CLI falha ao criar endpoints novos;
  - abrir o Início faz 1 chamada ao Xano quando a recomendação do dia já existe e até 5 quando precisa gerar uma nova, dentro do limite de 10 requisições a cada 20 s.
- **Google Gemini:**
  - uma chamada por recomendação gerada (primeira visita do dia ou "Atualizar");
  - vão só dados estruturados dos registros (números, datas, nomes de treino, objetivo e nível do perfil, idade em anos);
  - não vão nome, e-mail, descrições de refeições nem observações livres;
  - no plano gratuito, o Google pode usar esse conteúdo.
- **Configuração e dependências:** nenhuma variável nova e nenhuma biblioteca nova. Usa `GEMINI_API_KEY`, `GEMINI_MODEL`, `PULSE_ANALISE_SECRET` e `httpx`, que já existem.
- **OpenSpec:** esta change precisa ser arquivada depois de `registro-sono`, `registrar-treinos`, `registrar-peso` e `relatorios`, que também reescrevem "Páginas placeholder".
- **Testes:** lógica de contexto e validação, cliente do Gemini, cliente do Xano, `InicioState` com Xano e Gemini simulados, página e rotas.
