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
    decimal proteinas?
    decimal carboidratos?
    text descricao? filters=trim
    decimal gorduras?
    text analise_ia? filters=trim
    int user_id? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "_T33GlZGBWtkM_p7RkxtJ1QRVb4"
}