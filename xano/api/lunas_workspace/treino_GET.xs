// Query all Treino records
query treino verb=GET {
  api_group = "Luna's Workspace"

  input {
  }

  stack {
    db.query Treinos {
      return = {type: "list"}
    } as $treino
  }

  response = $treino
  guid = "wNAq3zZ2eQjnVzichiBEoCBvFx4"
}