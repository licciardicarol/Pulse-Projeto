// Delete Treino record.
query "treino/{treino_id}" verb=DELETE {
  api_group = "Luna's Workspace"

  input {
    int treino_id? filters=min:1
  }

  stack {
    db.del Treinos {
      field_name = "id"
      field_value = $input.treino_id
    }
  }

  response = null
  guid = "cNkxiusevWjOZG18zKWkpIQ8zJ8"
}