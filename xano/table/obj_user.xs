table Obj_user {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // Usuario vai colocar qual e o objetivo do treino dele
    enum Objetivo_treino? {
      values = ["Força", "Perda de peso", "Ganho de massa magra", ""]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "taRuWlxNGVfd757ZCPRED00DSGY"
}