// Lista os treinos do usuário autenticado (RLS: sempre por $auth.id)
query "treinos/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    // a ordenação (mais recentes primeiro) é feita no app
    db.query Treinos {
      where = $db.Treinos.user_id == $auth.id
      return = {type: "list"}
    } as $treinos
  }

  response = $treinos
  guid = "VqJVTnA196IREHQ-SGKyzsso-3g"
}