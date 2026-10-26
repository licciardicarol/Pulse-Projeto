// Registra um período de sono do usuário autenticado (RLS: dono sempre vem do token)
// inputs explícitos: sem user_id e sem duracao_minutos (calculada aqui)
query "sono/me" verb=POST {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    timestamp inicio_sono
    timestamp fim_sono
    int qualidade_sono filters=min:1|max:5
    text observacoes? filters=trim|max:500
  }

  stack {
    precondition ($input.fim_sono > $input.inicio_sono) {
      error_type = "inputerror"
      error = "Invalid sleep period."
    }

    // o fim do sono não pode estar no futuro
    precondition ($input.fim_sono <= ("now"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid sleep period."
    }

    var $duracao_minutos {
      value = (($input.fim_sono - $input.inicio_sono) / 60000)|floor
    }

    // de 15 minutos a 24 horas
    precondition ($duracao_minutos >= 15 && $duracao_minutos <= 1440) {
      error_type = "inputerror"
      error = "Invalid sleep duration."
    }

    // sem sobreposição com outro registro do mesmo usuário (encostados são permitidos)
    db.query Sono {
      where = $db.Sono.user_id == $auth.id && $db.Sono.inicio_sono < $input.fim_sono && $db.Sono.fim_sono > $input.inicio_sono
      return = {type: "count"}
    } as $conflitos

    precondition ($conflitos == 0) {
      error_type = "inputerror"
      error = "Overlapping sleep period."
    }

    db.add Sono {
      data = {
        created_at     : "now"
        updated_at     : "now"
        user_id        : $auth.id
        inicio_sono    : $input.inicio_sono
        fim_sono       : $input.fim_sono
        duracao_minutos: $duracao_minutos
        qualidade_sono : $input.qualidade_sono
        observacoes    : $input.observacoes
      }
    } as $registro
  }

  response = $registro
}