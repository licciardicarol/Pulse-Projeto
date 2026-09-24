# Spec: Cadastro do perfil (perfil-cadastro)

## ADDED Requirements

### Requirement: Cadastro inicial do perfil
O sistema DEVE permitir que o usuário preencha seus dados pessoais e de treino no primeiro acesso, usando os campos já definidos no schema da tabela `Perfil` do Xano.

#### Scenario: Usuário cadastra seu perfil
- **Given** um usuário novo acessa a tela de cadastro
- **When** ele preenche nome, data de nascimento, sexo, altura, modalidade, objetivo e meta semanal
- **Then** o sistema salva as informações no perfil associado ao usuário
- **Aceite testável**: a página exibe campos correspondentes aos atributos da tabela `Perfil` e confirma o envio com mensagem de sucesso

#### Scenario: Dados ausentes
- **Given** um usuário tenta salvar o perfil sem preencher campos obrigatórios
- **When** o formulário é enviado
- **Then** o sistema exibe uma mensagem de erro indicando o campo faltante
- **Aceite testável**: nome e data de nascimento devem ser obrigatórios e o formulário bloqueia o envio sem esses valores

#### Scenario: Sincronização com o Xano
- **Given** a variável `XANO_API_URL` está configurada
- **When** o usuário envia o formulário
- **Then** a requisição é enviada para a rota de perfis do Xano
- **Aceite testável**: os campos do payload seguem exatamente o schema `Perfil` e a resposta é tratada com sucesso ou erro

---

### Requirement: Dados do perfil
O sistema DEVE mapear corretamente os campos do schema do Xano no formulário.

#### Scenario: Campos vindos do Xano
- **Given** a tabela `Perfil` do Xano contém os campos listados no schema
- **When** o formulário é renderizado
- **Then** cada campo da tela corresponde a um campo do schema: `nome`, `data_de_nascimento`, `sexo`, `altura_cm`, `tipo_fisico`, `nivel_fisico`, `modalidade_fav`, `horario_fav_de_treino`, `meta_semanal`, `objetivo`, `medidas`
- **Aceite testável**: a interface inclui os campos de cadastro para todas as propriedades relevantes do perfil

## Relationships

- **Usuário 1:1 Perfil**
