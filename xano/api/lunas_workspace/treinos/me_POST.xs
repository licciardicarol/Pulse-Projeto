// Registra um treino do usuário autenticado (RLS: dono sempre vem do token)
// inputs explícitos: sem user_id e sem os campos legados (tipo, inicio, fim, carga, repeticoes)
query "treinos/me" verb=POST {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    date data
    int duracao_minutos filters=min:1|max:1440
    text nome filters=trim|min:2|max:60
    text categoria? filters=trim|max:40
    text intensidade? filters=trim|max:20
    text observacoes? filters=trim|max:500
  }

  stack {
    // a data do treino não pode ser posterior a hoje em São Paulo (compara só o dia)
    var $hoje_sp {
      value = "now"
        |format_timestamp:"Y-m-d":"America/Sao_Paulo"
    }
  
    precondition (($input.data|to_timestamp) <= ($hoje_sp|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid workout date."
    }
  
    db.add Treinos {
      data = {
        created_at     : "now"
        user_id        : $auth.id
        data           : $input.data
        duracao_minutos: $input.duracao_minutos
        nome           : $input.nome
        categoria      : $input.categoria
        intensidade    : $input.intensidade
        observacoes    : $input.observacoes
      }
    } as $treino
  }

  response = $treino
  guid = "HzBcSH9nzS4GhJQbyPnkvMYMRuQ"
}