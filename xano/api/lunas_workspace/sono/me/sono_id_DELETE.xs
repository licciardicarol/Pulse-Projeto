// Exclui um registro de sono, somente se ele pertencer ao usuário autenticado
query "sono/me/{sono_id}" verb=DELETE {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int sono_id filters=min:1
  }

  stack {
    db.get Sono {
      field_name = "id"
      field_value = $input.sono_id
    } as $registro

    // registro inexistente ou de outro usuário: mesma resposta, sem revelar que existe
    precondition ($registro != null) {
      error_type = "notfound"
      error = "Not Found."
    }

    precondition ($registro.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }

    db.del Sono {
      field_name = "id"
      field_value = $input.sono_id
    }
  }

  response = {sucesso: true}
}