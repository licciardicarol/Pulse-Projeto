# Tasks: Sugestões geradas por IA

Cada tarefa é dimensionada para caber em um bloco de até 2h.

## Back-end / dados (Python + SQL)

- [ ] 1.1 (30min) Criar migração SQL da tabela `sugestao` conforme `spec.md`
- [ ] 1.2 (30min) Atualizar `create-tables.sql` com a nova tabela e configurar RLS por `profile_id`
- [ ] 1.3 (1h30) Criar query/função de acesso a dados: buscar Treinos, Sonos e
      Refeições dos últimos 30 dias de um Perfil
- [ ] 1.4 (1h30) Criar função pura `montar_prompt(dados) -> str` que transforma
      os registros buscados em um prompt estruturado (sem chamar a API ainda)
- [ ] 1.5 (2h) Criar `services/ai_suggestions.py`: função que chama a API do
      Gemini com o prompt montado e retorna o texto da sugestão, com
      tratamento de erro/timeout/rate-limit
- [ ] 1.6 (1h) Criar função de persistência: salvar o resultado na tabela `sugestao`
- [ ] 1.7 (30min) Configurar variável de ambiente `GEMINI_API_KEY` (`.env`, fora do Git)

## Back-end / State (Reflex)

- [ ] 2.1 (1h) Criar `SugestaoState` com var `is_loading`, var `ultima_sugestao`
      e evento `gerar_sugestao`
- [ ] 2.2 (1h) Conectar o evento `gerar_sugestao` às funções de 1.3–1.6,
      incluindo o caso "sem dados suficientes" (não chama a API)
- [ ] 2.3 (1h) Adicionar var computada `historico_sugestoes` para listar
      sugestões anteriores do Perfil

## Front-end (componentes Reflex)

- [ ] 3.1 (1h) Criar componente `sugestao_card` exibindo o texto da sugestão
      e o aviso fixo de responsabilidade
- [ ] 3.2 (1h) Criar botão "gerar sugestão" com estado de loading
- [ ] 3.3 (1h) Criar estado vazio: mensagem quando não há dados suficientes
- [ ] 3.4 (1h30) Criar seção de histórico de sugestões (lista simples,
      ordenada por data)
- [ ] 3.5 (1h) Integrar a seção de sugestões à página de evolução existente

## Testes

- [ ] 4.1 (1h) Teste unitário: `montar_prompt` com dados mockados (cobre o
      requisito "nenhum dado inventado")
- [ ] 4.2 (1h) Teste unitário: chamada à API mockada retornando sucesso
- [ ] 4.3 (1h) Teste unitário: chamada à API mockada retornando erro/timeout
      (confirma que nenhum registro incompleto é salvo)
- [ ] 4.4 (1h) Teste de isolamento: usuário A não consegue ler sugestão de
      usuário B
- [ ] 4.5 (30min) Teste de UI: aviso de responsabilidade sempre presente
      junto à sugestão

## Validação

- [ ] 5.1 (30min) Rodar `pytest` e confirmar que todos os testes passam
- [ ] 5.2 (30min) Rodar `openspec validate` na proposta
- [ ] 5.3 (30min) Revisão do time antes de arquivar a change