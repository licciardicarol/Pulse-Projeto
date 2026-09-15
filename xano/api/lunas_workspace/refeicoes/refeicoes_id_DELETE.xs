// Delete Refeicoes record.
query "refeicoes/{refeicoes_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int refeicoes_id? filters=min:1
  }

  stack {
    db.del Refeicoes {
      field_name = "id"
      field_value = $input.refeicoes_id
    }
  }

  response = null
  guid = "YiYFZ0w5pcghIbMpWiD17fNyWlw"
}