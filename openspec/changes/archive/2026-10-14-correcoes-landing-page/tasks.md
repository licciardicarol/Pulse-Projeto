## 1. Centralização e hero

- [x] 1.1 Criar o helper reutilizável de container centralizado e aplicá-lo ao hero e às seções indicadas; verificar que o conteúdo fica centrado em 1920px sem alterar navbar/rodapé.
- [x] 1.2 Ajustar tipografia, espaçamentos e logo do hero; verificar os valores computados e a composição lado a lado da marca.

## 2. FAQ acessível

- [x] 2.1 Trocar Radix por controles nativos vinculados a um índice no Reflex State, preservando literalmente as cinco perguntas e respostas; verificar abrir, fechar e exclusividade de resposta.
- [x] 2.2 Estilizar estados transparentes, foco, seta, animação e reduced motion; verificar Tab/Enter/Espaço, ARIA e ausência de fundo azul.

## 3. Validação

- [x] 3.1 Executar pytest quando disponível e `reflex compile --dry`; pytest indisponível neste ambiente, testes de UI focados executados diretamente.
- [x] 3.2 Executar `reflex run` e verificar centralização, overflow horizontal, FAQ e logo em 360px, 768px, 1280px e 1920px.
- [x] 3.3 Rodar `openspec validate --changes correcoes-landing-page` e confirmar a validação da change.
