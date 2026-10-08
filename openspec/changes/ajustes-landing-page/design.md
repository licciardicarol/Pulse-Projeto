## Context

A landing page pública usa estilos centralizados em `styles/theme.py` e componentes em `projetofacul/landing_page.py`. A alteração mantém a estrutura atual de rotas e não altera estados ou integração com serviços externos.

## Goals / Non-Goals

**Goals:**
- Expandir o cabeçalho para a largura total.
- Reutilizar o botão secundário em toda a landing page.
- Centralizar conteúdo e melhorar o alinhamento responsivo.
- Garantir o comportamento acessível do FAQ.

**Non-Goals:**
- Alterar regras de negócio, Xano, schema ou rotas.
- Instalar dependências.
- Alterar o conteúdo da proposta ou os dados exibidos.

## Decisions

- O cabeçalho usa um container de largura completa e mantém padding interno responsivo.
- O botão secundário permanece visualmente idêntico ao botão do hero por meio de CSS compartilhado.
- A responsividade usa CSS com breakpoints e tipografia fluida.
- O FAQ usa o accordion integrado ao Reflex, com uma resposta ativa por vez.

## Risks / Trade-offs

- [Estilo aplicado por CSS global] → Os seletores de classe são específicos à landing page para evitar efeitos em outras telas.
- [Acesso ao efeito de accordion depende da estrutura do Radix] → O estado e os atributos ARIA são fornecidos pelo componente do Reflex e os estilos são aplicados com seletores específicos.

## Migration Plan

A alteração é compatível com a versão atual e não exige migração de dados ou dependências. Para manter o rollback simples, o design foi limitado à camada visual e aos estilos da landing page.

## Open Questions

Nenhuma questão permanece aberta.
