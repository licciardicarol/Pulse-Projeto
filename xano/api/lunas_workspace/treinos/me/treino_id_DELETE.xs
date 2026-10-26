// Exclui um treino, somente se ele pertencer ao usuário autenticado
query "treinos/me/{treino_id}" verb=DELETE {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int treino_id filters=min:1
  }

  stack {
    db.get Treinos {
      field_name = "id"
      field_value = $input.treino_id
    } as $treino
  
    // treino inexistente ou de outro usuário: mesma resposta, sem revelar que existe
    precondition ($treino != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    precondition ($treino.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    db.del Treinos {
      field_name = "id"
      field_value = $input.treino_id
    }
  }

  response = {sucesso: true}
  guid = "7xkqQJ9jHU7UKQI-IhwPXd_lPd0"
}