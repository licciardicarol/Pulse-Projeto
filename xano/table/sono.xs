table Sono {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    timestamp? inicio_sono?
    timestamp? fim_sono?
    enum qualidade_sono? {
      values = ["Muito ruim", "Ruim", "Regular", "Bom", "Muito bom"]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "yFlO8KZ5jq5BLKGoqiLVbLYHGhQ"
}