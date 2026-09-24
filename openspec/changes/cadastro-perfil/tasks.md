# Tasks: Cadastro do perfil

## Front-end (Reflex)

- [ ] 1.1 Criar a tela de cadastro do perfil com layout em cartão
- [ ] 1.2 Mapear todos os campos da tabela `Perfil` do Xano
- [ ] 1.3 Validar nome e data de nascimento como obrigatórios
- [ ] 1.4 Adicionar mensagens de erro e sucesso
- [ ] 1.5 Integrar os campos com o State do Reflex

## Backend / integração

- [ ] 2.1 Criar payload seguro para envio ao Xano
- [ ] 2.2 Enviar para `XANO_API_URL/profiles` quando configurado
- [ ] 2.3 Tratar falhas de conexão e ausência de configuração

## Validação

- [ ] 3.1 Verificar que a tela renderiza sem erros
- [ ] 3.2 Validar o código Python com compilação
- [ ] 3.3 Rodar `openspec validate --change cadastro-perfil`
