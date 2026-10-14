## 1. Rotas e preservação do onboarding

- [x] 1.1 Registrar uma única página de autenticação em `/login` e `/cadastro`, inicializando o modo pela rota e verificando as duas rotas em `tests/test_routes.py`.
- [x] 1.2 Mover a tela atual de perfil para `/onboarding` sem alterar `PerfilState` nem o POST `/profiles`; verificar que o formulário e o envio existentes continuam acessíveis.
- [x] 1.3 Conferir os links existentes da landing para `/login` e `/cadastro` e testar seus destinos.

## 2. Interface e comportamento dos formulários

- [x] 2.1 Criar o `AuthState` e a tela compartilhada, reutilizando `styles/theme.py`; verificar modo, URL, preservação do e-mail e limpeza de senhas/erros ao alternar.
- [x] 2.2 Implementar os campos dos modos Entrar e Criar conta, validação local e mensagens junto aos campos; verificar campos vazios, formato de e-mail, senha curta e confirmação divergente.
- [ ] 2.3 Implementar estados de envio, submissão por Enter e proteção contra duplo envio; verificar que a UI não afirma sucesso nem redireciona sem integração configurada.
- [x] 2.4 Construir apresentação, card, botão Google indisponível e navegação de retorno usando os tokens existentes; verificar textos, layout e ausência de dependências novas.

## 3. Acessibilidade, responsividade e microinterações

- [x] 3.1 Associar rótulos, autocomplete, semântica e navegação por teclado das abas, foco visível e `aria-live`; verificar os atributos no componente renderizado.
- [x] 3.2 Implementar estados de foco, indicador de aba e transições com suporte a `prefers-reduced-motion`; verificar foco, troca de modo e redução de movimento.
- [x] 3.3 Testar a página em 360px, 768px, 1280px e 1920px; verificar ausência de rolagem horizontal e controles com altura mínima de 44px.

## 4. Validação final e limite de integração

- [x] 4.1 Executar `reflex run` e validar visualmente os dois modos e as quatro larguras; registrar qualquer bloqueio de ambiente.
- [ ] 4.2 Executar `pytest` e confirmar que as verificações de rotas e do onboarding passam.
- [ ] 4.3 Manter login, cadastro real, Google OAuth, sessão e redirecionamento autenticado bloqueados até receber contratos Xano e destino pós-autenticação; então validar conta/perfil, login, credenciais inválidas e duplicidade em ambiente de teste sem alterar endpoints ou schema.