## Why

Hoje a rota inicial do Pulse abre diretamente o formulário de perfil, sem apresentar o produto nem oferecer uma entrada clara para clientes que já têm conta. Uma home pública com informações e acesso a cadastro/login torna o primeiro contato compreensível e permite que usuários novos e existentes iniciem o fluxo adequado.

## What Changes

- Substituir a tela de perfil na rota `/` por uma home pública responsiva com informações sobre o Pulse e suas áreas de acompanhamento.
- Incluir chamadas para criar conta e entrar, com rotas distintas e fluxos reais integrados à autenticação do Xano.
- Preservar o cadastro de perfil como etapa posterior à criação de conta, sem tratá-lo como cadastro de credenciais.
- Adicionar uma seção de perguntas frequentes sobre funcionamento, dados e uso do aplicativo; informações de saúde devem deixar claro que o Pulse não substitui orientação profissional.
- Configurar ou implementar no backend Xano o suporte de autenticação necessário, pois os endpoints versionados atualmente não expõem login e a tabela `Obj_user` declara `auth = false`.

## Capabilities

### New Capabilities
- `home-publica`: página pública inicial com informações do Pulse, FAQ e encaminhamento para cadastro e login.
- `acesso-usuario`: criação de conta e autenticação de usuários com sessão válida via Xano.

### Modified Capabilities
- Nenhuma

## Impact

- Interface e rotas Reflex em `projetofacul/projetofacul.py`.
- Novos fluxos de cadastro de conta e login; o cadastro de perfil existente deverá continuar acessível depois da criação de conta.
- Integração e configuração de autenticação no Xano, incluindo a entidade de usuário hoje definida sem autenticação e endpoints ainda não disponíveis neste repositório.
- Conteúdo estático da home e FAQ, sem dependência externa nova.