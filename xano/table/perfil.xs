// A tabela representa os dados de configuração e personalização do usuario
table Perfil {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // nome
    text nome? filters=trim
  
    // validar idade
    date? data_de_nascimento?
  
    // opcional
    text sexo? filters=trim
  
    decimal altura_cm?
    decimal tipo_fisico?
    text nivel_fisico? filters=trim
    enum modalidade_fav? {
      values = [
        "Musculação"
        "Cardio"
        "Funcional"
        "Luta"
        "CrossFit"
        "Yoga"
        "Esportes de areia"
        "Pilates"
      ]
    }
  
    int? horario_fav_de_treino?
    int meta_semanal?
    enum objetivo? {
      values = [
        "Hipertrofia (ganho de massa muscular)"
        "Emagrecimento (perda de gordura)"
        "Melhorar condicionamento físico"
        "Preservação de saúde mental"
      ]
    }
  
    bool medidas?
    timestamp data_atualizacao?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "G91Qbr-i1pVBslSIBEHnRH0pinI"
}