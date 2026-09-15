// Get Treino record
query "treino/{treino_id}" verb=GET {
  api_group = "Luna's Workspace"

  input {
    int treino_id? filters=min:1
  }

  stack {
    db.get Treinos {
      field_name = "id"
      field_value = $input.treino_id
    } as $treino
  
    precondition ($treino != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $treino
  guid = "9naTcok6NDZ3wpxUuBr3agqyxEc"
}