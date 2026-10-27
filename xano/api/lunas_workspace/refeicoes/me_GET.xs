// Lista as refeições do usuário autenticado (RLS: sempre por $auth.id)
query "refeicoes/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    // a ordenação (mais recentes primeiro) é feita no app
    db.query Refeicoes {
      where = $db.Refeicoes.user_id == $auth.id
      return = {type: "list"}
    } as $refeicoes
  }

  response = $refeicoes
  guid = "e94noCmttARIcBZEigjXNYPXaGc"
}