// Guarda uma recomendação do dia gerada por IA para o usuário autenticado.
// Só o servidor do Pulse chama: exige o token do dono E a chave de serviço (PULSE_ANALISE_SECRET).
// O dono sempre vem do token; os limites repetem a validação feita no app.
query "recomendacoes/me" verb=POST {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    date data_recomendacao
    text titulo filters=trim|min:1|max:80
    text texto filters=trim|min:1|max:400
    int recuperacao filters=min:0|max:100
    enum intensidade {
      values = ["Leve", "Moderado", "Intenso"]
    }
  
    text motivo_treino filters=trim|min:1|max:160
    text alimentacao filters=trim|min:1|max:200
    text modelo filters=trim|min:1|max:80
    text chave_servico {
      sensitive = true
    }
  }

  stack {
    // chave de serviço primeiro: sem ela nada é gravado
    precondition ($env.PULSE_ANALISE_SECRET != null && $env.PULSE_ANALISE_SECRET != "" && $input.chave_servico == $env.PULSE_ANALISE_SECRET) {
      error_type = "accessdenied"
      error = "Access denied."
    }
  
    db.add Recomendacoes {
      data = {
        created_at       : "now"
        user_id          : $auth.id
        data_recomendacao: $input.data_recomendacao
        titulo           : $input.titulo
        texto            : $input.texto
        recuperacao      : $input.recuperacao
        intensidade      : $input.intensidade
        motivo_treino    : $input.motivo_treino
        alimentacao      : $input.alimentacao
        modelo           : $input.modelo
      }
    } as $recomendacao
  }

  response = $recomendacao
  guid = "psVUca735AyNLdkq9hLceacSaoI"
}