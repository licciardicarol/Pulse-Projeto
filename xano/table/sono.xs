table Sono {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }

    timestamp? inicio_sono?
    timestamp? fim_sono?
    // 1 Muito ruim · 2 Ruim · 3 Regular · 4 Bom · 5 Muito bom (rótulos ficam no app)
    int qualidade_sono? filters=min:1|max:5
    // calculado pelo servidor a partir de inicio_sono e fim_sono
    int duracao_minutos?
    text observacoes? filters=trim|max:500
    timestamp updated_at?=now
    int user_id? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "yFlO8KZ5jq5BLKGoqiLVbLYHGhQ"
}