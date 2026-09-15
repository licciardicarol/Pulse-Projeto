<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** � up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above � do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs � components, state management, events, styling, database, routing, authentication � use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available � always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

## Sobre este projeto

Aplicação web de acompanhamento fitness (academia/treinos), construída com Reflex. O usuário registra:
- Objetivos (ex: emagrecimento, hipertrofia, resistência)
- Treinos realizados (exercícios, séries, cargas, duração)
- Refeições (o que comeu, horários e proteínas)
- Sono (duração e qualidade)
- Perfil (nome, idade, modalidade favorita e meta semana)
- Registro de peso (peso e horário registrado)

A partir desses dados, o sistema mostra a evolução do usuário ao longo do tempo e pode gerar sugestões (ex: ajustes de treino, alertas de sono insuficiente, etc.).

Para contexto detalhado de domínio, ver `domain-model.md` e `project-overview.md`. E todos esses registros estão disponíveis nas tabelas do Xano.

## Convenções de código

- Seguir os padrões de state management do Reflex (não usar variáveis globais soltas fora de `rx.State`)
- Nomes de arquivos e componentes em snake_case (padrão Python)
- Um `State` por área funcional (ex: `TreinosState`, `RefeiçõesState`, `SonoState`, `PerfilState`) em vez de um State gigante único
- Funções de lógica de negócio (cálculos de evolução, geração de sugestões) devem ficar separadas dos componentes de UI, em módulos próprios (ex: `logic/` ou `services/`)

(ajustem esse esqueleto para o que já foi criado pelo `reflex init`)

## Como trabalhar com o OpenSpec
- Toda funcionalidade nova (ex: "adicionar registro de sono", "tela de sugestões") deve começar com uma proposta em `openspec/changes/` antes de qualquer código
- Specs seguem o formato delta (ADDED/MODIFIED/REMOVED)
- Não editar `openspec/specs/` direto — só via arquivamento de uma change aprovada
- Rodar `openspec validate` antes de dar como concluída uma proposta

## O que o agente NÃO deve fazer
- Não commitar direto na branch `main` — sempre criar uma branch por feature e abrir PR
- Não instalar bibliotecas novas sem justificar no PR
- Não implementar lógica de "sugestões" com dados sensíveis de saúde sem deixar claro que não é aconselhamento médico
- Todo e qualquer código grande deixar opção de ser aceitou ou não

## Testes
- Framework: pytest
- Toda função de lógica de negócio (cálculo de evolução, geração de sugestões, validações) deve ter teste unitário correspondente
- Antes de finalizar qualquer proposta do OpenSpec, rodar `pytest` e garantir que os testes passam
- Testar todas as rotas e caminhos que o usuário pode fazer para que fique completamente ligadas as páginas

## Chaves de API / segredos
- Nunca commitar chaves de API no repositório
- A chave da API do Google Gemini fica em variável de ambiente (.env, fora do Git)
- Chamadas à API de LLM só podem ser feitas a partir do backend (States do
  Reflex), nunca do lado do cliente
- Integração com o Gemini ainda não foi implementada — ver capability `sugestoes`

## Sugestões geradas por IA
- Seguir a capability `sugestoes` definida no OpenSpec
- Toda sugestão gerada deve deixar claro na UI que é conteúdo gerado por IA
  e não substitui orientação profissional