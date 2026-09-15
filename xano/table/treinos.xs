table Treinos {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    enum tipo? {
      values = ["Superior", "Inferior", "Full body (corpo todo)"]
    }
  
    timestamp inicio?
    timestamp fim?
    decimal carga?
    int repeticoes?
    date? data?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "bDlgvnQ_lrvYwY3q3Ow9kv3-zlI"
}