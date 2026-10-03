## 1. Autenticação no Xano

- [ ] 1.1 Confirmar e registrar os endpoints de signup/login, formato dos payloads e tabela autenticável no workspace Xano; verificar que o contrato exportado cobre sucesso e credenciais rejeitadas
- [ ] 1.2 Configurar a associação entre identidade autenticada e perfil, garantindo que cada usuário só acesse seus próprios dados; verificar com chamadas para dois usuários distintos

## 2. Integração de autenticação no backend

- [ ] 2.1 Implementar chamadas de signup/login no State do Reflex usando a configuração de ambiente validada; verificar sucesso, dados inválidos e indisponibilidade do Xano com testes
- [ ] 2.2 Manter token e estado autenticado somente no servidor, sem expor senha em feedback ou logs; verificar respostas renderizadas e caminhos de erro

## 3. Home e fluxos de conta no Reflex

- [ ] 3.1 Substituir a rota `/` por home pública responsiva com apresentação do Pulse e chamadas separadas para criar conta e entrar; verificar navegação em viewport estreito e largo
- [ ] 3.2 Criar páginas de cadastro de credenciais e login com validação e feedback de sucesso/erro; verificar encaminhamento após sucesso e erros sem revelar existência de e-mail
- [ ] 3.3 Adicionar FAQ cobrindo conta, perfil e registros, com ressalva de que o Pulse não substitui orientação profissional; verificar conteúdo visível e acessível

## 4. Proteção de rotas e perfil

- [ ] 4.1 Preservar `/cadastro` como onboarding após criar conta e exigir sessão válida nas rotas internas; verificar redirecionamento de sessão ausente ou inválida
- [ ] 4.2 Associar o perfil ao usuário autenticado sem quebrar validações existentes; verificar que o cadastro de perfil continua salvando para a identidade correta

## 5. Validação integrada

- [ ] 5.1 Adicionar testes para os cenários dos specs de home e acesso de usuário; verificar execução completa com `pytest`
- [ ] 5.2 Validar a compilação do app Reflex e o fluxo manual home → cadastro/login → perfil, sem erros de rota ou renderização
- [ ] 5.3 Executar `openspec validate --change home-publica` e resolver erros dos artefatos desta mudança