// Add Registro_Peso record
query registro_peso verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Registro_Peso"
    }
  }

  stack {
    db.add Registro_Peso {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $registro_peso
  }

  response = $registro_peso
  guid = "uwkDkD9bcZrQkLnIZIR2nTwl_bA"
}