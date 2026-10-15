## Context

A página pública é implementada como uma função Reflex localizada em `projetofacul/projetofacul.py`. Não existem estilos globais dedicados à landing page; os componentes utilizam estilos diretos e o tema padrão do Reflex/Radix Themes.

## Goals / Non-Goals

**Goals:**
- Criar uma identidade visual dark mode para a landing page com tokens reutilizáveis.
- Organizar o conteúdo em seções com hierarquia clara e responsividade mobile-first.
- Ajustar interações de navegação, FAQ, cards e estados de foco.

**Non-Goals:**
- Criar uma nova integração de autenticação ou alterar o Xano.
- Alterar State, lógica de negócio, servidor ou schema existente.
- Criar dashboard, relatórios ou sugestões de IA além da landing page.
- Implementar uma rede social, marketplace ou funcionalidades fora do escopo.

## Decisions

### 1. Tokens de design centralizados
Todos os valores de design serão definidos em `styles/theme.py`, incluindo cores, tipografia, espaçamentos, sombras, raios e estados hover. A função da landing page consumirá esses valores por meio de constantes ou helpers.

**Alternativas consideradas:**
- Repetir valores diretamente nos componentes — descartado para evitar inconsistência entre seções.
- Criar um tema global usando CSS externo — descartado para manter a implementação no ecossistema Reflex e evitar dependências adicionais.

### 2. Componentes nativos e ícones Lucide
A interface usará componentes nativos do Reflex, com `rx.icon` para os elementos visuais. Não serão adicionadas bibliotecas JavaScript ou CSS de terceiros.

**Alternativas consideradas:**
- Imagens externas — descartado para reduzir tamanho de carregamento e dependência visual.
- SVGs embutidos manualmente — descartado porque `rx.icon` oferece melhor consistência entre componentes.

### 3. Layout responsivo mobile-first
A página será construída com containers, grids e stacks responsivos, usando breakpoints em CSS próprio. As seções começarão com layout vertical e passarão gradualmente para displays de duas ou mais colunas.

**Alternativas consideradas:**
- Criar layouts separados para mobile e desktop — descartado porque aumenta duplicação de componentes.
- Dependência de classes Tailwind — descartado para manter mudanças locais e reduzir configuração.

### 4. Microinterações com CSS e JavaScript leve
Animações de entrada, hover e seleção serão implementadas com classes CSS e um script leve para detectar elementos no viewport. O modo de redução de movimento será respeitado com media queries.

**Alternativas consideradas:**
- Animações pesadas com bibliotecas externas — descartado por aumentar o bundle e depender de JavaScript adicional.
- Requerir estado do cliente para armazenar preferências de animação — descartado para evitar alterações no backend.

### 5. Autenticação sem alteração de fluxo
Links e botões com finalidade de cadastro e entrada usarão `rx.redirect` para as rotas existentes. Caso `/login` e `/cadastro` ainda não existam, serão adicionados placeholders sem lógica de autenticação.

**Alternativas consideradas:**
- Criar novas telas de autenticação neste redesign — descartado porque muda o escopo além da landing page.
- Alterar diretamente o fluxo Xano — descartado pela regra de não alterar integração existente.

## Risks / Trade-offs

- [Custo de manutenção do CSS próprio] → Tokens centralizados e componentes reutilizáveis reduzem duplicação.
- [Reprodução de estilos em diferentes navegadores] → A implementação deve usar propriedades compatíveis com os navegadores suportados pelo Reflex.
- [Acesso via teclado] → Foco visível, ordem semântica e aria-labels serão considerados no desenvolvimento.
- [Animações excessivas] → Redução de movimento será ativada por preferência do sistema e pelos limites de performance.
- [Conteúdo de IA] → A mensagem de orientação profissional deve ser clara e não apresentar resultados simulados.

## Migration Plan

Não é necessária migração de dados ou schema. A implementação será feita em etapas sobre a função atual da página inicial, mantendo o route `/` e os componentes existentes para o cadastro.

1. Criar o módulo de tema.
2. Atualizar a função da home pública para consumir os tokens.
3. Validar responsividade e comportamento com `reflex compile --dry`.
4. Testar as rotas por `reflex run` e validar HTTP 200 na home.
5. Revisar acessibilidade, microinterações e foco antes de encerrar a change.

## Open Questions

Nenhuma questão bloqueante. Os requisitos de design e comportamento estão suficientemente definidos para implementação.
