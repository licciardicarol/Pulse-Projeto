# Proposal: Sugestões geradas por IA

## Objetivo
Permitir que o usuário do Pulse receba sugestões geradas por IA a partir
dos próprios dados registrados (treinos, sono e refeições), atendendo à
funcionalidade "Sugestões e insights automáticos" já prevista na seção
"Evolução e análise" do `project-overview.md`.

## Escopo
Inclui:
- Serviço de backend que busca os registros recentes do Perfil e monta um
  prompt estruturado
- Integração com a API do Google Gemini (modelo Flash) para gerar o texto
  da sugestão
- Persistência da sugestão gerada, associada ao Perfil
- Exibição da sugestão na interface, com aviso de que não substitui
  orientação profissional

Não inclui (fora de escopo desta proposta):
- Análise de IA embutida diretamente nos registros de Treino e Refeição
  (`analise_ia`) — já modelada no domain model, mas é uma capability
  separada
- Qualquer tipo de diagnóstico, prescrição ou recomendação médica/nutricional
- Fine-tuning ou treinamento de modelo próprio

## What Changes
- Nova entidade `Sugestao` associada ao Perfil (histórico de sugestões geradas)
- Novo serviço de backend (`services/ai_suggestions.py`) responsável por
  buscar dados, montar prompt e chamar a API do Gemini
- Novo State (`SugestaoState`) e componente de UI para exibir a sugestão
- **BREAKING**: nenhuma (funcionalidade aditiva)

## Impact
- Affected specs: nova capability `sugestoes`
- Affected code: `projetofacul/services/ai_suggestions.py`,
  `projetofacul/states/sugestao_state.py`, componente novo em `pages/`
- Affected data: nova tabela `Sugestao` no Xano (ver `spec.md` para o
  schema SQL proposto)
- Dependência externa nova: API do Google Gemini (chave em variável de
  ambiente — ver AGENTS.md, seção "Chaves de API / segredos"). Integração
  ainda não implementada; esta proposta cobre o desenho, não o código final.