// Exclui um registro de peso, somente se ele pertencer ao usuário autenticado
query "registro_peso/me/{registro_peso_id}" verb=DELETE {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int registro_peso_id filters=min:1
  }

  stack {
    db.get registro_Peso {
      field_name = "id"
      field_value = $input.registro_peso_id
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
  
    db.del registro_Peso {
      field_name = "id"
      field_value = $input.registro_peso_id
    }
  }

  response = {sucesso: true}
  guid = "hQK8KZVAoHv00O3UkfbpzN8_H6w"
}