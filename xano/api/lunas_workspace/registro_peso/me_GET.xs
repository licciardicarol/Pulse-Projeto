// Lista os registros de peso do usuário autenticado (RLS: sempre por $auth.id)
query "registro_peso/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    // a ordenação (mais recentes primeiro) é feita no app
    db.query registro_Peso {
      where = $db.registro_Peso.user_id == $auth.id
      return = {type: "list"}
    } as $registros
  }

  response = $registros
  guid = "3Dj990t2BxDoRDYq_QOhT1CX-L0"
}