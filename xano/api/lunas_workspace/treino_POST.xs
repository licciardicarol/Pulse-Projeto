// Add Treino record
query treino verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Treinos"
    }
  }

  stack {
    db.add Treinos {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $treino
  }

  response = $treino
  guid = "r0Rsa50nkvWlRpUzS5KAuvELxRI"
}