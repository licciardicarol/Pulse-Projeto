// Edit Registro_Peso record
query "registro_peso/{registro_peso_id}" verb=PATCH {
  api_group = "Luna's Workspace"

  input {
    int registro_peso_id? filters=min:1
    dblink {
      table = "Registro_Peso"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch Registro_Peso {
      field_name = "id"
      field_value = $input.registro_peso_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $registro_peso
  }

  response = $registro_peso
  guid = "jGG_sY7ymT98ZswBWTQGehyJbjE"
}