table Registro_Peso {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // Peso da pessoa
    decimal Peso?
  
    // data e horario que foi feito o peso
    timestamp? Data_Horario?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "k4U1uY6_iRQxdsnxOnrjkgLcfng"
}