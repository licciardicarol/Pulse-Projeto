table Refeicoes {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    date? data_refeicao?
    enum tipo? {
      values = [
        "Café da manhã"
        "Almoço"
        "Café da tarde"
        "Jantar"
      ]
    }
  
    decimal calorias?
    text proteinas? filters=trim
    text carboidratos? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "_T33GlZGBWtkM_p7RkxtJ1QRVb4"
}