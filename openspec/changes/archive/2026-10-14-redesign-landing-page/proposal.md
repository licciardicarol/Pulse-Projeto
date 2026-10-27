## Why

A landing page atual atende às rotas básicas, mas apresenta uma identidade visual genérica e não comunica de forma clara o valor do Pulse. O redesenho permite apresentar a proposta de valor, organizar as funcionalidades e criar uma experiência premium, responsiva e consistente com o restante do produto.

## What Changes

- Aplicar um redesign visual completo da home pública em dark mode azul-marinho.
- Centralizar cores, tipografia, espaçamentos e estados interativos em um arquivo de tema reutilizável.
- Adicionar navbar, hero, seções de funcionalidades, público-alvo, FAQ, CTA e rodapé.
- Implementar microinterações, foco acessível e atendimento ao modo de redução de movimento.
- Manter as rotas existentes e apenas criar placeholders para autenticação quando necessário.

## Capabilities

### New Capabilities
- `landing-page-visual`: apresentação visual e de conteúdo da home pública, incluindo design responsivo, acessibilidade e microinterações.

### Modified Capabilities
- Nenhuma. A mudança é restrita à camada visual e de composição da página.

## Impact

- Frontend Reflex: página inicial, estilos globais e componentes de navegação.
- Tokens de design: definição centralizada de cores, fontes, espaçamentos e estados.
- Rotas: `/` permanece a home pública; `/cadastro` e `/login` continuam disponibilizando a navegação correspondente.
- Autenticação: somente será considerada em comportamento de redirecionamento, sem alterar o fluxo Xano existente.
- Dependências: nenhum pacote novo; componentes nativos do Reflex e `rx.icon` serão utilizados.
