// Get Refeicoes record
query "refeicoes/{refeicoes_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int refeicoes_id? filters=min:1
  }

  stack {
    db.get Refeicoes {
      field_name = "id"
      field_value = $input.refeicoes_id
    } as $refeicoes
  
    precondition ($refeicoes != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $refeicoes
  guid = "ZcmQntiJh7vhKwd99r_kXbzD9jM"
}