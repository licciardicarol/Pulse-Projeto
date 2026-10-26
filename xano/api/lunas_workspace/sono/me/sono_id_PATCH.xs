// Edita um registro de sono, somente se ele pertencer ao usuário autenticado
// inputs explícitos: sem user_id e sem duracao_minutos (recalculada aqui)
query "sono/me/{sono_id}" verb=PATCH {
  api_group = "Luna's Workspace"
  auth = "user"

  input {
    int sono_id filters=min:1
    timestamp inicio_sono
    timestamp fim_sono
    int qualidade_sono filters=min:1|max:5
    text observacoes? filters=trim|max:500
  }

  stack {
    db.get Sono {
      field_name = "id"
      field_value = $input.sono_id
    } as $registro

    // registro inexistente ou de outro usuário: mesma resposta, sem revelar que existe
    precondition ($registro != null) {
      error_type = "notfound"
      error = "Not Found."
    }

    precondition ($registro.user_id == $auth.id) {
      error_type = "notfound"
      error = "Not Found."
    }

    precondition ($input.fim_sono > $input.inicio_sono) {
      error_type = "inputerror"
      error = "Invalid sleep period."
    }

    precondition ($input.fim_sono <= ("now"|to_timestamp)) {
      error_type = "inputerror"
      error = "Invalid sleep period."
    }

    var $duracao_minutos {
      value = (($input.fim_sono - $input.inicio_sono) / 60000)|floor
    }

    precondition ($duracao_minutos >= 15 && $duracao_minutos <= 1440) {
      error_type = "inputerror"
      error = "Invalid sleep duration."
    }

    // a checagem ignora o próprio registro
    db.query Sono {
      where = $db.Sono.user_id == $auth.id && $db.Sono.id != $input.sono_id && $db.Sono.inicio_sono < $input.fim_sono && $db.Sono.fim_sono > $input.inicio_sono
      return = {type: "count"}
    } as $conflitos

    precondition ($conflitos == 0) {
      error_type = "inputerror"
      error = "Overlapping sleep period."
    }

    db.patch Sono {
      field_name = "id"
      field_value = $input.sono_id
      data = {
        updated_at     : "now"
        inicio_sono    : $input.inicio_sono
        fim_sono       : $input.fim_sono
        duracao_minutos: $duracao_minutos
        qualidade_sono : $input.qualidade_sono
        observacoes    : $input.observacoes
      }
    } as $registro_atualizado
  }

  response = $registro_atualizado
}