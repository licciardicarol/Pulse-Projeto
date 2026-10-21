// Retorna o Perfil do usuário autenticado (RLS: sempre por $auth.id)
query "perfil/me" verb=GET {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
  }

  stack {
    db.get Perfil {
      field_name = "user_id"
      field_value = $auth.id
    } as $perfil
  
    precondition ($perfil != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $perfil
  guid = "qz2ep4nXV8pDcGGUMJq-fIO46ZU"
}