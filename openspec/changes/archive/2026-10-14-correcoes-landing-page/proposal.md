## Why

A landing page aparece desalinhada em telas largas porque seus containers de conteúdo ficam ancorados à esquerda. O FAQ também não oferece um controle de pergunta funcional e acessível, deixando as respostas ocultas.

## What Changes

- Centralizar explicitamente os containers do hero e das seções sem alterar o alinhamento do cabeçalho e do rodapé.
- Ajustar espaçamentos e tipografia do hero e manter a marca Pulse em uma linha.
- Substituir o FAQ atual por disclosures acessíveis, sem fundo de destaque, com somente uma resposta aberta por vez.
- Verificar o layout em 360px, 768px, 1280px e 1920px, incluindo ausência de rolagem horizontal.

## Capabilities

### New Capabilities
- `landing-page-ui`: apresentação responsiva, centralização e interação acessível do FAQ público.

### Modified Capabilities
- Nenhuma.

## Impact

- Componentes e CSS da landing page, state Reflex limitado à interação do FAQ e testes de UI existentes.
- Não altera regras de negócio, rotas, Xano, schema ou dependências.
