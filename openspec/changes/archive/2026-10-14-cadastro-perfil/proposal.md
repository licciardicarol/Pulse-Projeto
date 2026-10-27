## Why

O Pulse precisa de um cadastro inicial do perfil para registrar as informações pessoais e de treino do usuário antes que ele possa acompanhar treinos, sono, alimentação e evolução. Sem esse fluxo, o sistema não consegue associar os dados ao perfil correto nem ativar o onboarding do usuário.

## What Changes

- Criação de uma nova tela de cadastro do perfil no Reflex
- Mapeamento dos campos do banco Xano para o formulário de inscrição
- Validação básica do formulário antes do envio
- Envio dos dados para a API de perfis do Xano, com fallback seguro quando a URL do backend não estiver configurada
- Mensagens de sucesso e erro para orientar o usuário no preenchimento

## Capabilities

### New Capabilities
- `perfil-cadastro`: cadastro inicial do perfil do usuário com base no schema de `Perfil` do Xano

### Modified Capabilities
- Nenhuma

## Impact

- Código principal: `projetofacul/projetofacul.py`
- Dados: tabela `Perfil` do Xano (`nome`, `data_de_nascimento`, `sexo`, `altura_cm`, `tipo_fisico`, `nivel_fisico`, `modalidade_fav`, `horario_fav_de_treino`, `meta_semanal`, `objetivo`, `medidas`)
- Dependência: configuração de `XANO_API_URL` e opcionalmente `XANO_API_KEY` para sincronização com o backend
- Interface: nova página de onboarding/cadastro para o Pulse
