// Recomendação de treino do dia gerada por IA (uma linha por geração = histórico).
// A "recomendação de hoje" é a mais recente do usuário com data_recomendacao = dia atual.
// created_at sem visibilidade privada: o app mostra "Gerada às HH:MM" a partir dele.
table Recomendacoes {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    int user_id? {
      table = "user"
    }
  
    // dia local do usuário a que a recomendação se refere
    date? data_recomendacao?
  
    text titulo? filters=trim|max:80
    text texto? filters=trim|max:400
    int recuperacao? filters=min:0|max:100
    enum intensidade? {
      values = ["Leve", "Moderado", "Intenso"]
    }
  
    text motivo_treino? filters=trim|max:160
    text alimentacao? filters=trim|max:200
  
    // modelo de IA usado, ex.: gemini-3.5-flash-lite
    text modelo? filters=trim|max:80
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
    {
      type : "btree"
      field: [{name: "data_recomendacao", op: "desc"}]
    }
  ]

  guid = "lOwXMwOazz2vj3DE7YcVGqIP3MM"
}