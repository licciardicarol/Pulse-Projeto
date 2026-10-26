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
    text nome? filters=trim
    int duracao_minutos?
    text categoria? filters=trim
    text intensidade? filters=trim
    text observacoes? filters=trim
    int user_id? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "bDlgvnQ_lrvYwY3q3Ow9kv3-zlI"
}