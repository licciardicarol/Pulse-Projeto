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
    enum sexo? {
      values = ["Feminino", "Masculino", "Outro"]
    }
  
    decimal altura_cm?
    enum tipo_fisico? {
      values = ["Mesomorfo", "Ectomorfo", "Endomorfo"]
    }
  
    enum nivel_fisico? {
      values = [
        "Sedentário"
        "Iniciante"
        "Intermediário"
        "Avançado"
        "Atleta"
      ]
    }
  
    enum? horario_fav_de_treino? {
      values = ["Manhã", "Tarde", "Noite", "Madrugada"]
    }
  
    int meta_semanal?
    enum objetivo? {
      values = ["Perder gordura", "Ganhar massa", "Manter", "Performance"]
    }
  
    bool medidas?
    timestamp data_atualizacao?
    int user_id? {
      table = "user"
    }
  
    // controla o fluxo de onboarding; criado como false no signup
    bool onboarding_concluido?
  
    enum[] modalidade_fav1? {
      values = [
        "Musculação"
        "Corrida"
        "Ciclismo"
        "Funcional"
        "Crossfit"
        "Luta"
        "Yoga"
        "Natação"
        "Esportes coletivos"
      ]
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree|unique", field: [{name: "user_id", op: "asc"}]}
  ]

  guid = "G91Qbr-i1pVBslSIBEHnRH0pinI"
}