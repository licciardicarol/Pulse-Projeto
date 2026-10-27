table registro_Peso {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // Peso da pessoa
    decimal peso?
  
    // data e horario que foi feito o peso
    timestamp? data_horario?
  
    int user_id? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "k4U1uY6_iRQxdsnxOnrjkgLcfng"
}