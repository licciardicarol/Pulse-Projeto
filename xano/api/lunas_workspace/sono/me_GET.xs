// Lista os registros de sono do usuário autenticado (RLS: sempre por $auth.id)
query "sono/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    // a ordenação (mais recentes primeiro) é feita no app
    db.query Sono {
      where = $db.Sono.user_id == $auth.id
      return = {type: "list"}
    } as $registros
  }

  response = $registros
}