// Exclui uma refeição, somente se ela pertencer ao usuário autenticado
query "refeicoes/me/{refeicao_id}" verb=DELETE {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int refeicao_id filters=min:1
  }

  stack {
    db.get Refeicoes {
      field_name = "id"
      field_value = $input.refeicao_id
    } as $refeicao
  
    // refeição inexistente ou de outro usuário: mesma resposta, sem revelar que existe
    precondition ($refeicao != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    precondition ($refeicao.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }
  
    db.del Refeicoes {
      field_name = "id"
      field_value = $input.refeicao_id
    }
  }

  response = {sucesso: true}
  guid = "RwXpRiWgOJvyUyivdB4_9uGiZ6U"
}