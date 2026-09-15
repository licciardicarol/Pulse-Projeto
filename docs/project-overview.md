# project-overview.md


## Nome do projeto: Pulse


## O que é o projeto?
O Pulse é um aplicativo web de acompanhamento fitness e bem-estar que centraliza informações da rotina do usuário em um único sistema. O usuário pode configurar seu perfil e objetivos, registrar seus treinos e exercícios, refeições, períodos de sono, peso e medidas corporais. A partir dos dados registrados, o sistema permite acompanhar a evolução do usuário e utilizar recursos de inteligência artificial para realizar análises e gerar sugestões relacionadas aos dados disponíveis. A proposta é facilitar a organização da rotina e permitir que o usuário visualize sua evolução de forma integrada.


## Objetivo / problema que resolve
O Pulse existe para centralizar informações que normalmente ficam espalhadas entre aplicativos, anotações ou registros diferentes. O sistema busca facilitar o acompanhamento da rotina fitness, permitindo que o usuário registre seus dados, acompanhe sua evolução e tenha uma visão integrada de treino, alimentação, sono, peso e medidas corporais. A inteligência artificial é utilizada como recurso de análise e apoio, ajudando a interpretar os dados registrados e apresentar sugestões e insights ao usuário.


## Público-alvo
Pessoas que praticam atividades físicas, principalmente aquelas que treinam por conta própria e desejam:
- Organizar seus objetivos;
- Registrar seus treinos e exercícios;
- Acompanhar sua alimentação;
- Registrar e acompanhar o sono;
- Acompanhar peso e medidas corporais;
- Visualizar sua evolução;
- Receber análises e sugestões baseadas nos próprios dados.


## Funcionalidades principais (MVP)

### Perfil e configuração
- Cadastro e configuração do perfil;
- Informações pessoais e características utilizadas pelo sistema;
- Definição de objetivo;
- Definição de meta semanal de treinos;
- Escolha de modalidades favoritas;
- Configuração de horário de treino e unidades;
- Controle de onboarding.

### Treinos
- Cadastro de treinos;
- Registro de categoria, duração e intensidade;
- Registro de anotações;
- Registro de calorias estimadas;
- Registro de exercícios dentro de cada treino;
- Registro de séries, repetições, carga e ordem dos exercícios;
- Análise/avaliação relacionada à IA.

### Alimentação
- Registro de refeições;
- Classificação do tipo de refeição;
- Descrição dos alimentos/refeição;
- Registro de calorias;
- Registro de proteínas, carboidratos e gorduras;
- Possibilidade de análise da refeição por IA.

### Sono
- Registro dos períodos de sono;
- Registro de início e fim do sono;
- Registro da duração;
- Avaliação da qualidade do sono em escala de Muito Ruim, Ruim, Regular, Bom e Muito Bom;
- Registro de observações;
- Permitir mais de um período de sono quando necessário, como sono principal e soneca.

### Peso e medidas
- Registro do peso;
- Registro da data e horário da medição;
- Registro de observações;
- Registro opcional de medidas corporais;
- Acompanhamento de cintura, quadril, peito, braço, coxa e panturrilha;
- Possibilidade de relacionar uma medição corporal a um registro de peso.

### Evolução e análise
- Visualização dos dados registrados;
- Acompanhamento da evolução ao longo do tempo;
- Utilização dos dados para gerar análises e indicadores;
- Sugestões e insights automáticos utilizando inteligência artificial.


## Fora de escopo (por enquanto)
Não implementar funcionalidades que não fazem parte do escopo definido sem solicitação explícita.
Não fazem parte do MVP atual:
- Integração com smartwatches, smartbands ou outros wearables;
- Integração automática com aplicativos externos de saúde ou fitness;
- Chat com médico, nutricionista ou personal trainer real;
- Atendimento profissional dentro do aplicativo;
- Prescrição médica;
- Prescrição nutricional;
- Diagnóstico de doenças ou condições de saúde;
- Rede social ou comunidade de usuários;
- Sistema de contratação ou venda de serviços;
- Marketplace;
- Funcionalidades financeiras;
- Funcionalidades que dependam de dados externos não definidos no projeto.


## Regras para o agente de IA do desenvolvimento
Ao trabalhar no Pulse:
1. Respeitar a arquitetura e as funcionalidades já existentes.
2. Não criar tabelas, campos, páginas, APIs ou funcionalidades sem necessidade ou sem solicitação.
3. Não substituir estruturas existentes por alternativas diferentes sem justificativa.
4. Preservar a segurança e o RLS das tabelas.
5. Considerar que cada usuário deve acessar somente seus próprios dados.
6. Diferenciar claramente funcionalidades existentes de funcionalidades planejadas.
7. Não considerar `user\\\_goals` uma tabela existente até sua implementação.
8. Não inventar dados para completar registros.
9. Não remover funcionalidades existentes para implementar novas.
10. Priorizar alterações pequenas e compatíveis com a arquitetura atual.
11. Antes de alterar o banco de dados, verificar as tabelas, campos e relacionamentos existentes.
12. Antes de criar uma nova funcionalidade, verificar se ela já pode ser atendida pela estrutura atual.
13. Manter o foco no objetivo principal do Pulse: acompanhamento integrado da rotina, registros e evolução do usuário.


## Inteligência Artificial
A inteligência artificial é parte mais importante da proposta do Pulse.
Atualmente, o banco possui informações relacionadas à análise de IA em:
- treinos;
- refeições.
A IA pode utilizar os dados registrados pelo usuário para gerar análises, sugestões e insights sobre sua rotina e evolução.
A IA deve trabalhar somente com informações disponíveis no sistema e não deve inventar registros, resultados, métricas ou informações pessoais.
A IA é um recurso de apoio e análise do aplicativo. Ela não deve ser tratada como substituta de médico, nutricionista, personal trainer ou outro profissional.


## Stack técnico
- Frontend/Backend: Reflex (Python)
- Backend externo / dados: Xano
- Especificação e workflow: OpenSpec
- Agente de IA: Claude Code
- Versionamento: GitHub
- Agente de IA (dev): Google Gemini
- Geração de sugestões: Google Gemini API (modelo Flash, tier gratuito) — decisão tomada, integração ainda não implementada


## Segurança e regras do banco
Todas as tabelas atuais possuem proteção por usuário (RLS).
A regra principal é:
> Cada usuário pode visualizar e editar somente os próprios dados.
Os registros que possuem `user\\\_id` devem sempre estar associados ao usuário autenticado.
O sistema possui também:
- criação automática do perfil após o cadastro do usuário;
- atualização automática de `updated\\\_at` no perfil;
- relacionamentos entre as entidades, principalmente entre treinos e exercícios;
- índices para facilitar consultas por usuário e data quando necessário.
Não remover ou alterar as regras de segurança sem necessidade.


## Funcionalidades planejadas / futuras
A principal expansão prevista para o banco é uma estrutura de metas do usuário, por exemplo uma tabela `user\_goals`.
Ela poderá armazenar:
- tipo de meta;
- valor desejado;
- unidade;
- período da meta;
- status.
As metas poderão estar relacionadas a objetivos como:
- peso;
- calorias;
- proteína;
- horas de sono;
- quantidade de treinos por semana.
Essa estrutura é planejada e NÃO deve ser considerada uma tabela existente no banco atual até que seja efetivamente implementada.
Outras possíveis expansões devem ser implementadas somente quando forem solicitadas.