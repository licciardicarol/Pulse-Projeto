// Query all Registro_Peso records
query registro_peso verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Registro_Peso {
      return = {type: "list"}
    } as $registro_peso
  }

  response = $registro_peso
  guid = "Ptn022HecpWZJKgEKwpsFvA-G8M"
}