# Spec: Sugestões (sugestoes)

## Modelo de dados proposto (SQL)

```sql
CREATE TABLE sugestao (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id    UUID NOT NULL REFERENCES perfil(id),
    conteudo      TEXT NOT NULL,
    periodo_inicio DATE NOT NULL,   -- início do período de dados analisado
    periodo_fim    DATE NOT NULL,   -- fim do período de dados analisado
    data_geracao  TIMESTAMP NOT NULL DEFAULT now(),
    modelo_usado  VARCHAR(50) NOT NULL   -- ex: 'gemini-flash'
);

-- RLS: usuário só pode ler/escrever sugestões do próprio profile_id
-- (mesma regra aplicada às demais tabelas do Pulse)
```

## ADDED Requirements

### Requirement: Geração de sugestão
O sistema DEVE permitir que um usuário solicite uma sugestão gerada por IA
com base em seus registros recentes de treino, sono e alimentação.

#### Scenario: Usuário solicita uma sugestão com dados suficientes
- **Given** um usuário autenticado com pelo menos um registro de Treino,
  Sono ou Refeição nos últimos 30 dias
- **When** ele clica em "gerar sugestão"
- **Then** o sistema busca os registros do período, envia para a API do
  Gemini e salva/exibe o texto da sugestão retornada
- **Aceite testável**: dado um Perfil com >=1 registro em qualquer uma das
  3 tabelas nos últimos 30 dias, uma chamada ao endpoint de geração retorna
  HTTP 200 e um registro novo em `sugestao` com `profile_id` correto

#### Scenario: Usuário sem dados suficientes
- **Given** um usuário sem nenhum registro salvo nos últimos 30 dias
- **When** ele solicita uma sugestão
- **Then** o sistema informa que não há dados suficientes e não chama a API do Gemini
- **Aceite testável**: nenhuma requisição HTTP é feita à API externa quando
  a contagem de registros do período é zero (verificável via mock/spy no teste)

#### Scenario: Falha na API do Gemini
- **Given** um usuário solicita uma sugestão
- **When** a API do Gemini não responde, retorna erro ou estoura o limite
  de requisições gratuito (rate limit)
- **Then** o sistema exibe uma mensagem de erro amigável e não trava a
  interface, e nenhum registro de `sugestao` incompleto é salvo
- **Aceite testável**: com a chamada à API mockada para lançar exceção, o
  teste confirma que nenhuma linha é inserida em `sugestao` e que o State
  retorna `is_loading = False` ao final

---

### Requirement: Persistência da sugestão
O sistema DEVE salvar toda sugestão gerada, associada ao Perfil do usuário,
para permitir histórico.

#### Scenario: Sugestão salva após geração
- **Given** uma sugestão foi gerada com sucesso
- **When** o sistema recebe a resposta da API do Gemini
- **Then** um registro de `sugestao` é criado com `conteudo`,
  `periodo_inicio`, `periodo_fim`, `data_geracao` e `profile_id`
- **Aceite testável**: o registro criado possui todos os campos
  obrigatórios não nulos e `profile_id` igual ao do usuário autenticado
  na requisição

---

### Requirement: Privacidade e integridade dos dados
O sistema DEVE garantir que dados de saúde/fitness usados na geração de
sugestões sigam as mesmas regras de privacidade e integridade das demais
tabelas do Pulse.

#### Scenario: Isolamento de dados entre usuários
- **Given** dois usuários distintos, cada um com seus próprios registros
- **When** o usuário A solicita uma sugestão
- **Then** apenas os dados do Perfil do usuário A são enviados à API
  externa, e a sugestão gerada só é visível/consultável pelo usuário A (RLS)
- **Aceite testável**: uma tentativa de consultar `sugestao` de
  `profile_id` diferente do usuário autenticado retorna vazio ou erro de
  permissão

#### Scenario: Nenhum dado inventado é enviado
- **Given** um usuário solicita uma sugestão
- **When** o prompt é montado a partir dos registros do banco
- **Then** o prompt contém exclusivamente dados existentes no banco —
  nenhum valor é estimado, arredondado de forma enganosa ou inventado
  para completar informação ausente
- **Aceite testável**: teste unitário compara os valores inseridos no
  prompt byte a byte com os valores retornados pela query no banco de teste

---

### Requirement: Aviso de responsabilidade
O sistema DEVE deixar explícito, na interface, que a sugestão é gerada por
IA e não substitui orientação profissional de saúde ou educação física.

#### Scenario: Exibição do aviso
- **Given** uma sugestão é exibida na tela
- **When** o usuário visualiza o conteúdo
- **Then** um aviso fixo é mostrado junto à sugestão informando que não é
  aconselhamento profissional
- **Aceite testável**: o componente de UI que renderiza a sugestão sempre
  renderiza também o elemento de aviso, verificável por teste de snapshot/DOM

## Relationships (delta)

- **Perfil 1:N Sugestao**