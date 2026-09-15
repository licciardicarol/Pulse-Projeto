// Add Refeicoes record
query refeicoes verb=POST {
  api_group = "Luna's Workspace"

  input {
    dblink {
      table = "Refeicoes"
    }
  }

  stack {
    db.add Refeicoes {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $refeicoes
  }

  response = $refeicoes
  guid = "RU8Fo8iL3OYe5l23ON7ZPE87ed4"
}