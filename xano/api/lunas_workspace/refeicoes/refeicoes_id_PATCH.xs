// Edit Refeicoes record
query "refeicoes/{refeicoes_id}" verb=PATCH {
  api_group = "Luna's Workspace"

  input {
    int refeicoes_id? filters=min:1
    dblink {
      table = "Refeicoes"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Refeicoes {
      field_name = "id"
      field_value = $input.refeicoes_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $refeicoes
  }

  response = $refeicoes
  guid = "K-bp4RcpAXehxh3X7LQado98F2U"
}