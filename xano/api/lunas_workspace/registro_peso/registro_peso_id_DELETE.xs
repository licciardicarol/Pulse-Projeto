// Delete Registro_Peso record.
query "registro_peso/{registro_peso_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int registro_peso_id? filters=min:1
  }

  stack {
    db.del Registro_Peso {
      field_name = "id"
      field_value = $input.registro_peso_id
    }
  }

  response = null
  guid = "KsGPhPMqnopuZ3vn7ztglUMBz44"
}