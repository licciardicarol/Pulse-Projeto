// Get Registro_Peso record
query "registro_peso/{registro_peso_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int registro_peso_id? filters=min:1
  }

  stack {
    db.get Registro_Peso {
      field_name = "id"
      field_value = $input.registro_peso_id
    } as $registro_peso
  
    precondition ($registro_peso != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $registro_peso
  guid = "cFEwE-w8LXtQZeTp6o9EFxEMzWA"
}